# CLAUDE.md

# AI Telecaller – Engineering Guide

This repository contains the MVP implementation of an AI-powered Hospital Telecaller that will evolve into a Voice AI platform, Agentic AI system, and Multi-Tenant SaaS.

This file defines repository-wide engineering rules.

Detailed architecture and design documentation is located in `/docs`.

---

# Mission

Build a production-quality AI assistant that:

- Answers hospital-related questions accurately using RAG.
- Never hallucinates hospital information.
- Escalates uncertain conversations to human staff.
- Prioritizes security, maintainability, and reliability over rapid feature delivery.

---

# Product Scope

Current Phase:

**Phase 1 — AI Website Chatbot (MVP)**

Current capabilities:

- Authentication
- Admin Dashboard
- Knowledge Base
- RAG
- Hospital FAQ
- Doctor Information
- Department Information
- Conversation History

Do not implement future roadmap features unless explicitly requested.

---

# Documentation

The `/docs` directory is the source of truth.

Follow the documents in this order:

1. Product Requirements
2. System Architecture
3. Backend Architecture
4. AI RAG Architecture
5. Database Schema
6. API Specification
7. Security
8. Deployment
9. Test Plan
10. Roadmap
11. AI Evaluation

Do not duplicate documentation.

---

# Engineering Principles

Always prioritize:

- Simplicity
- Readability
- Maintainability
- Security
- Testability
- Scalability

Prefer clean code over clever code.

---

# Architecture Rules

Current architecture:

Modular Monolith

Do NOT introduce:

- Microservices
- Kubernetes
- Event Bus
- Service Mesh

unless explicitly requested.

Future migration should remain possible without rewriting business logic.

---

# Backend Rules

Use:

- FastAPI
- Async endpoints
- Dependency Injection
- Repository Pattern
- Service Layer

Never place business logic inside API routes.

Routes should:

- Validate input
- Call services
- Return responses

Nothing more.

---

# AI Rules

The AI must:

- Use retrieved context.
- Never invent hospital information.
- Refuse unsupported medical advice.
- Escalate low-confidence conversations.

Always prefer:

Retrieval → Generation

Never:

Generation → Retrieval

---

# RAG Rules

Every answer must:

- Retrieve relevant knowledge.
- Ground the response.
- Cite internal knowledge when appropriate.
- Return uncertainty instead of hallucinating.

Do not answer from model memory when hospital knowledge is required.

---

# Database Rules

Use PostgreSQL for:

- Operational data
- Conversations
- Doctors
- Departments
- FAQs

Use Pinecone only for embeddings.

Never store operational data inside Pinecone.

---

# API Rules

REST-first.

Version every endpoint.

Example:

/api/v1/

Always:

- Validate input
- Return proper HTTP status codes
- Handle exceptions gracefully

---

# Security Rules

Never:

- Hardcode secrets
- Trust user input
- Skip authentication
- Log sensitive information

Always:

- Validate uploads
- Sanitize inputs
- Verify authorization
- Apply least privilege

---

# Error Handling

Errors must:

- Be logged
- Be traceable
- Return safe client responses

Never expose stack traces.

---

# Logging

Every request should have:

- Request ID
- Timestamp
- Duration
- Route
- Status

Sensitive data must never be logged.

---

# Testing

All production features require:

- Unit tests
- Integration tests
- API tests

Regression tests are mandatory before release.

AI changes should be evaluated using the Golden Dataset once the evaluation framework is introduced.

---

# Coding Standards

Write:

- Small functions
- Clear names
- Type hints
- Docstrings where appropriate

Avoid:

- Deep nesting
- Duplicate code
- Global mutable state
- Magic values

---

# Performance

Prefer:

- Async I/O
- Database indexing
- Efficient queries

Avoid premature optimization.

Measure before optimizing.

---

# Documentation Rules

Every significant feature should update:

- API documentation
- Architecture documentation
- Tests

Keep documentation synchronized with implementation.

---

# Git Rules

Every change should:

- Compile
- Pass tests
- Maintain formatting
- Preserve backward compatibility where practical

Commit messages should be clear and descriptive.

---

# Definition of Done

A feature is complete only if:

- Code is implemented.
- Tests pass.
- Documentation is updated.
- Logging is included.
- Errors are handled.
- Security considerations are addressed.
- Performance impact is acceptable.

---

# Future Awareness

The MVP should remain compatible with future phases:

Phase 2

- Voice AI

Phase 3

- AI Agents

Phase 4

- Multi-Tenant SaaS

Design today's code so these capabilities can be added with minimal refactoring.

---

# Core Philosophy

Build software that is:

- Secure
- Reliable
- Observable
- Testable
- Modular
- Easy to maintain

Optimize for long-term engineering quality rather than short-term implementation speed.