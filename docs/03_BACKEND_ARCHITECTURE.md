# 03 — Backend Architecture

**Project:** AI Telecaller for Hospitals (MVP)

**Version:** 1.0

**Status:** Approved

**Owner:** Backend Architecture

---

# 1. Purpose

This document describes the backend architecture of the AI Telecaller MVP.

The backend is responsible for:

- Serving REST APIs
- Managing AI conversations
- Executing Retrieval-Augmented Generation (RAG)
- Managing hospital knowledge
- Processing uploaded documents
- Authenticating administrators
- Logging conversations
- Providing a reusable backend for both chatbot and future voice services

---

# 2. Design Philosophy

The backend follows the following engineering principles.

## Modular Monolith

The MVP is intentionally built as a Modular Monolith.

Reasons:

- Faster development
- Easier debugging
- Lower deployment complexity
- Single codebase
- Faster iteration

Each module is isolated and can later become an independent microservice without major refactoring.

---

## API First

All business capabilities are exposed through REST APIs.

No frontend should directly access databases.

---

## Domain Driven Organization

Code is organized by business domain instead of technical layers.

Example:

```
chat/
knowledge/
documents/
auth/
admin/
```

instead of

```
controllers/
models/
services/
```

---

## Clean Architecture

Business logic must never depend on frameworks.

Dependencies always point inward.

```
API

↓

Application

↓

Domain

↓

Infrastructure
```

---

## Asynchronous Processing

Long-running tasks should execute asynchronously.

Examples:

- Document indexing
- Embedding generation
- File processing

---

# 3. High-Level Backend Architecture

```
                Frontend

                    │

                    ▼

            FastAPI Application

                    │

      ┌─────────────┼─────────────┐

      ▼             ▼             ▼

   Chat Module   Admin Module   Auth Module

      │             │             │

      └─────────────┼─────────────┘

                    ▼

             AI Service Layer

                    ▼

             RAG Pipeline

      ┌─────────────┼─────────────┐

      ▼             ▼             ▼

 PostgreSQL    Pinecone      File Storage
```

---

# 4. Backend Modules

## Chat Module

Responsibilities

- Receive user messages
- Maintain conversation
- Call AI Service
- Return responses

Example APIs

```
POST /chat
POST /chat/reset
GET /chat/history
```

---

## AI Module

Responsibilities

- Prompt construction
- Context injection
- LLM interaction
- Confidence evaluation
- Response formatting

The AI Module never queries databases directly.

It always uses the RAG module.

---

## RAG Module

Responsibilities

- Embed query
- Vector search
- Retrieve documents
- Rank context
- Return relevant chunks

The RAG module ensures AI responses remain grounded in hospital knowledge.

---

## Knowledge Module

Responsibilities

- Upload documents
- Parse documents
- Chunk content
- Generate embeddings
- Store metadata

Supported files

- PDF
- DOCX
- TXT

---

## Admin Module

Responsibilities

- Login
- Document management
- FAQ management
- View conversations
- Trigger re-indexing

---

## Authentication Module

Responsibilities

- JWT generation
- Login
- Token validation
- Authorization

Only administrators require authentication.

Patients interact anonymously.

---

## Health Module

Responsibilities

Provide monitoring endpoints.

Example

```
GET /health

GET /ready

GET /live
```

---

# 5. Folder Structure

```
backend/

├── app/
│
├── api/
│
├── modules/
│   │
│   ├── auth/
│   ├── chat/
│   ├── rag/
│   ├── ai/
│   ├── knowledge/
│   ├── documents/
│   ├── admin/
│   └── health/
│
├── core/
│
├── database/
│
├── infrastructure/
│
├── models/
│
├── schemas/
│
├── utils/
│
├── tests/
│
└── main.py
```

---

# 6. Request Lifecycle

```
HTTP Request

↓

API Router

↓

Validation

↓

Business Service

↓

RAG

↓

LLM

↓

Response Builder

↓

HTTP Response
```

---

# 7. Service Layer Responsibilities

The service layer contains all business logic.

Examples

