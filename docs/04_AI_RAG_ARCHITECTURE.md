# 04 — AI RAG Architecture

**Project:** AI Telecaller for Hospitals (MVP)

**Version:** 0.1 (Knowledge Ingestion — Phase 3)

**Status:** In Progress — retrieval and generation are added in Phase 4

**Owner:** AI Architecture Team

---

# 1. Purpose

This document describes the AI knowledge architecture. Phase 3 delivers the ingestion half of the RAG pipeline: uploaded hospital documents are parsed, cleaned, chunked, embedded, and indexed into Pinecone. Phase 4 adds retrieval, prompt building, and grounded generation.

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

When AI credentials are absent (local development), uploads still succeed and are marked `failed` with `AI_NOT_CONFIGURED`.

---

# 6. Phase 4 (Planned)

Retrieval engine, prompt builder, Gemini generation, conversation memory, citations, confidence scoring, and human escalation. Retrieval always precedes generation; answers must be grounded in retrieved chunks.
