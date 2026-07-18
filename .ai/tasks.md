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

# Phase 2 — Hospital Management

### T020 — Hospital Model

### T021 — Hospital CRUD

### T022 — Department Model

### T023 — Department CRUD

### T024 — Doctor Model

### T025 — Doctor CRUD

### T026 — Working Hours

### T027 — Hospital Settings

---

# Phase 3 — Knowledge Base

### T030 — Document Upload

### T031 — PDF Parser

### T032 — DOCX Parser

### T033 — Text Cleaner

### T034 — Chunking

### T035 — Embeddings

### T036 — Pinecone

### T037 — Metadata Storage

### T038 — Knowledge CRUD

---

# Phase 4 — RAG

### T040 — Retrieval Engine

### T041 — Prompt Builder

### T042 — Gemini Integration

### T043 — Conversation Memory

### T044 — Citation Support

### T045 — Confidence Score

### T046 — Human Escalation

### T047 — RAG Evaluation

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