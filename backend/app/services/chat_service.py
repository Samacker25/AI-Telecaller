"""Chat orchestration: sessions, persisted history, and RAG answers.

The service resolves the session's conversation, rebuilds the bounded
prompt window from stored messages, delegates answering to the RAG
service, and persists both sides of the exchange.
"""

import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm import LLMClient
from app.ai.memory import ConversationMemory
from app.ai.retriever import Retriever
from app.core.exceptions import ServiceUnavailableError
from app.core.logging import get_logger
from app.models.conversation import Conversation, ConversationChannel, Message, MessageSender
from app.models.hospital import Hospital
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.hospital_repository import HospitalRepository
from app.schemas.chat import ChatResponse
from app.services.rag_service import RagService

logger = get_logger("app.services.chat")


class ChatService:
    """Handles chat sessions backed by persisted conversations."""

    def __init__(
        self,
        db: AsyncSession,
        *,
        retriever: Retriever,
        llm: LLMClient,
        confidence_threshold: float,
        max_history_turns: int,
    ) -> None:
        self._conversations = ConversationRepository(db)
        self._hospitals = HospitalRepository(db)
        self._retriever = retriever
        self._llm = llm
        self._confidence_threshold = confidence_threshold
        self._max_history_turns = max_history_turns

    async def handle_message(self, *, session_id: uuid.UUID | None, message: str) -> ChatResponse:
        """Answer one visitor message within its session."""
        hospital = await self._require_hospital()
        conversation = await self._resolve_conversation(session_id, hospital)
        memory = await self._rebuild_memory(conversation)

        rag = RagService(
            retriever=self._retriever,
            llm=self._llm,
            confidence_threshold=self._confidence_threshold,
            emergency_contact=self._emergency_contact(hospital),
        )
        started = time.perf_counter()
        answer = await rag.answer(hospital_id=hospital.id, question=message, memory=memory)
        response_time_ms = round((time.perf_counter() - started) * 1000)

        if answer.escalated:
            conversation.escalated = True
        await self._conversations.append_messages(
            conversation,
            [
                Message(sender=MessageSender.USER.value, message=message.strip()),
                Message(
                    sender=MessageSender.AI.value,
                    message=answer.answer,
                    response_time_ms=response_time_ms,
                    confidence_score=answer.confidence,
                    escalation_reason=(
                        answer.escalation_reason.value if answer.escalation_reason else None
                    ),
                ),
            ],
        )
        logger.info(
            "chat message handled",
            extra={
                "extra_fields": {
                    "conversation_id": str(conversation.id),
                    "escalated": answer.escalated,
                    "response_time_ms": response_time_ms,
                }
            },
        )
        return ChatResponse(
            session_id=conversation.session_id,
            conversation_id=conversation.id,
            answer=answer.answer,
            confidence=answer.confidence,
            escalated=answer.escalated,
            escalation_reason=answer.escalation_reason,
            citations=answer.citations,
        )

    @staticmethod
    def reset_session() -> uuid.UUID:
        """Issue a fresh session id; the old conversation history is preserved.

        Session ids map one-to-one to conversations, so a new id gives the
        visitor a clean context on their next message.
        """
        session_id = uuid.uuid4()
        logger.info("chat session reset")
        return session_id

    async def _require_hospital(self) -> Hospital:
        hospital = await self._hospitals.get_first()
        if hospital is None:
            raise ServiceUnavailableError(
                code="HOSPITAL_NOT_CONFIGURED",
                message="The hospital profile has not been configured yet.",
            )
        return hospital

    async def _resolve_conversation(
        self, session_id: uuid.UUID | None, hospital: Hospital
    ) -> Conversation:
        """Find the session's conversation, creating one for new sessions."""
        if session_id is not None:
            conversation = await self._conversations.get_by_session_id(session_id)
            if conversation is not None:
                return conversation
        return await self._conversations.create(
            session_id=session_id or uuid.uuid4(),
            hospital_id=hospital.id,
            channel=ConversationChannel.CHAT.value,
        )

    async def _rebuild_memory(self, conversation: Conversation) -> ConversationMemory:
        """Rebuild the prompt window from the most recent stored messages."""
        memory = ConversationMemory(max_turns=self._max_history_turns)
        messages = await self._conversations.list_messages(
            conversation.id, last=self._max_history_turns
        )
        for message in messages:
            if message.sender == MessageSender.USER.value:
                memory.add_user(message.message)
            elif message.sender == MessageSender.AI.value:
                memory.add_assistant(message.message)
        return memory

    @staticmethod
    def _emergency_contact(hospital: Hospital) -> str | None:
        settings = hospital.settings or {}
        contact = settings.get("emergency_contact")
        return contact if isinstance(contact, str) and contact.strip() else None
