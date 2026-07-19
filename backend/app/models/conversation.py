"""Conversation and message models for the chat API.

A conversation groups the messages exchanged during one chat session.
The ``position`` column on messages gives a deterministic ordering for
rebuilding the prompt window, independent of timestamp resolution.
"""

import enum
import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class ConversationChannel(enum.StrEnum):
    """Channel a conversation arrived through. Voice arrives in Phase 2."""

    CHAT = "chat"


class MessageSender(enum.StrEnum):
    """Author of a stored message."""

    USER = "user"
    AI = "ai"
    HUMAN = "human"


class Conversation(Base, TimestampMixin):
    """One chat session between a visitor and the AI assistant."""

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True, index=True, nullable=False)
    hospital_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("hospitals.id", ondelete="CASCADE"), index=True, nullable=False
    )
    channel: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ConversationChannel.CHAT.value
    )
    escalated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Message(Base, TimestampMixin):
    """A single stored utterance within a conversation."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    sender: Mapped[str] = mapped_column(String(10), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    escalation_reason: Mapped[str | None] = mapped_column(String(30))
