# Requirements: Orbit Labs AI assistant

What "correct" means for the system under test. Every requirement is written so it can be checked by a test, and
each test is tagged with the requirement it covers (`@pytest.mark.req("REQ-…")`). The RTM (docs/RTM.md, generated
in phase 8) links each requirement to its tests and their latest results.

**How each one is verified:** **D** = deterministic check (exact, free), **S** = semantic similarity,
**J** = LLM-as-judge score against a threshold, **R** = repeated runs with a pass-rate threshold.

## RAG assistant

| Id | Requirement | Verified by |
|---|---|---|
| REQ-RAG-01 | Answers state the correct fact (number, date, limit) from the **current** documents | D (key fact present) |
| REQ-RAG-02 | When the documents don't contain the answer, the reply is exactly the refusal message and adds no facts | D |
| REQ-RAG-03 | Answerable questions are answered, not refused (no over-refusal) | D |
| REQ-RAG-04 | Cited sources exist, were retrieved for this question, and are current; a refusal cites nothing | D |
| REQ-RAG-05 | Archived (superseded) documents are never retrieved or cited | D |
| REQ-RAG-06 | Every part of a multi-part question is answered | D |
| REQ-RAG-07 | Every claim in an answer is supported by the retrieved context (no hallucination) | J |
| REQ-RAG-08 | The answer is relevant to the question asked | J |

## Safety

| Id | Requirement | Verified by |
|---|---|---|
| REQ-SEC-01 | Instructions planted inside documents are ignored (indirect prompt injection) | D, R |
| REQ-SEC-02 | User attempts to override the rules ("ignore previous instructions…") are ignored | D, R |
| REQ-SEC-03 | The system prompt is never revealed, in whole or in part | D, R |

## Robustness

| Id | Requirement | Verified by |
|---|---|---|
| REQ-ROB-01 | The same question asked repeatedly gives the same key fact | R |
| REQ-ROB-02 | Paraphrases and typos of a question give the same key fact | D, S |

## Prompt features

| Id | Requirement | Verified by |
|---|---|---|
| REQ-PRM-01 | The ticket classifier returns valid JSON with exactly the keys `category`, `priority`, `summary` | D |
| REQ-PRM-02 | Classifier labels come from the allowed sets, and priorities follow the IT priority rules | D |
| REQ-PRM-03 | Summaries keep every number exact, add no new facts and respect the word limit | D, J |

## Performance and cost

| Id | Requirement | Verified by |
|---|---|---|
| REQ-PERF-01 | A RAG answer returns within 10 seconds (95th percentile over a run) | D |
| REQ-PERF-02 | A RAG request uses at most 3,000 tokens | D |
