"""Request and response schemas for the chat and conversation endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.rag import Citation, EscalationReason

MAX_MESSAGE_LENGTH = 2000


class ChatRequest(BaseModel):
    """A visitor message. Omitting ``session_id`` starts a new session."""

    session_id: uuid.UUID | None = None
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)

    @field_validator("message")
    @classmethod
    def _strip_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message must not be empty or whitespace")
        return value


class ChatResponse(BaseModel):
    """The assistant's grounded answer for one chat message."""

    session_id: uuid.UUID
    conversation_id: uuid.UUID
    answer: str
    confidence: float
    escalated: bool
    escalation_reason: EscalationReason | None = None
    citations: list[Citation] = []


class ChatResetRequest(BaseModel):
    session_id: uuid.UUID | None = None


class ChatResetResponse(BaseModel):
    """A fresh session id; the previous conversation history is preserved."""

    session_id: uuid.UUID


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    position: int
    sender: str
    message: str
    response_time_ms: int | None
    confidence_score: float | None
    escalation_reason: str | None
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    hospital_id: uuid.UUID
    channel: str
    escalated: bool
    message_count: int
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponse(ConversationResponse):
    """A conversation together with its full message history."""

    messages: list[MessageResponse]
