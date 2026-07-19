# Progress Log

## 2026-07-19 — Phase 0 Complete

### T001 — Initialize Repository ✅
- Repository created on GitHub and cloned (done previously).
- Backend structure under `backend/app/` (api, core, database, models, schemas, repositories, services, ai, utils).
- Frontend scaffolded with create-next-app (Next.js + TypeScript + Tailwind + ESLint, `src/` + App Router).
- `.pre-commit-config.yaml` (ruff, black, hygiene hooks).
- Formatting configured via `backend/pyproject.toml` (black + ruff, line length 100).

### T002 — Project Configuration ✅
- `app/core/config.py` — pydantic-settings `Settings` loaded from env vars / `.env`.
- `backend/.env.example` and `frontend/.env.example` document required variables.
- `app/core/logging.py` — JSON structured logging with request-ID context var.
- `app/core/middleware.py` — request ID + duration logging middleware.
- `app/core/exceptions.py` — standardized error envelope `{success, error: {code, message}}`.

### T003 — Database Setup ✅
- `app/database/base.py` — `Base` with naming conventions, `IDMixin`, `TimestampMixin`.
- `app/database/session.py` — lazy async engine, `async_sessionmaker`, `get_db` dependency.
- Alembic configured for async engine (`backend/alembic/`), URL read from settings (env), no migrations yet (no models yet).

### T004 — Docker Setup ✅
- `docker/backend.Dockerfile` (python 3.12-slim, non-root, healthcheck).
- `docker/frontend.Dockerfile` (node 22-alpine multi-stage).
- `docker-compose.yml` — postgres:16 + backend + frontend for local dev.

### T005 — CI/CD ✅
- `.github/workflows/ci.yml` — backend (ruff, black --check, pytest), frontend (lint, build), backend docker build.

### T010–T013 ✅
- Backend/front-end structures in place; health module: `GET /health`, `/live`, `/ready` (root, unauthenticated) + `GET /api/v1/ping` smoke test.
- `/ready` checks DB via `HealthService` (route → service → session, no logic in routes).
- API tests in `backend/tests/test_health.py` run against in-memory SQLite (aiosqlite).

### Notes / decisions
- Dependency layout: `requirements.txt` (runtime) + `requirements-dev.txt` (tooling); pyproject used only for tool config.
- Health endpoints live at app root (not versioned) per `docs/08_DEPLOYMENT.md` §14.
- Tests use dependency override of `get_db` — no Postgres needed locally or in CI.

### Next
- Phase 1 — Authentication (T010–T017 in tasks.md Phase 1 section).

## 2026-07-19 — Phase 3 Complete (Knowledge Base, T030–T038)

### Ingestion pipeline (`app/ai/`)
- `parsers.py` — PDF (pypdf), DOCX (python-docx, paragraphs + tables), TXT (utf-8 with latin-1 fallback); raises `DocumentParseError` on unreadable/empty documents.
- `text_cleaner.py` — NFKC normalization, line endings, control chars, whitespace; preserves paragraph breaks.
- `chunker.py` — paragraph-aware chunks (`CHUNK_SIZE`=1200 chars) with word-boundary overlap (`CHUNK_OVERLAP`=200).
- `embeddings.py` — `EmbeddingClient` protocol; `GeminiEmbeddingClient` (`gemini-embedding-001`, 768 dims, batches of 100).
- `vector_store.py` — `VectorStore` protocol; `PineconeVectorStore`: IDs `{document_id}:{chunk_index}`, namespace per hospital, deletes via ID-prefix listing (serverless-safe).

### Service / API
- `documents` table + migration `0003` (metadata only; status uploaded → processing → indexed/failed, `chunk_count`, `error_message`, `uploaded_by`).
- `KnowledgeService` — upload validation (type/size/empty), file storage under `UPLOAD_DIRECTORY` as `{document_id}.{ext}`, sync ingestion with status tracking, reindex, delete (vectors + file + record). Sync SDK calls wrapped in `run_in_threadpool`.
- `POST/GET /api/v1/documents`, `GET/DELETE /documents/{id}`, `POST /documents/{id}/reindex`. Writes admin-only, reads authenticated. Upload responds `{document_id, status}` per API spec.

