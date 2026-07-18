# 🏥 AI Telecaller for Hospitals (MVP)

> An AI-powered 24×7 virtual receptionist for hospitals that answers patient queries using Retrieval-Augmented Generation (RAG), seamlessly escalates complex conversations to human staff, and serves as the foundation for a multi-tenant SaaS platform.

---

## 📖 Overview

Hospital reception desks receive hundreds of repetitive calls every day regarding doctor availability, OPD timings, appointments, packages, reports, hospital facilities, insurance, and general inquiries. These repetitive interactions increase operational costs, extend patient waiting times, and reduce staff productivity.

This project aims to build a production-ready Minimum Viable Product (MVP) that automates these repetitive conversations using Generative AI while ensuring patients can always be transferred to a human representative whenever necessary.

The same AI backend is designed to power both:

- 📞 AI Voice Telecaller
- 💬 Hospital Website Chatbot

By sharing the same Retrieval-Augmented Generation (RAG) knowledge base, hospitals only maintain information in one place.

---

# 🎯 Project Goals

The MVP focuses on validating three core assumptions:

- AI can accurately answer hospital-related questions.
- AI can retrieve information from hospital documents with high accuracy.
- AI can safely transfer conversations to human staff when required.

The objective is **not** to replace hospital employees entirely, but to automate repetitive interactions and allow staff to focus on higher-value patient care.

---

# 🚀 MVP Features

## Patient FAQ Assistant

- Hospital information
- Doctor list
- Department information
- OPD schedule
- Visiting hours
- Contact information
- Emergency numbers

---

## AI Chatbot

- Natural language conversations
- Context-aware responses
- Multi-turn conversations
- Session history

---

## Retrieval-Augmented Generation (RAG)

Retrieve answers from hospital knowledge base including:

- FAQs
- Doctor database
- Hospital policies
- OPD schedule
- Medical packages
- Services
- Documents
- PDF files

---

## Knowledge Base Management

- Upload documents
- Automatic indexing
- Embedding generation
- Semantic search
- Knowledge updates

---

## Human Escalation

Transfer conversations when:

- AI confidence is low
- User explicitly requests human support
- Emergency situations
- Unsupported queries

---

## Admin Panel (Basic)

- Upload documents
- Manage FAQs
- View conversations
- Rebuild search index

---

# ❌ Out of Scope (MVP)

The following features are intentionally excluded from the MVP:

- Appointment booking
- WhatsApp integration
- Payment gateway
- Multi-language support
- Voice cloning
- CRM integration
- Billing system
- Analytics dashboard
- Multi-hospital SaaS
- Fine-tuned LLMs
- Agentic AI workflows
- Multi-agent orchestration

These will be introduced after validating the MVP.

---

# 🏗 High-Level Architecture

```text
                  Phone Call / Website Chat

                          │

                ┌─────────▼─────────┐
                │ API Gateway       │
                └─────────┬─────────┘
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼

 Voice Service      Chat Service      Admin Service

        │                 │
        └──────────┬──────┘
                   ▼

             AI Service

                   │

            RAG Pipeline

       ┌───────────┼───────────┐

       ▼           ▼           ▼

 PostgreSQL    Vector DB    Document Store
```

---

# 🧠 AI Workflow

1. Patient asks a question.
2. Query is converted into embeddings.
3. Relevant knowledge is retrieved.
4. Retrieved context is injected into the prompt.
5. LLM generates an answer.
6. AI confidence is evaluated.
7. If confidence is acceptable:

   - Respond to patient.

8. Otherwise:

   - Escalate to a human operator.

---

# 🛠 Tech Stack

## Frontend

- Next.js
- TypeScript
- Tailwind CSS

---

## Backend

- FastAPI
- Python
- AsyncIO

---

## AI

- Gemini
- LangChain
- LangGraph (Future)
- RAG

---

## Vector Database

- Pinecone

---

## Database

- PostgreSQL

---

## Cache

- Redis

---

## File Storage

- Local Storage (MVP)

Future:

- AWS S3

---

## Voice (Future MVP Extension)

- Twilio
- Deepgram
- ElevenLabs

---

## Deployment

Frontend

- Vercel

Backend

- Railway

Database

- Neon PostgreSQL

Redis

- Upstash

Vector Database

- Pinecone

---

# 📂 Project Structure

```text
ai-telecaller/

├── backend/
│
├── frontend/
│
├── docs/
│
├── knowledge_base/
│
├── scripts/
│
├── tests/
│
├── docker/
│
├── README.md
├── CLAUDE.md
└── .env.example
```

---

# 📄 Documentation

| Document | Purpose |
|-----------|---------|
| README.md | Project overview |
| CLAUDE.md | AI engineering guidelines |
| PRODUCT_REQUIREMENTS.md | Product scope |
| SYSTEM_ARCHITECTURE.md | Overall architecture |
| BACKEND_ARCHITECTURE.md | Backend design |
| AI_RAG_ARCHITECTURE.md | RAG implementation |
| DATABASE_SCHEMA.md | Database design |
| API_SPECIFICATION.md | REST APIs |
| SECURITY.md | Security practices |
| DEPLOYMENT.md | Deployment guide |
| TEST_PLAN.md | Testing strategy |
| ROADMAP.md | Product roadmap |

---

# 🔒 Security Principles

The MVP follows secure-by-default engineering principles.

- JWT Authentication
- HTTPS only
- Environment variables
- Prompt injection protection
- Input validation
- Rate limiting
- Secure document uploads
- Audit logging
- Principle of least privilege

---

# 📈 Success Metrics

The MVP will be considered successful if it achieves:

- ≥90% FAQ answer accuracy
- ≤3 seconds average response time
- ≥80% successful retrieval rate
- ≥95% API availability
- Safe human escalation for unsupported queries
- Stable deployment for pilot use within a hospital

---

# 🧪 Testing

The MVP includes testing for:

- Unit Testing
- API Testing
- RAG Retrieval Testing
- Prompt Validation
- Integration Testing
- Security Testing
- Manual User Acceptance Testing (UAT)

---

# 🛣 Roadmap

## Phase 1 — MVP

- AI Chatbot
- Hospital FAQ
- RAG
- Admin Panel
- Human Escalation
- Deployment

---

## Phase 2

- AI Voice Telecaller
- Call Recording
- Call Analytics
- Appointment Booking
- Dashboard

---

## Phase 3

- AI Receptionist
- WhatsApp Integration
- Email Automation
- Agentic AI Workflows
- Voice Analytics
- Calendar Integration
- CRM Integration

---

## Phase 4

- Multi-Hospital SaaS
- Multi-Tenant Architecture
- Subscription Billing
- Role-Based Access Control
- Monitoring & Observability

---

# 🤝 Contributing

This project follows enterprise engineering standards.

Before contributing:

- Read `CLAUDE.md`
- Follow coding standards
- Add tests for new functionality
- Update documentation
- Ensure all CI checks pass

---

# 📜 License

This project is currently proprietary and intended for internal development and evaluation.

Future licensing will be determined prior to public release.

---

# 👨‍💻 Vision

Our long-term vision is to build an AI-powered Hospital Operating Assistant that automates patient interactions across voice, chat, web, and messaging platforms.

The MVP is the first milestone toward a scalable, secure, and enterprise-grade healthcare AI platform capable of serving hospitals of all sizes through a unified SaaS solution.