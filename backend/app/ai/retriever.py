"""Retrieval engine: embed a query and find the most relevant knowledge chunks.

Retrieval always precedes generation. Results below the configured
similarity floor are dropped so the LLM only ever sees relevant context.
"""

import time
import uuid

from starlette.concurrency import run_in_threadpool

from app.ai.embeddings import EmbeddingClient
from app.ai.vector_store import RetrievedChunk, VectorStore
from app.core.logging import get_logger

logger = get_logger("app.ai.retriever")


class Retriever:
    """Semantic search over a hospital's indexed knowledge base."""

    def __init__(
        self,
        embedder: EmbeddingClient,
        vector_store: VectorStore,
        *,
        top_k: int,
        min_score: float,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        self._embedder = embedder
        self._vector_store = vector_store
        self._top_k = top_k
        self._min_score = min_score

    async def retrieve(self, *, hospital_id: uuid.UUID, query: str) -> list[RetrievedChunk]:
        """Return the most relevant chunks for ``query``, best match first.

        Chunks scoring below ``min_score`` are filtered out; an empty result
        means the knowledge base has nothing relevant to this question.
        """
        started = time.perf_counter()
        vectors = await run_in_threadpool(self._embedder.embed_texts, [query])
        matches = await run_in_threadpool(
            self._vector_store.query,
            hospital_id=hospital_id,
            vector=vectors[0],
            top_k=self._top_k,
        )
        relevant = sorted(
            (match for match in matches if match.score >= self._min_score),
            key=lambda match: match.score,
            reverse=True,
        )
        logger.info(
            "retrieval completed",
            extra={
                "extra_fields": {
                    "hospital_id": str(hospital_id),
                    "matches": len(matches),
                    "relevant": len(relevant),
                    "scores": [round(match.score, 4) for match in relevant],
                    "document_ids": [match.document_id for match in relevant],
                    "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                }
            },
        )
        return relevant
