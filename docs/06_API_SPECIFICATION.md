# 06 — API Specification

**Project:** AI Telecaller for Hospitals (MVP)

**Version:** 1.0

**Status:** Approved

**Owner:** API Architecture Team

---

# 1. Purpose

This document defines the REST API contract for the AI Telecaller MVP.

The API enables communication between:

- Website Chatbot
- Admin Dashboard
- AI Service
- Knowledge Management
- Future Voice Telecaller
- Future Mobile Applications

The API is designed to be stable, versioned, secure, and extensible.

---

# 2. API Design Principles

The API follows these principles.

## REST First

Use standard REST semantics.

---

## Resource-Oriented

Endpoints represent business resources rather than actions.

---

## Stateless

Every request contains all required information.

---

## JSON Only

All request and response bodies use JSON unless uploading files.

---

## Versioned

Every public endpoint includes an API version.

Example

```
/api/v1/
```

---

## Predictable

Consistent:

- Naming
- Status Codes
- Error Responses
- Pagination
- Authentication

---

# 3. Base URL

Development

```
http://localhost:8000/api/v1
```

Production

```
https://api.example.com/api/v1
```

---

# 4. Authentication

Public APIs

No authentication required.

Examples

- Chat
- Hospital Information

---

Protected APIs

Require JWT.

Examples

- Admin Login
- Document Upload
- FAQ Management

Authorization Header

```
Authorization: Bearer <JWT_TOKEN>
```

---

# 5. Content Types

Request

```
application/json
```

File Upload

```
multipart/form-data
```

Response

```
application/json
```

---

# 6. API Modules

The API is organized into the following domains.

```
/auth

/chat

/conversations

/documents

/faqs

/hospitals

/doctors

/departments

/admin

/health
```

---

# 7. Authentication APIs

## Register

```
POST /auth/register
```

Purpose

Create a dashboard account. The first registered account becomes the admin; later accounts are staff.

Request

```json
{
  "name": "Admin",
  "email": "admin@hospital.com",
  "password": "min-8-characters"
}
```

Response — `201 Created`

```json
{
  "id": "uuid",
  "name": "Admin",
  "email": "admin@hospital.com",
  "role": "admin",
  "is_active": true,
  "created_at": "..."
}
```

Errors: `409` if the email is already registered.

---

## Login

```
POST /auth/login
```

Purpose

Authenticate administrator.

Request

```json
{
  "email": "admin@hospital.com",
  "password": "********"
}
```

Response

```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

---

## Current User

```
GET /auth/me
```

Returns authenticated administrator.

---

## List Users

```
GET /auth/users
```

Returns all accounts. Requires the admin role; staff receive `403`.

---

## Logout

```
POST /auth/logout
```

Invalidates current session.

---

# 8. Chat APIs

## Send Message

```
POST /chat
```

Purpose

Send a patient message to the AI assistant.

Request

```json
{
  "session_id": "uuid",
  "message": "What are the OPD timings?"
}
```

Response

```json
{
  "answer": "...",
  "confidence": 0.96,
  "escalation": false
}
```

---

## Reset Conversation

```
POST /chat/reset
```

Clears current conversation context.

---

## Conversation History

```
GET /conversations/{conversation_id}
```

Returns complete message history.

---

# 9. Document APIs

## Upload Document

```
POST /documents
```

Authentication

Required

Supported

- PDF
- DOCX
- TXT

Response

```json
{
  "document_id": "...",
  "status": "processing"
}
```

---

## List Documents

```
GET /documents
```

Returns uploaded documents.

---

## Document Details

```
GET /documents/{id}
```

---

## Delete Document

```
DELETE /documents/{id}
```

---

## Reindex Document

```
POST /documents/{id}/reindex
```

Triggers embedding regeneration.

---

# 10. FAQ APIs

## List FAQs

```
GET /faqs
```

---

## Create FAQ

```
POST /faqs
```

---

## Update FAQ

```
PUT /faqs/{id}
```

---

## Delete FAQ

```
DELETE /faqs/{id}
```

---

# 11. Hospital APIs

The MVP supports a single hospital profile. Reads are public; writes are admin-only.

## List Hospitals

```
GET /hospitals
```

## Create Hospital

```
POST /hospitals
```

Admin only. Returns `409` if a hospital profile already exists.

## Hospital Details

```
GET /hospitals/{id}
```

## Update Hospital

```
PUT /hospitals/{id}
```

Admin only. Partial update; omitted fields are unchanged.

## Hospital Settings

```
GET /hospitals/{id}/settings
PUT /hospitals/{id}/settings
```

Settings include weekly working hours, emergency contact, and escalation email. `GET` requires authentication; `PUT` is admin-only. Working hours are validated (end after start, no overlapping slots).

---

# 12. Doctor APIs

Reads are public; writes are admin-only.

## List Doctors

```
GET /doctors
```

Optional Filters (query parameters)

- department_id
- specialization (case-insensitive)
- available

---

## Doctor Details

```
GET /doctors/{id}
```

---

## Create Doctor

```
POST /doctors
```

Admin only. Requires an existing `department_id`. Accepts an optional `opd_schedule` (validated weekly working hours).

---

## Update Doctor

```
PUT /doctors/{id}
```

Admin only. Partial update; moving a doctor requires a valid `department_id`.

---

## Delete Doctor

```
DELETE /doctors/{id}
```

Admin only.

---

# 13. Department APIs

Reads are public; writes are admin-only.

## List Departments

```
GET /departments
```

---

## Department Details

```
GET /departments/{id}
```

---

## Create Department

```
POST /departments
```

Admin only. Department names are unique per hospital (case-insensitive); duplicates return `409`.

---

## Update Department

```
PUT /departments/{id}
```

Admin only.

---

## Delete Department

```
DELETE /departments/{id}
```

Admin only. Returns `409` if the department still has doctors.

---

# 14. Admin APIs

## Dashboard Summary

```
GET /admin/dashboard
```

Returns

- Document Count
- Conversation Count
- FAQ Count
- AI Usage

---

## Audit Logs

```
GET /admin/audit
```

---

# 15. Health APIs

## Health Check

```
GET /health
```

---

## Readiness

```
GET /ready
```

---

## Liveness

```
GET /live
```

---

# 16. Standard Success Response

```json
{
  "success": true,
  "data": {}
}
```

---

# 17. Standard Error Response

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Requested resource was not found."
  }
}
```

