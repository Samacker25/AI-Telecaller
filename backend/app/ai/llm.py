"""LLM text generation for grounded answers.

The ``LLMClient`` protocol keeps the service layer independent of the
provider; ``GeminiLLMClient`` is the production implementation.
"""

from typing import Protocol

from app.core.logging import get_logger

logger = get_logger("app.ai.llm")


class LLMError(Exception):
    """Raised when the LLM cannot produce a response."""


class LLMClient(Protocol):
    """Generates a text answer from a system instruction and a prompt."""

    def generate(self, *, system_instruction: str, prompt: str) -> str: ...


class GeminiLLMClient:
    """Generates answers using the Gemini API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        temperature: float,
        max_output_tokens: int,
    ) -> None:
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens

    def generate(self, *, system_instruction: str, prompt: str) -> str:
        from google.genai import types

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=self._temperature,
            max_output_tokens=self._max_output_tokens,
        )
        try:
            response = self._client.models.generate_content(
                model=self._model, contents=prompt, config=config
            )
        except Exception as exc:
            logger.warning(
                "llm generation failed",
                extra={"extra_fields": {"model": self._model, "error": type(exc).__name__}},
            )
            raise LLMError("Answer generation failed.") from exc

        text = (response.text or "").strip()
        if not text:
            raise LLMError("LLM returned an empty response.")
        return text
