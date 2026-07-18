# 08 — Deployment

**Project:** AI Telecaller for Hospitals (MVP)

**Version:** 1.0

**Status:** Approved

**Owner:** Platform Engineering Team

---

# 1. Purpose

This document defines the deployment architecture for the AI Telecaller MVP.

The deployment strategy prioritizes:

- Fast development
- Low operational overhead
- High availability
- Secure infrastructure
- Easy scalability
- Cost efficiency

The MVP uses managed cloud services to minimize infrastructure management while maintaining a production-ready architecture.

---

# 2. Deployment Goals

The deployment platform must provide:

- 24×7 availability
- HTTPS by default
- Automatic deployments
- Environment isolation
- Managed databases
- Easy rollback
- Horizontal scalability (future)

---

# 3. Deployment Architecture

```
                    Users

                       │

               HTTPS Requests

                       │

              Vercel (Frontend)

                       │

                 REST API

                       │

             Railway (Backend)

        ┌──────────┼──────────┐

        │          │          │

        ▼          ▼          ▼

    PostgreSQL  Pinecone   Gemini API

         │

         ▼

   Document Storage
```

---

# 4. Technology Stack

| Component | Platform |
|------------|----------|
| Frontend | Vercel |
| Backend | Railway |
| Database | PostgreSQL (Neon) |
| Vector Database | Pinecone |
| AI Model | Gemini |
| File Storage | Railway Volume / Cloud Storage |
| DNS | Cloudflare (Future) |
| Monitoring | Railway Logs |
| CI/CD | GitHub Actions |

---

# 5. Deployment Environments

Three environments should exist.

## Development

Purpose

Local development.

Characteristics

- Local PostgreSQL (optional)
- Local API
- Development API keys

---

## Staging

Purpose

Testing before production.

Characteristics

- Production-like environment
- Separate database
- Separate Pinecone index
- Separate Gemini API key

---

## Production

Purpose

Live hospital usage.

Characteristics

- HTTPS only
- Production database
- Production secrets
- Monitoring enabled

---

# 6. Frontend Deployment

Platform

Vercel

Responsibilities

- Next.js hosting
- Global CDN
- HTTPS
- Automatic deployments
- Preview deployments

Deployment flow

```
Git Push

↓

GitHub

↓

Vercel Build

↓

Production
```

---

# 7. Backend Deployment

Platform

Railway

Responsibilities

- FastAPI hosting
- Environment variables
- Persistent storage
- Logs
- Health checks

Deployment flow

```
Git Push

↓

GitHub

↓

Railway Build

↓

Deploy

↓

Health Check

↓

Live
```

---

# 8. Database Deployment

Platform

Neon PostgreSQL

Responsibilities

- Structured data
- Automatic backups
- SSL connections
- High availability

Stores

- Administrators
- Doctors
- Departments
- FAQs
- Conversations
- Audit Logs

---

# 9. Vector Database Deployment

Platform

Pinecone

Responsibilities

- Store embeddings
- Semantic search
- Context retrieval

The vector database is managed independently from PostgreSQL.

---

# 10. AI Service

Platform

Gemini API

Responsibilities

- Language generation
- Grounded responses
- Natural language understanding

The backend communicates with Gemini over HTTPS.

---

# 11. File Storage

Stores

- PDF
- DOCX
- TXT

MVP

- Railway Persistent Volume

Future

- AWS S3
- Google Cloud Storage
- Azure Blob Storage

---

# 12. Environment Variables

The following environment variables are required.

```
DATABASE_URL

JWT_SECRET

JWT_ALGORITHM

JWT_EXPIRE_MINUTES

GEMINI_API_KEY

PINECONE_API_KEY

PINECONE_INDEX

UPLOAD_DIRECTORY

MAX_UPLOAD_SIZE

APP_ENV

LOG_LEVEL
```

Secrets must never be committed to source control.

---

# 13. Build Process

Backend

```
Install Dependencies

↓

Run Tests

↓

Build Application

↓

Deploy

↓

Health Check
```

Frontend

```
Install

↓

Lint

↓

Build

↓

Deploy
```

