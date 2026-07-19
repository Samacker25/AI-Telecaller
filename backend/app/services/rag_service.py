"""RAG orchestration: retrieve -> assess confidence -> generate or escalate.

Retrieval always precedes generation. When the knowledge base cannot
support a confident answer — or the question needs a human (emergency,
medical advice) — the service escalates instead of letting the model
guess.
"""

import time
import uuid

from fastapi import status
from starlette.concurrency import run_in_threadpool

from app.ai.llm import LLMClient, LLMError
from app.ai.memory import ConversationMemory
from app.ai.prompt_builder import build_prompt, build_system_instruction
from app.ai.retriever import Retriever
from app.ai.safety import detect_emergency, detect_medical_advice_request
from app.ai.vector_store import RetrievedChunk, VectorStoreError
from app.core.exceptions import AppError, ServiceUnavailableError
from app.core.logging import get_logger
from app.schemas.rag import Citation, EscalationReason, RagAnswer

logger = get_logger("app.services.rag")

_FALLBACK_UNAVAILABLE = (
    "I'm not certain about that based on the hospital's information. "
    "I have flagged your question for our staff, who will follow up with the correct details."
)
_FALLBACK_GENERATION = (
    "I'm having trouble answering right now. " "Your question has been forwarded to hospital staff."
)
_FALLBACK_MEDICAL_ADVICE = (
    "I can't provide medical advice such as diagnosis, prescriptions, or dosages. "
    "Please consult a qualified doctor. "
    "I have flagged this conversation for hospital staff to follow up."
)


class RagService:
    """Answers hospital questions grounded in retrieved knowledge."""

    def __init__(
        self,
        *,
        retriever: Retriever,
        llm: LLMClient,
        confidence_threshold: float,
        emergency_contact: str | None = None,
    ) -> None:
        self._retriever = retriever
        self._llm = llm
        self._confidence_threshold = confidence_threshold
        self._emergency_contact = emergency_contact

    async def answer(
        self,
        *,
        hospital_id: uuid.UUID,
        question: str,
        memory: ConversationMemory,
    ) -> RagAnswer:
        """Produce a grounded answer (or an escalation) for ``question``."""
        question = question.strip()
        if not question:
            raise AppError(
                code="EMPTY_QUESTION",
                message="Question must not be empty.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if detect_emergency(question):
            return self._escalate(
                memory,
                question=question,
                reason=EscalationReason.EMERGENCY,
                answer=self._emergency_message(),
            )
        if detect_medical_advice_request(question):
            return self._escalate(
                memory,
                question=question,
                reason=EscalationReason.MEDICAL_ADVICE,
                answer=_FALLBACK_MEDICAL_ADVICE,
            )

        try:
            chunks = await self._retriever.retrieve(hospital_id=hospital_id, query=question)
        except VectorStoreError as exc:
            raise ServiceUnavailableError(
                code="VECTOR_STORE_UNAVAILABLE",
                message="Knowledge search is unavailable. Try again later.",
            ) from exc

        if not chunks:
            return self._escalate(
                memory,
                question=question,
                reason=EscalationReason.NO_KNOWLEDGE,
                answer=_FALLBACK_UNAVAILABLE,
            )

        confidence = self._confidence(chunks)
        if confidence < self._confidence_threshold:
            return self._escalate(
                memory,
                question=question,
                reason=EscalationReason.LOW_CONFIDENCE,
                answer=_FALLBACK_UNAVAILABLE,
                confidence=confidence,
            )

        prompt = build_prompt(question=question, chunks=chunks, history=memory.turns)
        started = time.perf_counter()
        try:
            answer_text = await run_in_threadpool(
                self._llm.generate,
                system_instruction=build_system_instruction(),
                prompt=prompt,
            )
        except LLMError:
            return self._escalate(
                memory,
                question=question,
                reason=EscalationReason.GENERATION_FAILED,
                answer=_FALLBACK_GENERATION,
                confidence=confidence,
            )
        logger.info(
            "answer generated",
            extra={
                "extra_fields": {
                    "hospital_id": str(hospital_id),
                    "confidence": confidence,
                    "citations": len(chunks),
                    "llm_duration_ms": round((time.perf_counter() - started) * 1000, 1),
                }
            },
        )

        memory.add_user(question)
        memory.add_assistant(answer_text)
        return RagAnswer(
            answer=answer_text,
            confidence=confidence,
            escalated=False,
            citations=[
                Citation(
                    document_id=chunk.document_id,
                    file_name=chunk.file_name,
                    chunk_index=chunk.chunk_index,
                    score=round(chunk.score, 4),
                )
                for chunk in chunks
            ],
        )

    @staticmethod
    def _confidence(chunks: list[RetrievedChunk]) -> float:
        """Confidence is the best retrieval similarity: simple and explainable."""
        return round(max(chunk.score for chunk in chunks), 4)

    def _escalate(
        self,
        memory: ConversationMemory,
        *,
        question: str,
        reason: EscalationReason,
        answer: str,
        confidence: float = 0.0,
    ) -> RagAnswer:
        """Record the exchange and return a safe, escalated response."""
        logger.info(
            "conversation escalated",
            extra={"extra_fields": {"reason": reason.value, "confidence": confidence}},
        )
        memory.add_user(question)
        memory.add_assistant(answer)
        return RagAnswer(
            answer=answer,
            confidence=confidence,
            escalated=True,
            escalation_reason=reason,
        )

    def _emergency_message(self) -> str:
        contact = self._emergency_contact or "the hospital emergency line"
        return (
            f"If this is a medical emergency, please call {contact} "
            "or your local emergency number immediately. "
            "I am also alerting hospital staff to assist you."
        )
