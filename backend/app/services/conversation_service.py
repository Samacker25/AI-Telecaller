"""Read access to stored conversations for hospital staff."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.conversation import Conversation, Message
from app.repositories.conversation_repository import ConversationRepository


class ConversationService:
    """Lists conversations and returns full message histories."""

    def __init__(self, db: AsyncSession) -> None:
        self._conversations = ConversationRepository(db)

    async def list_conversations(
        self, *, escalated: bool | None = None, limit: int = 50, offset: int = 0
    ) -> list[Conversation]:
        return await self._conversations.list_conversations(
            escalated=escalated, limit=limit, offset=offset
        )

    async def get_conversation(
        self, conversation_id: uuid.UUID
    ) -> tuple[Conversation, list[Message]]:
        conversation = await self._conversations.get_by_id(conversation_id)
        if conversation is None:
            raise NotFoundError(code="CONVERSATION_NOT_FOUND", message="Conversation not found.")
        messages = await self._conversations.list_messages(conversation.id)
        return conversation, messages
