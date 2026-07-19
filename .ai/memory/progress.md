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
