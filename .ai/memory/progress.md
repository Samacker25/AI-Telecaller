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
