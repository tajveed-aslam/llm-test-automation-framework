"""Seeded bugs: deliberate defects planted in the demo app so you can practise finding them.

Each bug is a realistic mistake teams really make when building AI apps. Every place in the app code that behaves
differently because of a bug is marked with `if bug("B1"):` so you can read the broken path next to the correct one.

Choose which bugs are active with the SUT_BUGS environment variable:
    SUT_BUGS=all        every bug on: the "v1 release candidate" before testing   (default)
    SUT_BUGS=none       every bug fixed
    SUT_BUGS=B1,B4      only those bugs on

The full catalogue, with the symptom and the test that catches each one, is in docs/SEEDED_BUGS.md.
"""

import os

CATALOGUE = {
    "B1": "Open-book prompt: the model may use general knowledge -> invents answers (hallucination)",
    "B2": "Top-k = 1: only one chunk retrieved -> multi-part answers miss facts and the gaps get guessed",
    "B3": "Archived documents are searched -> outdated, contradictory facts (stale-data hallucination)",
    "B4": "Citations written by the model -> fake source names, and sources listed even when it refuses",
    "B5": "Temperature 1.0 -> the same question gets different answers",
    "B6": "Document text is not fenced off -> instructions planted in a document are obeyed (prompt injection)",
    "B7": "No non-disclosure rule -> the system prompt can be extracted",
    "B8": "Loose classifier prompt -> labels outside the allowed set, and invalid JSON",
}


def active_bugs() -> set[str]:
    raw = os.getenv("SUT_BUGS", "all").strip().lower()
    if raw in ("", "none"):
        return set()
    if raw == "all":
        return set(CATALOGUE)
    return {b.strip().upper() for b in raw.split(",") if b.strip()}


def bug(bug_id: str) -> bool:
    """True if this seeded bug is switched on. Read fresh each call, so tests can switch bugs per test."""
    return bug_id in active_bugs()