### Notes / decisions
- Ingestion runs synchronously in the upload request (spec budget <30 s); failures mark the document `failed` instead of failing the request, so uploads are never lost.
- Providers injected behind protocols and built in `get_knowledge_service` (documents.py); tests override with in-memory fakes — no Gemini/Pinecone needed (`tests/test_knowledge.py`, `tests/test_ingestion.py`; 106 tests passing).
- Missing AI credentials → documents marked `failed` with `AI_NOT_CONFIGURED`; app remains usable in dev.
- New deps: pypdf, python-docx, python-multipart, google-genai, pinecone.
- `docs/04_AI_RAG_ARCHITECTURE.md` written (ingestion half; retrieval/generation reserved for Phase 4).

### Next
- Phase 4 — RAG (T040–T047): retrieval engine, prompt builder, Gemini generation, confidence + escalation.

## 2026-07-19 — Phase 4 Complete (RAG, T040–T047)

### Answering pipeline (`app/ai/` + `app/services/rag_service.py`)
- `vector_store.py` — added `VectorStore.query` + `RetrievedChunk` (Pinecone similarity search, per-hospital namespace, metadata returned).
- `retriever.py` — `Retriever`: embed query → top-k search → drop matches below `RETRIEVAL_MIN_SCORE` (0.45), sorted best-first; logs latency/scores/doc IDs.
- `llm.py` — `LLMClient` protocol; `GeminiLLMClient` (`LLM_MODEL`=gemini-2.5-flash, temperature 0.2, 1024-token cap); `LLMError` on failure/empty output.
- `memory.py` — `ConversationMemory`: bounded turn window (`CONVERSATION_MAX_TURNS`=10), `clear()`; persistence deferred to Phase 5.
- `prompt_builder.py` — fixed order system → numbered context `[n]` → history → question; grounding + no-medical-advice + injection-resistance rules.
- `safety.py` — deterministic regex detection of emergencies and medical-advice requests (false positives route to humans — the safe direction).
- `rag_service.py` — `RagService.answer`: safety checks → retrieve → confidence (best similarity) → generate or escalate. Returns `RagAnswer {answer, confidence, escalated, escalation_reason, citations}` (`app/schemas/rag.py`, Pydantic for Phase 5 reuse). Escalation reasons: emergency, medical_advice, no_knowledge, low_confidence, generation_failed. Vector-store outage raises 503 `VECTOR_STORE_UNAVAILABLE`.

### Evaluation (T047)
- `app/ai/evaluation.py` — `load_golden_dataset` + `evaluate_rag` (per-case pass, pass rate, escalation accuracy).
- `backend/evals/golden_dataset.json` — 7 seed cases (answerable + must-escalate).
- `python -m scripts.rag_eval` — runs the dataset against live providers, exits non-zero on failure (release gate).
- `docs/11_AI_EVALUATION.md` written; `docs/04_AI_RAG_ARCHITECTURE.md` updated to v0.2 (answering pipeline documented).

### Notes / decisions
- Confidence = best retrieval similarity score — simple, deterministic, explainable; thresholds configurable (`RAG_CONFIDENCE_THRESHOLD`=0.55).
- Escalations still record both turns in memory so follow-ups stay coherent; escalated answers never include invented content or citations.
- `RagService` takes no DB session — Phase 5's chat service owns persistence and can pass `emergency_contact` from hospital settings.
- Tests: `tests/test_rag.py` + `tests/test_rag_evaluation.py` (35 new; 141 total passing) with fake embedder/vector store/LLM — no credentials needed.

### Next
- Phase 5 — Chat API (T050–T054): chat endpoint, conversation storage, sessions, streaming, history.