- AI orchestration
- Prompt generation
- Conversation management
- Retrieval
- Escalation logic

Business logic must never exist inside API routes.

---

# 8. Data Layer

The backend uses three storage systems.

## PostgreSQL

Stores structured data.

Examples

- Users
- Doctors
- FAQs
- Conversations
- Sessions
- Metadata

---

## Pinecone

Stores vector embeddings.

Responsibilities

- Similarity search
- Semantic retrieval

---

## File Storage

Stores uploaded source documents.

Examples

- PDFs
- DOCX
- TXT

---

# 9. API Layer

The API layer should contain only:

- Validation
- Authentication
- Routing
- Serialization

No business logic.

---

Example

```
Client

↓

Router

↓

Service

↓

Repository

↓

Database
```

---

# 10. Repository Layer

Repositories isolate database operations.

Example

```
DoctorRepository

ConversationRepository

DocumentRepository

FAQRepository
```

Advantages

- Easier testing
- Database independence
- Better maintainability

---

# 11. AI Processing Pipeline

```
Question

↓

Validation

↓

Conversation Context

↓

Retriever

↓

Top-K Documents

↓

Prompt Builder

↓

Gemini

↓

Response

↓

Confidence Check

↓

Return
```

---

# 12. Error Handling

Every module returns standardized responses.

Example

```json
{
    "success": false,
    "error": {
        "code": "DOCUMENT_NOT_FOUND",
        "message": "Requested document does not exist."
    }
}
```

Unexpected exceptions must never expose internal details.

---

# 13. Logging

Every request should generate logs.

Examples

- Request ID
- User Session
- API
- Duration
- Status Code
- AI Model
- Retrieved Documents
- Errors

Sensitive information must never be logged.

---

# 14. Configuration

Configuration must come exclusively from environment variables.

Examples

```
DATABASE_URL

GEMINI_API_KEY

PINECONE_API_KEY

JWT_SECRET

UPLOAD_DIRECTORY
```

Hardcoded secrets are prohibited.

---

# 15. Security

Backend security includes

- JWT Authentication
- Password Hashing
- HTTPS
- Request Validation
- File Validation
- Prompt Injection Protection
- Rate Limiting
- Audit Logging

See:

`07_SECURITY.md`

---

# 16. Performance Goals

| Metric | Target |
|---------|---------|
| Average API Response | <300 ms (excluding LLM latency) |
| AI Response | <3 seconds |
| Document Upload | <30 seconds |
| Health Endpoint | <50 ms |
| Retrieval | <500 ms |

---

# 17. Future Evolution

The Modular Monolith is intentionally designed for future decomposition.

Potential future services:

```
API Gateway

↓

Authentication Service

↓

Chat Service

↓

AI Service

↓

RAG Service

↓

Knowledge Service

↓

Notification Service

↓

Analytics Service
```

Because modules are isolated, each can be extracted into its own service with minimal code changes.

---

# 18. Architectural Decisions

| Decision | Reason |
|----------|--------|
| FastAPI | Async, high performance, Python ecosystem |
| Modular Monolith | Faster MVP delivery |
| PostgreSQL | Reliable relational database |
| Pinecone | Managed vector search |
| Gemini | High-quality generative AI |
| REST APIs | Simplicity and interoperability |
| Repository Pattern | Separation of persistence logic |
| Service Layer | Centralized business logic |

---

# 19. Backend Principles

The backend should always follow these principles:

- Single Responsibility Principle
- Separation of Concerns
- Clean Architecture
- Dependency Injection
- Stateless APIs
- Domain-Based Modules
- Async by Default
- Secure by Default
- Testable Components
- Observable Services

---

# 20. Summary

The backend architecture is designed to maximize developer productivity during the MVP while establishing a strong foundation for future growth.

Key characteristics:

- Modular Monolith
- Clean Architecture
- API-First Design
- AI-Centric Backend
- RAG-Based Knowledge Retrieval
- Cloud-Native Deployment
- Future-Ready Microservice Migration

This architecture minimizes operational complexity today while enabling a smooth transition to a distributed, enterprise-grade platform as product adoption grows.