---

# 14. Health Checks

Every deployment must expose:

```
GET /health

GET /ready

GET /live
```

These endpoints should not require authentication.

---

# 15. CI/CD Pipeline

GitHub Actions pipeline

```
Push

↓

Lint

↓

Unit Tests

↓

Security Scan

↓

Build

↓

Deploy

↓

Health Check

↓

Production
```

Deployment should stop immediately if any stage fails.

---

# 16. Rollback Strategy

If deployment fails:

1. Stop rollout
2. Restore previous deployment
3. Investigate failure
4. Redeploy after fix

The previous stable version should always remain deployable.

---

# 17. Logging

Application logs should include:

- Request ID
- API Route
- Response Time
- Errors
- Authentication Events
- AI Calls
- Escalations

Logs must not contain:

- Passwords
- JWT tokens
- API keys
- Sensitive patient information

---

# 18. Monitoring

The MVP monitors:

- CPU usage
- Memory usage
- API response time
- Error rate
- Deployment health
- Uptime

Future enhancements:

- Prometheus
- Grafana
- OpenTelemetry

---

# 19. Security During Deployment

Deployment requirements:

- HTTPS enabled
- TLS certificates
- Secret management
- Private environment variables
- Database SSL
- Secure file permissions

No secrets should be stored in code repositories.

---

# 20. Backup Strategy

PostgreSQL

- Daily automated backups
- Point-in-time recovery (where supported)

Documents

- Versioned storage

Configuration

- Environment variables backed up securely

---

# 21. Disaster Recovery

Recovery process:

1. Restore database
2. Restore document storage
3. Redeploy backend
4. Restore frontend
5. Verify health endpoints

Recovery procedures should be tested periodically.

---

# 22. Scaling Strategy

## MVP

Single backend instance.

---

## Phase 2

- Multiple backend instances
- Managed Redis cache
- Background workers

---

## Phase 3

- API Gateway
- AI Service
- RAG Service
- Worker Service

---

## Phase 4

- Kubernetes
- Auto Scaling
- Multi-region deployment
- Global CDN
- Event-driven architecture

---

# 23. Performance Targets

| Component | Target |
|-----------|--------|
| Frontend Load | <2 sec |
| API Response | <300 ms (excluding LLM) |
| AI Response | <3 sec |
| Deployment Time | <10 min |
| Health Check | <50 ms |

---

# 24. Deployment Checklist

Before production deployment:

- All tests passed
- Linting passed
- Environment variables configured
- Database migrations completed
- Health endpoints verified
- HTTPS enabled
- Security checks completed
- Backup verified
- Monitoring enabled

Deployment must not proceed if any mandatory check fails.

---

# 25. Future Infrastructure Evolution

## Phase 2

- Background job queue
- Redis
- Scheduled tasks

---

## Phase 3

- Dedicated AI service
- Dedicated RAG service
- Object storage
- CDN

---

## Phase 4

- Kubernetes
- Service Mesh
- Multi-region deployment
- Blue/Green deployments
- Canary releases
- Infrastructure as Code (Terraform)

---

# 26. Architectural Decisions

| Decision | Reason |
|----------|--------|
| Vercel | Optimized Next.js hosting |
| Railway | Simple backend deployment |
| Neon PostgreSQL | Managed relational database |
| Pinecone | Managed vector search |
| Gemini | Managed LLM service |
| GitHub Actions | Automated CI/CD |
| Managed Services | Lower operational overhead |

---

# 27. Deployment Principles

Every deployment must be:

- Repeatable
- Automated
- Observable
- Secure
- Versioned
- Recoverable
- Tested
- Documented

Manual production deployments should be avoided whenever possible.

---

# 28. Summary

The deployment architecture is intentionally lightweight, leveraging managed cloud services to deliver a secure and reliable AI application with minimal operational complexity.

Key characteristics include:

- Managed infrastructure
- Automated deployments
- Secure secret management
- Production-ready HTTPS
- Independent frontend and backend deployments
- Managed relational and vector databases
- CI/CD with automated validation
- Clear migration path toward a scalable, multi-service SaaS platform