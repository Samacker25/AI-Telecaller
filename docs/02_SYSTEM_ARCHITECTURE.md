# 02 — System Architecture

**Project:** AI Telecaller for Hospitals (MVP)

**Version:** 1.0

**Status:** Approved

**Owner:** Solution Architecture

---

# 1. Purpose

This document defines the high-level architecture for the AI Telecaller MVP.

The objective of the architecture is to provide a scalable, maintainable, and secure foundation for an AI-powered hospital receptionist capable of answering patient questions through both chat and voice channels.

The MVP prioritizes simplicity while ensuring the architecture can evolve into a multi-tenant SaaS platform without major redesign.

---

# 2. Architecture Principles

The system is designed according to the following principles.

## Simplicity First

Only build what is required for the MVP.

Avoid premature optimization.

---

## Modular Design

Each component has a single responsibility.

Business logic should remain independent from infrastructure.

---

## AI First

AI capabilities should be reusable across all communication channels.

The same AI backend should power:

- Website Chatbot
- Voice Telecaller
- Future WhatsApp Bot
- Future Mobile App

---

## Cloud Native

Every service should be deployable independently.

No component should depend on local infrastructure.

---

## Stateless Services

Application services should remain stateless whenever possible.

State should be stored in external systems.

---

## API First

All communication between components occurs through APIs.

No direct database access between services.

---

# 3. System Overview

```
                   +----------------------+
                   |      Patient         |
                   +----------+-----------+
                              |
              +---------------+----------------+
              |                                |
              |                                |
      Website Chatbot                  Voice Telecaller
              |                                |
              +---------------+----------------+
                              |
                    FastAPI Backend API
                              |
          +-------------------+-------------------+
          |                                       |
          |                                       |
      AI Service                           Admin APIs
          |
          |
      RAG Pipeline
          |
   +------+------+----------------+
   |             |                |
PostgreSQL   Vector DB      Knowledge Files
              (Pinecone)
```

---

# 4. System Components

## Frontend

Responsibilities

- Chat interface
- Admin dashboard
- Authentication
- Document upload
- Conversation history

Technology

- Next.js
- TypeScript
- TailwindCSS

---

## Backend API

Responsibilities

- REST APIs
- Authentication
- AI orchestration
- Document management
- Session management

Technology

- FastAPI
- Python

---

## AI Service

Responsibilities

- Query understanding
- Prompt construction
- Context management
- LLM interaction
- Confidence evaluation

The AI Service should never directly access raw documents.

All knowledge retrieval must occur through the RAG pipeline.

---

## RAG Pipeline

Responsibilities

- Embed user query
- Semantic search
- Retrieve relevant chunks
- Rank retrieved documents
- Return contextual information

The RAG pipeline is responsible for grounding every AI response.

---

## PostgreSQL

Stores structured application data.

Examples

- Users
- Sessions
- Hospitals
- Doctors
- FAQs
- Conversation history
- Uploaded documents metadata

---

## Vector Database

Stores document embeddings.

Responsibilities

- Similarity search
- Top-K retrieval
- Metadata filtering

Technology

- Pinecone

---

## Knowledge Base

Stores source documents.

Examples

- PDF
- DOCX
- TXT

Examples of hospital information

- Doctor list
- OPD schedule
- Departments
- Packages
- Hospital policies

---

# 5. Request Flow

## Chat Request

```
Patient

↓

Frontend

↓

Backend API

↓

AI Service

↓

RAG Pipeline

↓

Vector Search

↓

Relevant Context

↓

LLM

↓

AI Response

↓

Frontend
```

---

## Document Upload Flow

```
Administrator

↓

Upload Document

↓

Backend

↓

Document Processing

↓

Chunking

↓

Embedding Generation

↓

Vector Database

↓

Metadata Storage

↓

Ready for Search
```

---

# 6. Data Flow

The application manages two primary categories of data.

## Structured Data

Stored in PostgreSQL.

Examples

- Users
- Doctors
- Departments
- Conversations
- Sessions

---

## Unstructured Data

Stored as knowledge documents.

Examples

- PDFs
- FAQs
- Hospital policies
- Medical packages

---

## Semantic Data

Stored in Pinecone.

Examples

- Vector embeddings
- Metadata
- Chunk references

---

# 7. Authentication Flow

Administrator

↓

Login

↓

JWT Token

↓

Protected APIs

↓

Authorization

Only administrators require authentication during the MVP.

Patients can interact with the chatbot anonymously.

---

# 8. Human Escalation

The AI should immediately transfer the conversation when:

- Confidence score below threshold
- No relevant context found
- User requests a human
- Emergency-related queries
- AI cannot answer safely

The MVP only records the escalation request.

Automatic call routing is introduced in Phase 2.

---

# 9. Technology Stack

| Layer | Technology |
|---------|------------|
| Frontend | Next.js |
| Backend | FastAPI |
| Language | Python |
| AI Model | Gemini |
| Framework | LangChain |
| Vector Database | Pinecone |
| Database | PostgreSQL |
| Cache | Redis (Future) |
| Deployment | Railway |
| Frontend Hosting | Vercel |

---

# 10. Deployment Architecture

```
Users

↓

Vercel

↓

FastAPI (Railway)

↓

Gemini API

↓

Pinecone

↓

Neon PostgreSQL
```

Every component uses managed cloud services to minimize operational overhead during the MVP.

---

# 11. Security Boundaries

The architecture follows the principle of least privilege.

Security controls include:

- HTTPS
- JWT Authentication
- Environment variables
- API validation
- Input sanitization
- Prompt injection protection
- Rate limiting
- Audit logging

Detailed security requirements are documented in `07_SECURITY.md`.

---

# 12. Scalability Strategy

The MVP is intentionally simple.

Future scaling will include:

- API Gateway
- Background workers
- Redis
- Message queues
- Kubernetes
- Horizontal scaling
- Multi-region deployment

These enhancements can be introduced without redesigning the overall architecture because system components are loosely coupled.

---

# 13. Failure Handling

The system should gracefully degrade when external services fail.

Examples

| Failure | Behavior |
|----------|----------|
| Gemini unavailable | Return friendly error |
| Pinecone unavailable | Disable AI response |
| Database unavailable | Retry and log |
| Document upload fails | Rollback indexing |
| Retrieval returns nothing | Escalate to human |

The system must never generate answers without retrieved context.

---

# 14. Architectural Decisions

| Decision | Reason |
|----------|--------|
| FastAPI | High performance, async support |
| PostgreSQL | Reliable relational storage |
| Pinecone | Managed vector search |
| Gemini | Strong multimodal and RAG capabilities |
| Next.js | Production-ready frontend |
| Railway | Rapid cloud deployment |
| Vercel | Simple frontend hosting |

---

# 15. Future Architecture Evolution

The MVP architecture is intentionally designed to evolve incrementally.

## Phase 2

- Voice Service
- Twilio Integration
- Speech-to-Text
- Text-to-Speech
- Appointment Booking

---

## Phase 3

- Agentic AI
- Multi-Agent Orchestration
- Workflow Automation
- Calendar Integration
- WhatsApp Integration
- Email Automation
- CRM Integration

---

## Phase 4

- Multi-Tenant SaaS
- RBAC
- Billing
- Analytics
- Audit Dashboard

---

# 16. Architecture Summary

The MVP architecture emphasizes:

- Simplicity over complexity
- Modular services
- AI-first design
- Shared backend for chat and voice
- Secure retrieval using RAG
- Cloud-native deployment
- Future-ready scalability

This architecture provides a stable foundation for validating the product while minimizing engineering complexity and enabling a smooth transition to an enterprise-grade SaaS platform.