# 04 — AI RAG Architecture

**Project:** AI Telecaller for Hospitals (MVP)

**Version:** 0.2 (Retrieval + Generation — Phase 4)

**Status:** Current — chat API wiring arrives in Phase 5

**Owner:** AI Architecture Team

---

# 1. Purpose

This document describes the AI knowledge architecture. Phase 3 delivers the ingestion half of the RAG pipeline: uploaded hospital documents are parsed, cleaned, chunked, embedded, and indexed into Pinecone. Phase 4 adds the answering half: retrieval, prompt building, grounded Gemini generation, conversation memory, citations, confidence scoring, human escalation, and a golden-dataset evaluation framework.

---

# 2. Ingestion Pipeline

```
Upload (PDF / DOCX / TXT)
        │
        ▼
Validate (type, size, non-empty)
        │
        ▼
Store file + metadata record (status: uploaded)
        │
        ▼
Parse (status: processing)          app/ai/parsers.py
        │
        ▼
Clean text                          app/ai/text_cleaner.py
        │
        ▼
Chunk (paragraph-aware, overlap)    app/ai/chunker.py
        │
        ▼
Embed (Gemini embeddings)           app/ai/embeddings.py
        │
        ▼
Index into Pinecone                 app/ai/vector_store.py
        │
        ▼
Metadata updated (status: indexed, chunk_count)
```

Any failure marks the document `failed` with a safe error message; the upload itself is never lost, and `POST /documents/{id}/reindex` re-runs the pipeline.

---

# 3. Components

| Component | Module | Responsibility |
|-----------|--------|----------------|
| Parsers | `app/ai/parsers.py` | Extract text from PDF (pypdf), DOCX (python-docx), TXT |
| Text Cleaner | `app/ai/text_cleaner.py` | Unicode NFKC, line endings, control chars, whitespace |
| Chunker | `app/ai/chunker.py` | Paragraph-aware chunks (`CHUNK_SIZE` chars) with word-boundary overlap (`CHUNK_OVERLAP`) |
| Embeddings | `app/ai/embeddings.py` | `EmbeddingClient` protocol; `GeminiEmbeddingClient` (`EMBEDDING_MODEL`, `EMBEDDING_DIMENSION`) |
| Vector Store | `app/ai/vector_store.py` | `VectorStore` protocol; `PineconeVectorStore` |
| Orchestration | `app/services/knowledge_service.py` | Upload validation, status lifecycle, pipeline execution |

Providers are injected behind protocols so tests (and future providers) never touch the real services. Sync SDK calls run in a threadpool to keep endpoints non-blocking.

---

# 4. Vector Storage Layout

- Vector ID: `{document_id}:{chunk_index}`
- Namespace: hospital ID (prepares for multi-tenancy)
- Metadata: `document_id`, `hospital_id`, `chunk_index`, `file_name`, `text`

Deletes list IDs by document prefix (serverless indexes do not support metadata-filter deletes). PostgreSQL stores only document metadata (`documents` table); no embeddings or document text.

---

# 5. Configuration

| Variable | Default | Meaning |
|----------|---------|---------|
| `GEMINI_API_KEY` | — | Embedding provider credentials |
| `PINECONE_API_KEY` / `PINECONE_INDEX` | — | Vector database |
| `EMBEDDING_MODEL` | `gemini-embedding-001` | Embedding model |
| `EMBEDDING_DIMENSION` | `768` | Output dimensionality (must match the Pinecone index) |
| `CHUNK_SIZE` | `1200` | Target chunk length (characters) |
| `CHUNK_OVERLAP` | `200` | Overlap between adjacent chunks |
| `LLM_MODEL` | `gemini-2.5-flash` | Generation model |
| `LLM_TEMPERATURE` | `0.2` | Generation temperature (low for factual answers) |
| `LLM_MAX_OUTPUT_TOKENS` | `1024` | Generation output cap |
| `RETRIEVAL_TOP_K` | `5` | Chunks requested per query |
| `RETRIEVAL_MIN_SCORE` | `0.45` | Similarity floor; weaker matches are discarded |
| `RAG_CONFIDENCE_THRESHOLD` | `0.55` | Answers below this confidence escalate |
| `CONVERSATION_MAX_TURNS` | `10` | History turns kept in the prompt window |

When AI credentials are absent (local development), uploads still succeed and are marked `failed` with `AI_NOT_CONFIGURED`.

---

# 6. Answering Pipeline (Phase 4)

Retrieval always precedes generation; the model never answers hospital questions from its own memory.

```
Question
    │
    ▼
Safety checks (emergency / medical advice)     app/ai/safety.py
    │   └── match → escalate immediately (no retrieval, no LLM)
    ▼
Retrieve (embed query → Pinecone top-k,        app/ai/retriever.py
          drop scores < RETRIEVAL_MIN_SCORE)
    │   └── nothing relevant → escalate (no_knowledge)
    ▼
Confidence = best similarity score
    │   └── below RAG_CONFIDENCE_THRESHOLD → escalate (low_confidence)
    ▼
Build prompt (system → context → history →     app/ai/prompt_builder.py
              question)
    ▼
Generate (Gemini)                              app/ai/llm.py
    │   └── failure → escalate (generation_failed)
    ▼
RagAnswer {answer, confidence, citations,      app/services/rag_service.py
           escalated, escalation_reason}
```

## Components

| Component | Module | Responsibility |
|-----------|--------|----------------|
| Retriever | `app/ai/retriever.py` | Embed the query, similarity search, filter and rank chunks |
| Vector query | `app/ai/vector_store.py` | `VectorStore.query` → `RetrievedChunk` (id, file, text, score) |
| Prompt Builder | `app/ai/prompt_builder.py` | Fixed order: system instructions, numbered context, history, question |
| LLM | `app/ai/llm.py` | `LLMClient` protocol; `GeminiLLMClient` (`LLM_MODEL`) |
| Memory | `app/ai/memory.py` | `ConversationMemory` — bounded window of recent turns |
| Safety | `app/ai/safety.py` | Deterministic emergency / medical-advice detection |
| Orchestration | `app/services/rag_service.py` | Retrieval → confidence → generation or escalation |
| Evaluation | `app/ai/evaluation.py` | Golden-dataset runner (see `docs/11_AI_EVALUATION.md`) |

## Citations

Every non-escalated answer carries the retrieved chunks as citations (`document_id`, `file_name`, `chunk_index`, `score`), and the prompt instructs the model to reference context entries with `[n]` markers.

## Confidence and escalation

Confidence is the best retrieval similarity score — simple and explainable. The service escalates (safe fallback answer, `escalated: true`, a reason code, no invented content) for: `emergency`, `medical_advice`, `no_knowledge`, `low_confidence`, and `generation_failed`. Safety checks are deliberately deterministic keyword rules: a false positive only routes the patient to a human, which is the safe direction.

## Conversation memory

`ConversationMemory` keeps the last `CONVERSATION_MAX_TURNS` turns for prompt context; both grounded answers and escalations are recorded so follow-ups stay coherent. Persistent conversation storage (PostgreSQL `conversations`/`messages`) arrives with the Chat API in Phase 5, which will rebuild the window from stored messages.
