"""Two prompt-only features (no retrieval): the LLM transforms text you give it.

    summarise(text)        -> a short summary that must keep every number exact
    classify_ticket(text)  -> JSON: {"category", "priority", "summary"} using a fixed set of labels

These are the "prompt testing" targets: does the model follow instructions, keep the format, and not add facts?
"""

import json

from sut import llm
from sut.bugs import bug

CATEGORIES = ["hardware", "software", "access", "network", "security", "other"]
PRIORITIES = ["P1", "P2", "P3"]


def summarise(text: str, max_words: int = 50) -> str:
    system = (
        f"Summarise the text in at most {max_words} words. Keep every number, date, amount and limit exactly as "
        "written. Do not add information that is not in the text."
    )
    return llm.generate(system, text, temperature=0.0)


def classify_ticket(ticket: str) -> dict:
    """Returns {"raw": the model's exact text, "parsed": the JSON as a dict, or None if it isn't valid JSON}."""
    if bug("B8"):
        # BUG B8: no list of allowed labels, no priority rules, no JSON mode. The model invents its own labels
        # ("Hardware Issue", "High") and may wrap the JSON in ``` fences, so the output breaks downstream code.
        system = "Classify this IT support ticket and give it a priority. Reply in JSON."
        raw = llm.generate(system, ticket, temperature=0.0)
    else:
        system = (
            "Classify the IT support ticket. Reply with JSON only, exactly these keys:\n"
            f'  "category": one of {CATEGORIES}\n'
            f'  "priority": one of {PRIORITIES}. P1 = critical outage or security incident; P2 = one person cannot '
            "work at all; P3 = requests and minor faults\n"
            '  "summary": the problem in at most 12 words'
        )
        raw = llm.generate(system, ticket, temperature=0.0, json_output=True)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = None
    return {"raw": raw, "parsed": parsed}
