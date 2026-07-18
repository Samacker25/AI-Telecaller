# FastAPI Skill

## Purpose

This document defines the FastAPI development standards for the AI Telecaller project.

It provides implementation guidelines that every developer and AI coding assistant must follow to ensure consistency, maintainability, scalability, and production readiness.

These rules apply to every FastAPI module in this repository.

---

# Core Principles

Always build APIs that are:

- Simple
- Async
- Modular
- Secure
- Testable
- Observable
- Maintainable

Business logic must remain independent from the web framework.

---

# Architecture

Always follow this flow:

```

HTTP Request

↓

API Route

↓

Service Layer

↓

Repository Layer

↓

Database

↓

Response

```

Never skip layers.

---

# Project Structure

```

app/

api/
core/
database/
models/
schemas/
repositories/
services/
ai/
utils/

```

Every module should follow this structure.

---

# API Routes

Routes should only:

- Validate requests
- Authenticate users
- Call services
- Return responses

Routes must NOT:

- Query the database
- Call SQLAlchemy directly
- Contain business logic
- Build AI prompts
- Perform vector search

Keep route handlers small.

Target:

< 30 lines whenever possible.

---

# Service Layer

Business logic belongs here.

Services may:

- Call repositories
- Call AI services
- Call external APIs
- Handle transactions
- Perform validations

Services should never depend on HTTP objects.

Never use:

- Request
- Response
- FastAPI routing decorators

inside services.

---

# Repository Layer

Repositories are responsible for:

- Database access
- CRUD operations
- Queries
- Pagination
- Filtering

Repositories should never contain business rules.

---

# Dependency Injection

Always use FastAPI dependency injection.

Inject:

- Database session
- Current user
- Authentication
- Configuration
- Services

Avoid global state.

---

# Async Programming

Use async for:

- Database operations
- HTTP requests
- AI model calls
- Vector database
- File operations

Avoid blocking code inside async functions.

---

# Request Validation

Always validate:

- Request body
- Query parameters
- Path parameters
- Uploaded files

Use Pydantic models.

Never trust client input.

---

# Response Models

Always define response schemas.

Never return:

- SQLAlchemy models
- Raw dictionaries
- Internal exceptions

Responses should be stable and versioned.

---

# Error Handling

Raise meaningful exceptions.

Convert internal errors into user-friendly responses.

Never expose:

- Stack traces
- Database errors
- Internal implementation details

Log detailed errors internally.

---

# Authentication

Protect all administrative endpoints.

Use:

- JWT
- Role-based authorization

Never trust client-provided roles.

---

# Authorization

Verify authorization inside the service layer.

Do not rely only on frontend restrictions.

Every protected action must verify permissions.

---

# Database Sessions

Use dependency injection for database sessions.

Never create sessions manually inside services.

Keep transactions short.

Rollback on failure.

---

# Pagination

Large collections must support:

- limit
- offset

Future support:

- cursor pagination

Never return thousands of records in one request.

---

# Filtering

Support filtering through query parameters.

Filtering should happen in the database, not in Python.

---

# File Uploads

Validate:

- MIME type
- File extension
- File size

Reject unsupported files.

Never trust uploaded filenames.

---

# Background Tasks

Use FastAPI BackgroundTasks only for lightweight operations.

Future long-running jobs should use dedicated workers.

---

# Configuration

All configuration belongs in environment variables.

Never hardcode:

- Secrets
- URLs
- API Keys
- Database credentials

Centralize configuration in `core/config.py`.

---

# Logging

Every request should generate structured logs.

Include:

- Request ID
- Endpoint
- Status Code
- Duration

Never log:

- Passwords
- Tokens
- Personal information

---

# Health Endpoints

Provide:

```

GET /health

GET /ready

```

Health endpoints should not perform expensive operations.

---

# API Versioning

Always version APIs.

Example:

```

/api/v1/

```

Future breaking changes require new API versions.

---

# OpenAPI Documentation

Use:

- Summary
- Description
- Tags
- Response models
- Status codes

Generate complete OpenAPI documentation automatically.

---

# Performance

Prefer:

- Async endpoints
- Efficient queries
- Database indexes
- Connection pooling

Avoid premature optimization.

Measure before optimizing.

---

# Testing

Every endpoint requires:

- Unit tests
- Integration tests
- API tests

Critical endpoints require authentication tests.

---

# Security

Always:

- Validate input
- Escape output where appropriate
- Verify authentication
- Verify authorization
- Sanitize uploads

Never assume user input is safe.

---

# Documentation

Every new endpoint must update:

- API Specification
- Test Plan (if applicable)

Documentation should remain synchronized with implementation.

---

# Code Style

Prefer:

- Small functions
- Descriptive names
- Type hints
- Docstrings for public functions

Avoid:

- Deep nesting
- Long functions
- Duplicate logic
- Global mutable state

---

# Definition of Done

A FastAPI feature is complete only if:

- Routes are implemented.
- Service layer is complete.
- Repository layer is complete.
- Request validation exists.
- Response models exist.
- Error handling is implemented.
- Authentication is enforced.
- Authorization is verified.
- Logging is included.
- Tests pass.
- Documentation is updated.

---

# Anti-Patterns

Never:

- Put business logic in routes.
- Access the database directly from routes.
- Mix HTTP logic with business logic.
- Hardcode configuration.
- Return raw ORM models.
- Ignore exceptions.
- Duplicate business logic.
- Expose internal errors.

---

# FastAPI Philosophy

FastAPI is responsible for transport.

Services are responsible for business logic.

Repositories are responsible for persistence.

Keeping these responsibilities separate ensures the codebase remains scalable, testable, and easy to evolve as the project grows from an MVP into a production-grade AI platform.