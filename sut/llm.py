"""The only file that talks to Gemini. Two jobs: embed text (for search) and generate text (answers).

Free-tier keys are rate limited, so both calls retry on HTTP 429 (too many requests) and 5xx (server busy).
"""

import time

from google import genai
from google.genai import errors, types

from sut import config

_client: genai.Client | None = None


def client() -> genai.Client:
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is missing: copy .env.example to .env and add your key.")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _retry(call, attempts: int = 5):
    for attempt in range(attempts):
        try:
            return call()
        except errors.APIError as e:
            if not (e.code == 429 or (e.code or 0) >= 500) or attempt == attempts - 1:
                raise
            time.sleep(2 ** (attempt + 1))  # wait 2s, 4s, 8s, 16s


def embed(texts: list[str], task_type: str) -> list[list[float]]:
    """Text -> embeddings (lists of numbers that capture meaning).
    task_type: RETRIEVAL_DOCUMENT for document chunks, RETRIEVAL_QUERY for questions."""
    result = _retry(
        lambda: client().models.embed_content(
            model=config.EMBEDDING_MODEL, contents=texts, config=types.EmbedContentConfig(task_type=task_type)
        )
    )
    return [e.values for e in result.embeddings]


def generate(system_prompt: str, user_prompt: str, temperature: float, json_output: bool = False) -> str:
    """Send a prompt to the LLM and return its text.
    temperature: 0 = as repeatable as possible, 1 = more varied.  json_output: ask Gemini for JSON only."""
    settings = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
        response_mime_type="application/json" if json_output else None,
    )
    result = _retry(lambda: client().models.generate_content(model=config.ANSWER_MODEL, contents=user_prompt, config=settings))
    return (result.text or "").strip()
