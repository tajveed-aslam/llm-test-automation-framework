"""Settings for the demo app (the system under test). Each can be overridden by an environment variable."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ANSWER_MODEL = os.getenv("ANSWER_MODEL", "gemini-flash-lite-latest")  # the LLM that writes answers
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")  # turns text into vectors

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent / "knowledge_base"
CHROMA_DIR = ROOT / "chroma_db"
COLLECTION = "orbit_labs"

TOP_K = 4  # chunks retrieved per question (bug B2 changes this to 1)
REFUSAL = "I don't know based on the Orbit Labs documents."
