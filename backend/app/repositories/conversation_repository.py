"""Data access for Conversation and Message records."""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message


class ConversationRepository:
    """Repository encapsulating conversations and messages table queries."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation | None:
        return await self._db.get(Conversation, conversation_id)

    async def get_by_session_id(self, session_id: uuid.UUID) -> Conversation | None:
        result = await self._db.execute(
            select(Conversation).where(Conversation.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def list_conversations(
        self, *, escalated: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[Conversation]:
        query = (
            select(Conversation)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if escalated is not None:
            query = query.where(Conversation.escalated == escalated)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def create(self, **fields: Any) -> Conversation:
        conversation = Conversation(**fields)
        self._db.add(conversation)
        await self._db.commit()
        await self._db.refresh(conversation)
        return conversation

    async def list_messages(
        self, conversation_id: uuid.UUID, *, last: int | None = None
    ) -> list[Message]:
        """Messages in conversation order; ``last`` keeps only the most recent N."""
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.position)
        )
        result = await self._db.execute(query)
        messages = list(result.scalars().all())
        if last is not None:
            messages = messages[-last:]
        return messages

    async def append_messages(self, conversation: Conversation, messages: list[Message]) -> None:
        """Store new messages atomically and update the conversation counters."""
        for offset, message in enumerate(messages):
            message.conversation_id = conversation.id
            message.position = conversation.message_count + offset
            self._db.add(message)
        conversation.message_count += len(messages)
        await self._db.commit()
