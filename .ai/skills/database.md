# Database Skill

## Purpose

This document defines the database design, implementation, and operational standards for the AI Telecaller project.

The primary goals are:

- Data integrity
- Performance
- Security
- Maintainability
- Scalability
- Future SaaS compatibility

These rules apply to PostgreSQL, SQLAlchemy, Alembic, and future database evolution.

---

# Database Principles

The database is the single source of truth for all operational data.

Always prioritize:

- Data consistency
- Referential integrity
- Normalization
- Explicit relationships
- Safe migrations
- Efficient queries

Avoid premature denormalization.

---

# Database Technologies

Current stack:

- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- AsyncPG

Future:

- Read replicas
- Partitioning
- Multi-tenant architecture

---

# Responsibilities

## PostgreSQL

Stores:

- Users
- Hospitals
- Doctors
- Departments
- FAQs
- Documents
- Conversations
- Messages
- Audit Logs

Never store embeddings in PostgreSQL.

---

## Pinecone

Stores only:

- Embeddings
- Vector metadata
- Semantic search indexes

Never store business data inside Pinecone.

---

# Architecture

Always follow:

```

API

↓

Service

↓

Repository

↓

SQLAlchemy

↓

PostgreSQL

```

Business logic must never exist inside repositories.

---

# Repository Pattern

Each entity should have its own repository.

Example:

```

repositories/

doctor_repository.py

department_repository.py

faq_repository.py

document_repository.py

conversation_repository.py

```

Repositories should only:

- Create
- Read
- Update
- Delete
- Query

Nothing else.

---

# Service Layer

Services coordinate:

- Multiple repositories
- Validation
- Transactions
- AI operations
- External APIs

Repositories must never call services.

---

# SQLAlchemy Standards

Use:

- SQLAlchemy 2.x
- AsyncSession
- Declarative models
- Explicit relationships

Avoid legacy SQLAlchemy APIs.

---

# Model Design

Models should contain:

- Table definition
- Relationships
- Constraints

Avoid:

- Business logic
- External API calls
- AI logic
- Validation logic

---

# Primary Keys

Use UUIDs for all primary entities.

Example:

- User
- Hospital
- Doctor
- Conversation
- Document

Avoid sequential IDs for externally exposed resources.

---

# Foreign Keys

Always define foreign keys explicitly.

Enable referential integrity.

Use cascading deletes only when appropriate.

Never delete important historical data automatically.

---

# Constraints

Use database constraints whenever possible.

Examples:

- UNIQUE
- NOT NULL
- CHECK
- FOREIGN KEY

Do not rely only on application validation.

---

# Indexing

Create indexes for:

- Foreign keys
- Frequently filtered columns
- Frequently searched columns

Examples:

- email
- hospital_id
- created_at
- updated_at

Avoid unnecessary indexes.

Every index increases write cost.

---

# Naming Conventions

Tables:

snake_case

Example:

```

hospital_departments

```

Columns:

snake_case

Example:

```

created_at

updated_at

doctor_name

```

Primary key:

```

id

```

Foreign key:

```

hospital_id

```

Boolean:

```

is_active

is_deleted

```

Timestamp:

```

created_at

updated_at

```

---

# Soft Delete

Prefer soft delete for important entities.

Example:

```

is_deleted

deleted_at

```

Never permanently remove:

- Conversations
- Audit Logs
- Uploaded Documents

unless explicitly required.

---

# Timestamps

Every important table should include:

```

created_at

updated_at

```

Future:

```

deleted_at

```

Use UTC.

---

# Transactions

Keep transactions:

- Small
- Atomic
- Predictable

Rollback on failure.

Never leave partial updates.

---

# Async Database Access

Always use:

AsyncSession

Avoid synchronous database operations.

---

# Query Design

Prefer:

- Explicit joins
- Pagination
- Filtering
- Ordering

Avoid:

- SELECT *
- N+1 queries
- Loading unnecessary relationships

---

# Pagination

Every collection endpoint should support:

```

limit

offset

```

Future:

Cursor pagination.

---

# Bulk Operations

Use bulk operations carefully.

Validate data before writing.

Keep transactions manageable.

---

# Migrations

Use Alembic.

Never modify production schema manually.

Every schema change requires:

- Migration
- Review
- Testing

Migration history must remain linear.

---

# Seed Data

Seed only:

- Default administrator
- Example hospital
- Initial departments
- Initial FAQs

Never seed production secrets.

---

# Environment Separation

Maintain separate databases for:

Development

Testing

Production

Never share production data with development.

---

# Validation

Validate data in two places:

Application layer

+

Database constraints

Never depend on only one layer.

---

# Relationships

Prefer explicit relationships.

Example:

Hospital

↓

Department

↓

Doctor

↓

Conversation

Avoid unnecessary many-to-many relationships.

---

# Concurrency

Assume multiple concurrent users.

Avoid race conditions.

Use transactions where consistency matters.

---

# Performance

Optimize by:

- Indexing
- Efficient queries
- Async I/O
- Query profiling

Never optimize blindly.

Measure first.

---

# Security

Never expose:

- Internal IDs unnecessarily
- Database errors
- SQL queries
- Connection strings

Always use parameterized queries.

Never build SQL using string concatenation.

---

# Backup Strategy

Future production requirements:

- Automated backups
- Point-in-time recovery
- Backup verification
- Disaster recovery testing

---

# Multi-Tenant Readiness

Current MVP supports one hospital.

However, design entities so future tenant support is simple.

Prefer including:

```

hospital_id

```

on business entities where appropriate.

Avoid hardcoding assumptions that only one hospital exists.

---

# Audit Logging

Critical operations should be auditable.

Examples:

- Login
- Document upload
- FAQ changes
- Doctor updates
- Permission changes

Audit logs should be append-only.

---

# Testing

Database changes require:

- Migration tests
- Repository tests
- Transaction tests
- Constraint validation
- Performance verification

Never merge untested schema changes.

---

# Definition of Done

Database work is complete only if:

- Models are implemented.
- Relationships are correct.
- Constraints are defined.
- Migrations are created.
- Repository methods are tested.
- Queries are optimized.
- Indexes are reviewed.
- Documentation is updated.

---

# Anti-Patterns

Never:

- Put business logic in models.
- Query the database directly from routes.
- Skip migrations.
- Store embeddings in PostgreSQL.
- Store operational data in Pinecone.
- Disable constraints for convenience.
- Ignore transaction failures.
- Hardcode SQL strings.

---

# Database Philosophy

PostgreSQL is the authoritative source for operational data.

Repositories manage persistence.

Services manage business logic.

The database should remain clean, consistent, secure, and scalable, enabling seamless evolution from a single-hospital MVP to a future multi-tenant SaaS platform without major architectural changes.