# AI Telecaller MVP Development Tasks

## Phase 0 — Project Foundation ✅ (completed 2026-07-19)

### T001 — Initialize Repository ✅
- [x] Create backend structure
- [x] Create frontend structure
- [x] Configure Git
- [x] Configure pre-commit
- [x] Configure formatting

---

### T002 — Project Configuration ✅
- [x] Environment variables
- [x] Settings management
- [x] Logging
- [x] Configuration loader

---

### T003 — Database Setup ✅
- [x] PostgreSQL connection
- [x] SQLAlchemy
- [x] Async session
- [x] Alembic
- [x] Base model

---

### T004 — Docker Setup ✅
- [x] Backend Dockerfile
- [x] Frontend Dockerfile
- [x] docker-compose
- [x] Local development

---

### T005 — CI/CD ✅
- [x] GitHub Actions
- [x] Lint
- [x] Tests
- [x] Build

### T006 — Backend Project Structure ✅

### T007 — Frontend Project Structure ✅

### T008 — Shared Utilities & Core Modules ✅

### T009 — Health Check & Smoke Test APIs ✅
---

# Phase 1 — Authentication ✅ (completed 2026-07-19)

### T010 — User Model ✅
- [x] `users` table (UUID id, name, email, password_hash, role, is_active, timestamps)
- [x] Alembic migration `0001_create_users_table`

### T011 — Password Hashing ✅
- [x] bcrypt hashing and verification (`app/core/security.py`)

### T012 — JWT Authentication ✅
- [x] Token creation/decoding with expiry (HS256, PyJWT)
- [x] Bearer token dependency (`app/api/deps.py`)

### T013 — Login API ✅
- [x] `POST /api/v1/auth/login` returning access_token / token_type / expires_in

### T014 — Register API ✅
- [x] `POST /api/v1/auth/register` (first user becomes admin, later users staff)

### T015 — Current User API ✅
- [x] `GET /api/v1/auth/me`

### T016 — Role Based Access ✅
- [x] `require_roles` dependency; admin-only `GET /api/v1/auth/users`

### T017 — Auth Tests ✅
- [x] Hashing, register, login, /me, and RBAC tests (27 tests passing)

---

# Phase 2 — Hospital Management ✅ (completed 2026-07-19)

### T020 — Hospital Model ✅
- [x] `hospitals` table (UUID id, name, address, phone, email, website, settings JSON, timestamps)
- [x] Alembic migration `0002_create_hospital_tables`

### T021 — Hospital CRUD ✅
- [x] `GET/POST /api/v1/hospitals`, `GET/PUT /api/v1/hospitals/{id}` (public reads, admin writes)
- [x] Single-hospital MVP: second create returns 409

### T022 — Department Model ✅
- [x] `departments` table (hospital FK, unique name per hospital)

### T023 — Department CRUD ✅
- [x] `GET/POST /api/v1/departments`, `GET/PUT/DELETE /api/v1/departments/{id}`
- [x] Case-insensitive duplicate-name protection; delete blocked while doctors exist

### T024 — Doctor Model ✅
- [x] `doctors` table (hospital + department FKs, specialization, qualification, opd_schedule JSON, is_available)

### T025 — Doctor CRUD ✅
- [x] `GET/POST /api/v1/doctors`, `GET/PUT/DELETE /api/v1/doctors/{id}`
- [x] Public list filters: department_id, specialization (case-insensitive), available

### T026 — Working Hours ✅
- [x] `WeeklySchedule` schema (per-day time slots, end-after-start and overlap validation)
- [x] Used for doctor OPD schedules and hospital working hours

### T027 — Hospital Settings ✅
- [x] `GET/PUT /api/v1/hospitals/{id}/settings` (working hours, emergency contact, escalation email)
- [x] Stored as validated JSON on the hospital record

---

# Phase 3 — Knowledge Base ✅ (completed 2026-07-19)

### T030 — Document Upload ✅
- [x] `POST /api/v1/documents` (multipart; PDF/DOCX/TXT; type, size, and empty-file validation)
- [x] Files stored under `UPLOAD_DIRECTORY` with server-generated names (`{document_id}.{ext}`)

### T031 — PDF Parser ✅
- [x] pypdf text extraction (`app/ai/parsers.py`)

