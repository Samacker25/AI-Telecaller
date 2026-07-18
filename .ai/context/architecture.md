# Architecture Context

## Current Architecture

The project follows a **Modular Monolith** architecture.

Future migration to microservices is planned but must not influence MVP complexity.

---

## High-Level Flow

```
User

↓

Frontend

↓

FastAPI Backend

↓

AI Service

↓

RAG Pipeline

↓

Gemini

↓

Response

↓

Human Escalation (if required)
```

---

## Major Components

Frontend

- Next.js
- React
- TypeScript

Backend

- FastAPI
- Async Python
- Service Layer
- Repository Pattern

Data

- PostgreSQL
- Pinecone

AI

- Gemini
- LangChain
- RAG

---

## Design Principles

- Separation of concerns
- Dependency Injection
- Service Layer
- Repository Pattern
- Async programming
- Modular design

---

## Future Roadmap

Phase 1

Website Chatbot

↓

Phase 2

Voice AI

↓

Phase 3

AI Agents

↓

Phase 4

Multi-Tenant SaaS

Current development must remain compatible with future phases while avoiding unnecessary abstraction.