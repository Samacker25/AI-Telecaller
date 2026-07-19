"""Conversation history endpoints for hospital staff. Authenticated."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.database.session import get_db
from app.schemas.chat import ConversationDetailResponse, ConversationResponse, MessageResponse
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_conversation_service(db: DbSession) -> ConversationService:
    return ConversationService(db)


Conversations = Annotated[ConversationService, Depends(get_conversation_service)]


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    user: CurrentUser,
    service: Conversations,
    escalated: Annotated[bool | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ConversationResponse]:
    """List conversations, newest first, optionally filtered by escalation."""
    conversations = await service.list_conversations(
        escalated=escalated, limit=limit, offset=offset
    )
    return [ConversationResponse.model_validate(conversation) for conversation in conversations]


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: uuid.UUID, user: CurrentUser, service: Conversations
) -> ConversationDetailResponse:
    """Return a conversation with its complete message history."""
    conversation, messages = await service.get_conversation(conversation_id)
    return ConversationDetailResponse(
        **ConversationResponse.model_validate(conversation).model_dump(),
        messages=[MessageResponse.model_validate(message) for message in messages],
    )
