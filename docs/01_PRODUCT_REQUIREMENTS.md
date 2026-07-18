# 01 — Product Requirements Document (PRD)

**Project:** AI Telecaller for Hospitals (MVP)

**Document Version:** 1.0

**Status:** Approved for MVP Development

**Owner:** Product Management

**Stakeholders:** Engineering, AI/ML, Backend, Frontend, Hospital Operations, IT Administration

**Last Updated:** YYYY-MM-DD

---

# 1. Executive Summary

AI Telecaller is an AI-powered virtual hospital receptionist that answers patient queries using a Retrieval-Augmented Generation (RAG) knowledge base and seamlessly transfers conversations to human staff whenever AI cannot confidently assist.

The MVP focuses on validating the core product hypothesis:

> **Can an AI receptionist successfully automate the majority of repetitive hospital inquiries while maintaining patient trust and providing a seamless fallback to human staff?**

The same backend services will power both:

- AI Website Chatbot
- AI Voice Telecaller

This shared architecture minimizes maintenance cost while maximizing knowledge reuse.

---

# 2. Background

Hospital reception departments spend a significant amount of time answering repetitive questions, including:

- Doctor availability
- OPD timings
- Hospital departments
- Diagnostic packages
- Visiting hours
- Hospital address
- Contact information
- General FAQs

These repetitive conversations increase operational costs and reduce staff productivity.

The goal is not to replace hospital staff but to automate repetitive interactions and allow employees to focus on higher-value patient care.

---

# 3. Problem Statement

Current hospital communication has several limitations:

- Reception staff are only available during working hours.
- Patients experience long waiting times.
- Staff repeatedly answer the same questions.
- Information may be inconsistent across employees.
- Peak-hour call volume overwhelms reception desks.
- Website FAQs become outdated and are difficult to maintain.

The hospital requires an intelligent assistant that provides consistent, accurate, and available responses 24×7.

---

# 4. Vision

Build an AI-powered hospital receptionist capable of handling patient inquiries across voice and chat channels while maintaining enterprise-grade security, reliability, and scalability.

Long-term vision:

> A multi-tenant SaaS platform enabling hospitals to deploy an AI receptionist without maintaining their own AI infrastructure.

---

# 5. Product Goals

## Primary Goals

- Provide 24×7 patient assistance.
- Reduce receptionist workload.
- Improve patient response time.
- Deliver consistent information.
- Support both voice and chat using a shared backend.
- Enable seamless transfer to human staff.

---

## Business Goals

- Validate product-market fit.
- Deploy successfully in one hospital.
- Measure operational improvements.
- Build the foundation for a SaaS platform.

---

## Technical Goals

- Modular backend architecture.
- Production-ready RAG pipeline.
- Easy knowledge base updates.
- Low infrastructure cost.
- Cloud-native deployment.

---

# 6. Target Users

## Primary Users

### Patients

Need quick answers regarding:

- Doctors
- Departments
- Hospital services
- OPD schedules
- Contact details

---

### Patient Attendants

Need:

- Visiting rules
- Billing information
- Diagnostic services
- Hospital facilities

---

### Hospital Reception Staff

Need:

- Reduced repetitive workload
- Easy escalation handling
- Accurate AI responses

---

### Hospital Administrator

Need:

- Upload documents
- Update knowledge base
- Monitor AI performance

---

# 7. Success Metrics

The MVP will be considered successful if it achieves the following objectives.

| Metric | Target |
|---------|---------|
| FAQ Accuracy | ≥90% |
| Retrieval Accuracy | ≥90% |
| Average Response Time | <3 seconds |
| Human Escalation Success | 100% |
| System Availability | ≥95% |
| Failed Queries | <10% |
| Deployment Success | 1 Production Hospital |

---

# 8. MVP Scope

## Included

### AI Chatbot

- Natural language conversations
- Context-aware responses
- Session history

---

### RAG Knowledge Base

Retrieve information from:

- FAQs
- Doctor list
- Departments
- Packages
- Hospital policies
- Contact information
- PDF documents

---

### Knowledge Base Management

- Upload PDF
- Upload DOCX
- Upload TXT
- Automatic indexing
- Embedding generation
- Semantic search

---

### Human Escalation

Transfer conversations when:

- AI confidence is low
- User requests human assistance
- AI cannot retrieve relevant information

