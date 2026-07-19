"""Schemas for RAG answers, citations, and escalation.

Defined as Pydantic models so the Phase 5 chat API can return them
directly.
"""

import enum

from pydantic import BaseModel


class EscalationReason(enum.StrEnum):
    EMERGENCY = "emergency"
    MEDICAL_ADVICE = "medical_advice"
    NO_KNOWLEDGE = "no_knowledge"
    LOW_CONFIDENCE = "low_confidence"
    GENERATION_FAILED = "generation_failed"


class Citation(BaseModel):
    """Source chunk that grounded an answer."""

    document_id: str
    file_name: str
    chunk_index: int
    score: float


class RagAnswer(BaseModel):
    """A grounded answer with confidence, sources, and escalation state."""

    answer: str
    confidence: float
    escalated: bool
    escalation_reason: EscalationReason | None = None
    citations: list[Citation] = []
