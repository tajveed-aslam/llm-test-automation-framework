"""Builds the search index (the "R" in RAG).

    documents -> chunks (one per "## " section) -> embeddings -> ChromaDB

Every chunk keeps metadata: which file it came from, its section, and the document's status (current or archived).
Run once, and again whenever the documents change:   python -m sut.ingest
"""

import re

import chromadb

from sut import config, llm


def read_front_matter(markdown: str) -> tuple[dict, str]:
    """Split the '--- key: value ---' header from the document body."""
    match = re.match(r"^---\n(.*?)\n---\n", markdown, re.DOTALL)
    if not match:
        return {}, markdown
    meta = dict(line.split(":", 1) for line in match.group(1).splitlines() if ":" in line)
    return {k.strip(): v.strip() for k, v in meta.items()}, markdown[match.end():]


def chunk_document(source: str, markdown: str) -> list[dict]:
    """One chunk per section. The document title is kept on every chunk so it still makes sense on its own."""
    meta, body = read_front_matter(markdown)
    title = re.search(r"^# (.+)$", body, re.MULTILINE).group(1).strip()
    chunks = []
    for i, section in enumerate(re.split(r"^## ", body, flags=re.MULTILINE)[1:], start=1):
        heading, _, text = section.partition("\n")
        chunks.append({
            "id": f"{source}#{i}",
            "text": f"{title} > {heading.strip()}\n\n{text.strip()}",
            "source": source,
            "section": heading.strip(),
            "status": meta.get("status", "current"),
        })
    return chunks


def load_all_chunks() -> list[dict]:
    """All documents, including archived ones. Whether archived chunks are SEARCHED is decided at query time."""
    chunks = []
    for path in sorted(config.KNOWLEDGE_BASE_DIR.rglob("*.md")):
        source = path.relative_to(config.KNOWLEDGE_BASE_DIR).as_posix()
        chunks.extend(chunk_document(source, path.read_text(encoding="utf-8")))
    return chunks


def collection() -> chromadb.Collection:
    store = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    # We pass our own Gemini embeddings, so Chroma's built-in embedding model is not used.
    return store.get_or_create_collection(config.COLLECTION, embedding_function=None, metadata={"hnsw:space": "cosine"})


def build_index() -> int:
    chunks = load_all_chunks()
    vectors = llm.embed([c["text"] for c in chunks], task_type="RETRIEVAL_DOCUMENT")
    col = collection()
    if col.count():
        col.delete(ids=col.get()["ids"])
    col.add(
        ids=[c["id"] for c in chunks],
        embeddings=vectors,
        documents=[c["text"] for c in chunks],
        metadatas=[{k: c[k] for k in ("source", "section", "status")} for c in chunks],
    )
    return len(chunks)


if __name__ == "__main__":
    print(f"Indexed {build_index()} chunks into {config.CHROMA_DIR.name}/")
