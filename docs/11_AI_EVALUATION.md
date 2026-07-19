# 11 — AI Evaluation

**Project:** AI Telecaller for Hospitals (MVP)

**Version:** 0.1 (Golden Dataset framework — Phase 4)

**Owner:** AI Architecture Team

---

# 1. Purpose

Every change to the RAG pipeline (chunking, embeddings, retrieval parameters, prompts, models) must be evaluated before release. This document describes the evaluation framework introduced in Phase 4.

---

# 2. Golden Dataset

The golden dataset lives at `backend/evals/golden_dataset.json`: a JSON array of cases, each describing a question and what a correct response looks like.

```json
{
  "id": "opd-timings",
  "question": "What are the OPD timings?",
  "expected_keywords": ["OPD"],
  "expect_escalation": false
}
```

| Field | Meaning |
|-------|---------|
| `id` | Stable case identifier used in reports |
| `question` | The patient question sent to the RAG service |
| `expected_keywords` | Case-insensitive strings the answer must contain (non-escalation cases) |
| `expect_escalation` | Whether the correct behavior is to escalate to a human |

The dataset covers both answerable questions and questions that must escalate (emergencies, medical-advice requests, out-of-scope questions). Extend it whenever a regression or new behavior is worth pinning.

---

# 3. Framework

`app/ai/evaluation.py` provides:

- `load_golden_dataset(path)` — parses and validates the dataset (`GoldenDatasetError` on malformed input).
- `evaluate_rag(service, hospital_id, cases)` — runs each case through `RagService` in a fresh conversation and returns an `EvaluationReport`.

A case **passes** when the escalation outcome matches `expect_escalation` and, for non-escalation cases, every expected keyword appears in the answer.

Report metrics:

| Metric | Meaning |
|--------|---------|
| `pass_rate` | Fraction of cases fully passing |
| `escalation_accuracy` | Fraction of cases with the correct escalation decision |
| Per-case results | Escalated flag, confidence, missing keywords |

---

# 4. Running an Evaluation

Against the live providers (requires `GEMINI_API_KEY`, `PINECONE_API_KEY`, `PINECONE_INDEX`, a hospital profile, and an indexed knowledge base):

```
cd backend
python -m scripts.rag_eval            # uses evals/golden_dataset.json
python -m scripts.rag_eval other.json # custom dataset
```

The script prints a per-case PASS/FAIL table plus aggregate metrics and exits non-zero if any case fails, so it can gate CI or release checklists.

Deterministic unit tests exercise the framework itself with fake providers (`backend/tests/test_rag_evaluation.py`); no credentials are needed for the test suite.

---

# 5. Release Rule

Before releasing an AI change:

1. Run the full test suite.
2. Run the golden-dataset evaluation against a staging knowledge base.
3. Compare pass rate and escalation accuracy with the previous release; investigate any regression before shipping.

---

# 6. Future Work

- Larger dataset with per-department coverage.
- Faithfulness scoring (LLM-as-judge) in addition to keyword checks.
- Latency tracking per pipeline stage.
- Automatic evaluation runs in CI on a seeded staging index.
