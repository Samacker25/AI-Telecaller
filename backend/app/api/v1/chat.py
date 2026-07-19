"""Public chat endpoints for the website chatbot.

Visitors are unauthenticated; sessions are tracked with unguessable
UUID session ids. The streaming endpoint answers over Server-Sent
Events so the frontend can render responses incrementally.
"""

import json
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import GeminiEmbeddingClient
from app.ai.llm import GeminiLLMClient
from app.ai.retriever import Retriever
from app.ai.vector_store import PineconeVectorStore
from app.core.config import get_settings
from app.core.exceptions import ServiceUnavailableError
from app.database.session import get_db
from app.schemas.chat import ChatRequest, ChatResetRequest, ChatResetResponse, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

DbSession = Annotated[AsyncSession, Depends(get_db)]

_STREAM_WORDS_PER_CHUNK = 8


def get_chat_service(db: DbSession) -> ChatService:
    """Build the chat service with AI providers from configuration."""
    settings = get_settings()
    if not settings.gemini_api_key or not settings.pinecone_api_key or not settings.pinecone_index:
        raise ServiceUnavailableError(
            code="AI_NOT_CONFIGURED",
            message="The AI assistant is not available right now.",
        )
    retriever = Retriever(
        GeminiEmbeddingClient(
            api_key=settings.gemini_api_key,
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        ),
        PineconeVectorStore(api_key=settings.pinecone_api_key, index_name=settings.pinecone_index),
        top_k=settings.retrieval_top_k,
        min_score=settings.retrieval_min_score,
    )
    llm = GeminiLLMClient(
        api_key=settings.gemini_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_output_tokens=settings.llm_max_output_tokens,
    )
    return ChatService(
        db,
        retriever=retriever,
        llm=llm,
        confidence_threshold=settings.rag_confidence_threshold,
        max_history_turns=settings.conversation_max_turns,
    )


Chat = Annotated[ChatService, Depends(get_chat_service)]


@router.post("", response_model=ChatResponse)
async def send_message(payload: ChatRequest, service: Chat) -> ChatResponse:
    """Answer a visitor message. Omit ``session_id`` to start a new session."""
    return await service.handle_message(session_id=payload.session_id, message=payload.message)


@router.post("/stream")
async def send_message_stream(payload: ChatRequest, service: Chat) -> StreamingResponse:
    """Answer a visitor message as a Server-Sent Events stream.

    Events: ``meta`` (session/conversation ids), ``delta`` (answer text
    chunks), ``done`` (confidence, escalation state, citations).
    """
    response = await service.handle_message(session_id=payload.session_id, message=payload.message)
    return StreamingResponse(
        _stream_events(response),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/reset", response_model=ChatResetResponse)
async def reset_conversation(payload: ChatResetRequest, service: Chat) -> ChatResetResponse:
    """Clear the conversation context by issuing a fresh session id."""
    return ChatResetResponse(session_id=service.reset_session())


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _stream_events(response: ChatResponse) -> AsyncIterator[str]:
    """Emit a completed chat response as an SSE event sequence."""
    yield _sse_event(
        "meta",
        {"session_id": str(response.session_id), "conversation_id": str(response.conversation_id)},
    )
    words = response.answer.split(" ")
    for start in range(0, len(words), _STREAM_WORDS_PER_CHUNK):
        chunk = " ".join(words[start : start + _STREAM_WORDS_PER_CHUNK])
        if start + _STREAM_WORDS_PER_CHUNK < len(words):
            chunk += " "
        yield _sse_event("delta", {"text": chunk})
    yield _sse_event(
        "done",
        {
            "confidence": response.confidence,
            "escalated": response.escalated,
            "escalation_reason": (
                response.escalation_reason.value if response.escalation_reason else None
            ),
            "citations": [citation.model_dump() for citation in response.citations],
        },
    )
