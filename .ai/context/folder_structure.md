# Project Structure

```
AI-Telecaller/

├── .ai/
│   └── context/
│
├── docs/
│
├── frontend/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── ai/
│   │   ├── utils/
│   │   └── main.py
│   │
│   └── tests/
│
├── scripts/
│
├── docker/
│
├── .github/
│
├── README.md
├── CLAUDE.md
└── CONTRIBUTING.md
```

---

## Layer Responsibilities

### API

HTTP endpoints only.

---

### Services

Business logic.

---

### Repositories

Database access.

---

### Models

Database models.

---

### Schemas

Request and response models.

---

### AI

RAG pipeline

Prompt construction

LLM integration

Retrieval

Embedding

---

### Tests

Unit

Integration

API

Performance

Future AI Evaluation

---

## Future Directories

After MVP:

```
evaluation/

prompts/

agents/

monitoring/
```

These directories should be introduced only when their corresponding roadmap phase begins.