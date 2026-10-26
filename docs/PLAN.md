# Plan: LLM test automation framework

A Python + Pytest framework for testing AI/LLM applications: plain prompts and a RAG (retrieval-augmented)
assistant. Built step by step so every layer is explained; every test documents its steps and logs **expected vs
actual**, and a Requirements Traceability Matrix (RTM) links each requirement to its tests and their latest result.

## What is being tested (system under test)

The framework ships with a small, self-contained **demo AI app** so it runs out of the box:

1. **Prompt features**: a "policy summariser" and a "ticket classifier" that return structured JSON, calling Gemini
   directly. Used for prompt testing: instructions, output format, refusals, consistency.
2. **RAG assistant**: answers questions about a fictional company ("Orbit Labs") from a small set of markdown
   documents, using embeddings + ChromaDB retrieval + Gemini. Used for RAG testing: retrieval, groundedness,
   hallucination, out-of-scope refusal, citations.

The framework talks to the app through an **adapter** interface, so it can later be pointed at another AI app
(e.g. an HTTP endpoint) without changing the tests.

## Framework architecture

```
config/            settings per environment (model names, thresholds, record/replay mode)
framework/
  clients/         LLM client wrapper: retries, timing, token usage, record/replay "cassettes"
  adapters/        how tests call the system under test (in-process now; HTTP later)
  assertions/      reusable checks: contains_fact, json_schema, refusal, semantic_similarity, grounded (judge) ...
  evaluators/      LLM-as-judge (Gemini) with rubric prompts and scores
  steps.py         step(), expect() helpers: log every step with expected vs actual into the report
  rtm.py           builds docs/RTM.md from requirement markers + test results
sut/               the demo AI app (prompt features + RAG) and its knowledge base
tests/
  data/            data-driven test cases (YAML): golden Q&A, injection payloads, paraphrases
  prompt/  rag/  safety/  robustness/  performance/
docs/              PLAN.md, REQUIREMENTS.md, RTM.md (generated), TEST_STRATEGY.md
```

## How a test reads (target style)

```python
@pytest.mark.req("REQ-RAG-003")
def test_out_of_scope_question_is_refused(rag):
    """TC-RAG-007: the assistant refuses questions its documents don't answer.
    Steps: 1) ask an out-of-scope question  2) check the answer is the refusal  3) check no sources are cited
    Expected: refusal message, empty sources, no invented facts."""
    with step("Ask a question the documents don't cover"):
        result = rag.ask("What is the CEO's favourite colour?")
    expect("answer is the refusal message", expected=REFUSAL, actual=result.answer)
    expect("no sources are cited", expected=[], actual=result.sources)
```

Every `step`/`expect` line appears in the HTML report with PASS/FAIL, expected and actual values.

## Phases (one at a time, explained, then wait for "next")

| # | Phase | What you'll learn |
|---|---|---|
| 0 | Repo, plan, requirements | How an AI test effort is scoped; writing testable requirements for non-deterministic systems |
| 1 | Demo AI app (prompt features + RAG) | What you're testing and where it can fail |
| 2 | Framework core: client, record/replay, step logging, report | Making LLM tests repeatable and cheap; expected vs actual reporting |
| 3 | Prompt tests | Instruction following, JSON schema, refusals, temperature/determinism |
| 4 | RAG tests | Retrieval (hit@k, MRR), groundedness, citations, out-of-scope |
| 5 | LLM-as-judge | Faithfulness, relevancy, hallucination scores; thresholds; judge weaknesses |
| 6 | Safety and robustness | Prompt injection, jailbreaks, PII/system-prompt leakage, paraphrase consistency |
| 7 | Performance and cost | Latency budgets, token usage and cost per test |
| 8 | RTM, CI, reports | Auto-generated RTM; GitHub Actions (replay on every push, live on demand) |
| 9 | README, interview notes, portfolio + CV | Presenting it |

## Key decisions

- **Python 3.13 locally, CI on 3.11+**; Pytest; `google-genai` for Gemini; ChromaDB; DeepEval only where it adds
  value over our own judge (decided in phase 5, with reasons).
- **Record/replay:** live mode calls Gemini and records responses; replay mode re-uses them, so CI is free,
  fast and deterministic. Live runs are triggered on demand.
- **Gemini key** reused from the owner's existing projects, kept in `.env` (never committed).