---

# 18. HTTP Status Codes

| Status | Meaning |
|----------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 413 | Payload Too Large |
| 415 | Unsupported Media Type |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

# 19. Validation Rules

Examples

Chat Message

- Required
- Max Length: 2000

Email

- RFC compliant

Password

- Minimum length

Uploaded Files

- Allowed formats only
- Maximum file size configurable

---

# 20. Pagination

Collection endpoints support pagination.

Example

```
GET /documents?page=1&page_size=20
```

Response

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 145
}
```

---

# 21. Filtering

Supported where appropriate.

Example

```
GET /doctors?department=Cardiology
```

---

# 22. Sorting

Example

```
GET /documents?sort=created_at&order=desc
```

---

# 23. Security

API protections include:

- JWT Authentication
- HTTPS
- Input Validation
- Output Encoding
- Rate Limiting
- File Validation
- Prompt Injection Protection
- Request Logging

See

`07_SECURITY.md`

---

# 24. Idempotency

Safe methods

```
GET
PUT
DELETE
```

should be idempotent.

POST operations that create resources should support idempotency keys if future integrations require them.

---

# 25. API Versioning Strategy

Current

```
/api/v1
```

Future versions

```
/api/v2
/api/v3
```

Breaking changes require a new API version.

---

# 26. Future APIs

Phase 2

```
/voice

/calls

/appointments
```

---

Phase 3

```
/agents

/workflows

/integrations

/calendars

/notifications
```

---

Phase 4

```
/tenants

/billing

/analytics

/subscriptions
```

---

# 27. Performance Targets

| API | Target |
|------|---------|
| Health | <50 ms |
| Login | <200 ms |
| Chat (excluding LLM) | <300 ms |
| Retrieval | <500 ms |
| Document Upload | <30 sec |
| Dashboard | <500 ms |

---

# 28. API Governance

Every API must:

- Be documented
- Be versioned
- Return consistent responses
- Validate input
- Produce structured errors
- Be observable through logs
- Include automated tests
- Follow semantic versioning

---

# 29. OpenAPI Specification

The backend should automatically generate an OpenAPI 3.1 specification.

FastAPI provides:

- `/docs` (Swagger UI)
- `/redoc` (ReDoc)
- `/openapi.json`

This specification serves as the single source of truth for client generation and integration testing.

---

# 30. Architectural Decisions

| Decision | Reason |
|----------|--------|
| REST APIs | Simplicity and broad compatibility |
| JWT Authentication | Stateless security |
| Versioned Endpoints | Backward compatibility |
| JSON Payloads | Standard interoperability |
| OpenAPI | Automatic API documentation |
| Domain-Based Routing | Clear ownership and maintainability |

---

# 31. Summary

The API architecture is designed to provide a stable, secure, and scalable contract between all application components.

Key characteristics include:

- RESTful design
- Versioned endpoints
- JWT-protected administration
- Shared APIs for chat and future voice channels
- Consistent request and response formats
- Automatic OpenAPI documentation
- Extensible domain-based routing for future SaaS evolution