### T032 — DOCX Parser ✅
- [x] python-docx extraction of paragraphs and tables

### T033 — Text Cleaner ✅
- [x] Unicode NFKC, line endings, control chars, whitespace (`app/ai/text_cleaner.py`)

### T034 — Chunking ✅
- [x] Paragraph-aware chunking with word-boundary overlap (`app/ai/chunker.py`)

### T035 — Embeddings ✅
- [x] `EmbeddingClient` protocol + `GeminiEmbeddingClient` (`app/ai/embeddings.py`)

### T036 — Pinecone ✅
- [x] `VectorStore` protocol + `PineconeVectorStore` (namespace per hospital, prefix deletes)

### T037 — Metadata Storage ✅
- [x] `documents` table + migration `0003` (status lifecycle: uploaded → processing → indexed/failed)

### T038 — Knowledge CRUD ✅
- [x] List/get/delete/reindex endpoints; `KnowledgeService`; 21 API + ingestion unit tests

---

# Phase 4 — RAG ✅ (completed 2026-07-19)

### T040 — Retrieval Engine ✅
- [x] `VectorStore.query` + `RetrievedChunk` (Pinecone similarity search per hospital namespace)
- [x] `Retriever` (`app/ai/retriever.py`): embed query → top-k search → drop scores below `RETRIEVAL_MIN_SCORE`

### T041 — Prompt Builder ✅
- [x] `app/ai/prompt_builder.py`: fixed order system → numbered context `[n]` → history → question
- [x] Grounding, no-medical-advice, and prompt-injection-resistance rules in the system instruction

### T042 — Gemini Integration ✅
- [x] `LLMClient` protocol + `GeminiLLMClient` (`LLM_MODEL`, temperature, output cap; `LLMError` on failure)

### T043 — Conversation Memory ✅
- [x] `ConversationMemory` (`app/ai/memory.py`): bounded window (`CONVERSATION_MAX_TURNS`), oldest dropped first, `clear()`
- [x] Persistence deferred to Phase 5 conversation storage by design

### T044 — Citation Support ✅
- [x] Answers carry `Citation` list (document_id, file_name, chunk_index, score); prompt instructs `[n]` markers

### T045 — Confidence Score ✅
- [x] Confidence = best retrieval similarity; `RAG_CONFIDENCE_THRESHOLD` gates generation

### T046 — Human Escalation ✅
- [x] `RagService` escalates with safe fallback answers: emergency, medical_advice, no_knowledge, low_confidence, generation_failed
- [x] Deterministic emergency/medical-advice detection (`app/ai/safety.py`); emergency contact injected when configured

### T047 — RAG Evaluation ✅
- [x] Golden dataset (`backend/evals/golden_dataset.json`) + framework (`app/ai/evaluation.py`)
- [x] `python -m scripts.rag_eval` runner; docs/11_AI_EVALUATION.md written; 35 RAG/eval tests passing

---

# Phase 5 — Chat API

### T050 — Chat Endpoint

### T051 — Conversation Storage

### T052 — Session Management

### T053 — Streaming Response

### T054 — Chat History

---

# Phase 6 — Frontend

### T060 — Login Page

### T061 — Dashboard

### T062 — Chat UI

### T063 — Hospital Settings

### T064 — Doctor Management

### T065 — Knowledge Base UI

---

# Phase 7 — Security

### T070 — Rate Limiting

### T071 — File Validation

### T072 — Prompt Injection Protection

### T073 — API Security

### T074 — Audit Logs

---

# Phase 8 — Monitoring

### T080 — Structured Logging

### T081 — Metrics

### T082 — Health Checks

### T083 — Error Monitoring

---

# Phase 9 — Deployment

### T090 — Railway Deployment

### T091 — Docker Production

### T092 — Environment Validation

### T093 — Domain Configuration

---

# Phase 10 — Testing

### T100 — Unit Tests

### T101 — Integration Tests

### T102 — E2E Tests

### T103 — AI Evaluation

### T104 — Performance Testing

---

# Phase 11 — Production Readiness

### T110 — Backup Strategy

### T111 — Documentation

### T112 — Release Checklist

### T113 — Final Security Review

### T114 — MVP Release