---

### Basic Admin Panel

- Upload documents
- Re-index knowledge
- Manage FAQs
- View conversations

---

### Deployment

Cloud deployment using managed infrastructure.

---

# 9. Out of Scope

The following capabilities will NOT be implemented in the MVP.

## Voice Calling

Voice integration is planned after validating chatbot performance.

---

## Appointment Booking

Deferred.

---

## Payment Processing

Deferred.

---

## WhatsApp Integration

Deferred.

---

## Email Automation

Deferred.

---

## Multi-language Support

Deferred.

---

## Analytics Dashboard

Deferred.

---

## SaaS Multi-Tenancy

Deferred.

---

## CRM Integration

Deferred.

---

## Agentic AI

Deferred.

---

## Voice Analytics

Deferred.

---

## Fine-Tuned Models

Deferred.

---

# 10. Functional Requirements

## Authentication

The system shall:

- authenticate administrators
- authorize API requests
- secure endpoints using JWT

---

## AI Chat

The system shall:

- accept user questions
- retrieve relevant knowledge
- generate grounded responses
- maintain conversation context

---

## Knowledge Base

The system shall:

- upload documents
- generate embeddings
- update vector database
- delete obsolete knowledge

---

## Search

The system shall:

- perform semantic search
- return Top-K relevant chunks
- support metadata filtering

---

## Administration

Administrator shall be able to:

- upload files
- delete files
- rebuild embeddings
- manage FAQs

---

# 11. Non-Functional Requirements

## Availability

Minimum availability:

95%

---

## Performance

Average response time:

<3 seconds

---

## Scalability

Support future migration to:

- Multiple hospitals
- Multiple AI models
- Horizontal scaling

---

## Security

- HTTPS
- JWT
- Secure Secrets
- Rate Limiting
- Prompt Injection Protection

---

## Reliability

Graceful degradation if:

- Vector DB unavailable
- AI model unavailable
- Retrieval fails

---

# 12. User Journey

## Chatbot Flow

```text
Patient

↓

Open Chat

↓

Ask Question

↓

Retrieve Context

↓

Generate Response

↓

Confidence Check

↓

High Confidence?

├── Yes → Respond
│
└── No → Human Escalation
```

---

# 13. Business Rules

The AI must:

- Never fabricate information.
- Never provide medical diagnosis.
- Never prescribe medicine.
- Never guess unavailable information.
- Always use retrieved knowledge.
- Escalate when uncertain.
- Inform users when information is unavailable.

---

# 14. Assumptions

- Hospital provides accurate knowledge documents.
- Internet connectivity is available.
- AI model API remains operational.
- Administrators maintain updated documentation.

---

# 15. Risks

| Risk | Impact | Mitigation |
|--------|---------|------------|
| Hallucination | High | Strict RAG grounding |
| Outdated documents | Medium | Easy document updates |
| AI downtime | High | Retry + graceful fallback |
| Poor retrieval | High | Improve chunking and embeddings |
| Prompt Injection | High | Input validation and prompt protection |

---

# 16. Dependencies

External services:

- Gemini API
- Pinecone
- PostgreSQL
- Redis
- Railway
- Vercel

Future:

- Twilio
- Deepgram
- ElevenLabs

---

# 17. Release Criteria

The MVP can be released when:

- All core APIs pass testing.
- RAG retrieval accuracy meets target.
- Security checklist is completed.
- Deployment is successful.
- Hospital knowledge base is indexed.
- Human escalation works correctly.
- User Acceptance Testing (UAT) is approved.

---

# 18. Future Roadmap

## Phase 2

- Voice Telecaller
- Call Routing
- Appointment Booking
- Call Recording
- Analytics

---

## Phase 3

- Agentic AI
- WhatsApp
- Email
- Calendar Integration
- AI Workflow Automation
- Hospital CRM Integration

---

## Phase 4

- Multi-Hospital SaaS
- Tenant Isolation
- Billing
- Monitoring
- Role-Based Access Control

---

# 19. Definition of Success

The MVP is successful if:

- Patients receive fast and accurate answers.
- Hospital staff experience a measurable reduction in repetitive inquiries.
- The system operates reliably in production.
- The architecture is validated as a reusable foundation for future SaaS expansion.
- The product demonstrates clear value to support broader deployment across additional hospitals.