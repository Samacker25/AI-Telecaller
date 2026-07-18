# 05 — Database Schema

**Project:** AI Telecaller for Hospitals (MVP)

**Version:** 1.0

**Status:** Approved

**Owner:** Database Architecture Team

---

# 1. Purpose

This document defines the relational database schema for the AI Telecaller MVP.

The database stores operational and business data required by the application.

Knowledge retrieval is intentionally separated into a vector database (Pinecone). PostgreSQL stores only structured metadata and application state.

---

# 2. Design Principles

The schema follows these principles.

## Normalize First

Avoid duplicated information.

---

## AI-Aware

Store metadata required by the AI pipeline.

Do **not** store embeddings in PostgreSQL.

---

## Auditability

Important operations should be traceable.

---

## Extensibility

Support future SaaS multi-tenancy without redesign.

---

## Soft Deletes

Business records should support logical deletion where appropriate.

---

# 3. Storage Architecture

```
                    Application

                          │

        ┌─────────────────┴─────────────────┐

        │                                   │

        ▼                                   ▼

 PostgreSQL                         Pinecone Vector DB

 Operational Data                 Semantic Embeddings

        │                                   │

 Users                             Document Chunks

 Doctors                           Semantic Search

 Conversations                     Similarity Search

 Documents Metadata                Context Retrieval
```

---

# 4. Database Overview

The MVP uses PostgreSQL for:

- Authentication
- Hospital data
- Doctor information
- Departments
- FAQs
- Conversation history
- Uploaded document metadata
- Audit information

---

# 5. Entity Relationship Overview

```
Hospital
    │
    ├────────────┐
    │            │
    ▼            ▼

Department     Doctor

    │

    ▼

FAQ

    │

    ▼

Document

    │

    ▼

Conversation

    │

    ▼

Message

Administrator
```

---

# 6. Core Tables

## users

Purpose

Stores administrator and staff accounts. The first registered user becomes the admin; later users default to the staff role.

Fields

| Field | Type |
|---------|------|
| id | UUID |
| name | VARCHAR |
| email | VARCHAR |
| password_hash | TEXT |
| role | VARCHAR |
| is_active | BOOLEAN |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |

Indexes

- email

---

## hospitals

Purpose

Stores hospital information.

Fields

| Field | Type |
|---------|------|
| id | UUID |
| name | VARCHAR |
| address | TEXT |
| phone | VARCHAR |
| email | VARCHAR |
| website | VARCHAR |
| created_at | TIMESTAMP |

Future versions support multiple hospitals (multi-tenancy).

---

## departments

Purpose

Stores hospital departments.

Fields

| Field | Type |
|---------|------|
| id | UUID |
| hospital_id | UUID |
| name | VARCHAR |
| description | TEXT |
| created_at | TIMESTAMP |

Relationship

Hospital

↓

Departments

---

## doctors

Purpose

Stores doctor information.

Fields

| Field | Type |
|---------|------|
| id | UUID |
| hospital_id | UUID |
| department_id | UUID |
| name | VARCHAR |
| specialization | VARCHAR |
| qualification | VARCHAR |
| opd_schedule | JSONB |
| is_available | BOOLEAN |
| created_at | TIMESTAMP |

Relationship

Hospital

↓

Department

↓

Doctor

---

## faqs

Purpose

Stores manually curated FAQ entries.

Fields

| Field | Type |
|---------|------|
| id | UUID |
| hospital_id | UUID |
| question | TEXT |
| answer | TEXT |
| category | VARCHAR |
| is_active | BOOLEAN |
| created_at | TIMESTAMP |

---

## documents

Purpose

Stores uploaded knowledge documents.

Fields

| Field | Type |
|---------|------|
| id | UUID |
| hospital_id | UUID |
| file_name | VARCHAR |
| file_type | VARCHAR |
| storage_path | TEXT |
| status | VARCHAR |
| uploaded_by | UUID |
| created_at | TIMESTAMP |

Status values

- Uploaded
- Processing
- Indexed
- Failed

---

## conversations

Purpose

Stores AI conversations.

Fields

| Field | Type |
|---------|------|
| id | UUID |
| session_id | UUID |
| hospital_id | UUID |
| channel | VARCHAR |
| escalation | BOOLEAN |
| created_at | TIMESTAMP |

Channels

