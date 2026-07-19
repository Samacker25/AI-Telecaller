"""Embedding generation for knowledge chunks.

The ``EmbeddingClient`` protocol keeps the service layer independent of the
provider; ``GeminiEmbeddingClient`` is the production implementation.
"""

from typing import Protocol

from app.core.logging import get_logger

logger = get_logger("app.ai.embeddings")

# Gemini embed_content accepts at most 100 texts per request.
_BATCH_SIZE = 100


class EmbeddingError(Exception):
    """Raised when embeddings cannot be generated."""


class EmbeddingClient(Protocol):
    """Generates one embedding vector per input text."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class GeminiEmbeddingClient:
    """Embeds text using the Gemini embeddings API."""

    def __init__(self, api_key: str, model: str, dimension: int) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._dimension = dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        from google.genai import types

        vectors: list[list[float]] = []
        config = types.EmbedContentConfig(output_dimensionality=self._dimension)
        try:
            for start in range(0, len(texts), _BATCH_SIZE):
                batch = texts[start : start + _BATCH_SIZE]
                response = self._client.models.embed_content(
                    model=self._model, contents=batch, config=config
                )
                vectors.extend(list(embedding.values) for embedding in response.embeddings)
        except Exception as exc:
            logger.warning(
                "embedding generation failed",
                extra={"extra_fields": {"model": self._model, "error": type(exc).__name__}},
            )
            raise EmbeddingError("Embedding generation failed.") from exc

        if len(vectors) != len(texts):
            raise EmbeddingError("Embedding provider returned an unexpected number of vectors.")
        return vectors