- Chat
- Voice (Future)

---

## messages

Purpose

Stores conversation messages.

Fields

| Field | Type |
|---------|------|
| id | UUID |
| conversation_id | UUID |
| sender | VARCHAR |
| message | TEXT |
| response_time_ms | INTEGER |
| confidence_score | DECIMAL |
| created_at | TIMESTAMP |

Sender values

- User
- AI
- Human

---

## audit_logs

Purpose

Stores administrative activities.

Fields

| Field | Type |
|---------|------|
| id | UUID |
| administrator_id | UUID |
| action | VARCHAR |
| entity | VARCHAR |
| entity_id | UUID |
| metadata | JSONB |
| created_at | TIMESTAMP |

Examples

- Upload Document
- Delete FAQ
- Login
- Reindex Knowledge

---

# 7. Relationships

```
Hospital

├── Departments

├── Doctors

├── FAQs

├── Documents

└── Conversations

Conversation

└── Messages

Administrator

└── Audit Logs
```

---

# 8. Conversation Model

```
Conversation

↓

Multiple Messages

↓

AI Context

↓

Stored History
```

Only conversation history required for the active session is retrieved during inference.

---

# 9. Document Metadata

PostgreSQL stores only metadata.

Example

```
Document ID

↓

File Name

↓

Upload Time

↓

Status

↓

Storage Location
```

Document text is processed into embeddings and stored in Pinecone.

---

# 10. Vector Database

The vector database stores:

- Chunk ID
- Document ID
- Embedding
- Metadata
- Chunk Text

This data is intentionally separated from PostgreSQL.

---

# 11. Indexing Strategy

Recommended indexes.

## administrators

- email

---

## doctors

- hospital_id
- department_id
- specialization

---

## departments

- hospital_id

---

## faqs

- hospital_id
- category

---

## documents

- hospital_id
- status

---

## conversations

- hospital_id
- session_id

---

## messages

- conversation_id

---

# 12. Data Lifecycle

```
Upload

↓

Metadata Saved

↓

Document Processed

↓

Embeddings Generated

↓

Indexed

↓

Available for Retrieval
```

---

# 13. Retention Policy

| Data | Retention |
|---------|-----------|
| Conversation History | Configurable |
| Audit Logs | Long-term |
| Documents | Until Deleted |
| FAQs | Permanent |
| Doctors | Active Records |
| Departments | Permanent |

---

# 14. Performance Considerations

The schema is optimized for:

- Fast lookup
- Minimal joins
- Read-heavy workloads
- AI conversation history
- Metadata retrieval

Large document content is never stored inside operational tables.

---

# 15. Security

Sensitive fields include:

- Password Hash
- Email
- Conversation History

Requirements

- Hash passwords
- Encrypt connections
- Parameterized queries
- Principle of least privilege
- Row-level authorization (future)

---

# 16. Backup Strategy

Database backups

- Daily backup
- Point-in-time recovery (if supported)
- Versioned document storage

Vector database backups follow provider capabilities.

---

# 17. Future Schema Evolution

## Phase 2

New tables

- appointments
- call_logs
- notifications

---

## Phase 3

New tables

- ai_agents
- workflows
- integrations
- calendars
- crm_connections

---

## Phase 4

New tables

- tenants
- subscriptions
- billing
- roles
- permissions

---

# 18. Architectural Decisions

| Decision | Reason |
|----------|--------|
| PostgreSQL | Reliable relational storage |
| UUID Primary Keys | Distributed-friendly |
| JSONB for Schedules | Flexible structure |
| Separate Vector DB | Better semantic search |
| Metadata in PostgreSQL | Faster management |
| Soft Deletes | Data recovery and auditing |

---

# 19. Database Principles

The database should always follow these principles:

- Normalize operational data
- Keep embeddings outside PostgreSQL
- Store metadata separately from AI vectors
- Use UUIDs for identifiers
- Prefer immutable audit records
- Optimize for reads
- Avoid premature denormalization
- Design for future multi-tenancy

---

# 20. Summary

The MVP database architecture separates operational data from AI knowledge storage.

Key characteristics include:

- PostgreSQL for structured application data
- Pinecone for semantic search
- UUID-based entities
- Audit-ready design
- Extensible schema for future SaaS growth
- Minimal, maintainable relational model optimized for an AI-first hospital assistant