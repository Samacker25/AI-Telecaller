"""API tests for the chat endpoints and conversation history.

The retriever and LLM are replaced with in-memory fakes, so no external
AI services are required.
"""

import json
import uuid
from typing import Annotated

import pytest
from fastapi import Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm import LLMError
from app.ai.retriever import Retriever
from app.ai.vector_store import RetrievedChunk
from app.api.v1.chat import get_chat_service
from app.database.session import get_db
from app.services.chat_service import ChatService

ANSWER = "OPD runs 9 AM to 5 PM [1]."


def make_chunk(score: float, *, index: int = 0) -> RetrievedChunk:
    return RetrievedChunk(
        document_id="doc-1",
        chunk_index=index,
        file_name="hospital_faq.pdf",
        text="OPD runs 9 AM to 5 PM.",
        score=score,
    )


class FakeEmbedder:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]


class FakeVectorStore:
    """Returns a configurable result set; tests mutate ``results``."""

    def __init__(self) -> None:
        self.results: list[RetrievedChunk] = [make_chunk(0.91)]

    def query(
        self, *, hospital_id: uuid.UUID, vector: list[float], top_k: int
    ) -> list[RetrievedChunk]:
        return self.results


class FakeLLM:
    def __init__(self) -> None:
        self.answer = ANSWER
        self.error = False
        self.prompts: list[str] = []

    def generate(self, *, system_instruction: str, prompt: str) -> str:
        if self.error:
            raise LLMError("Answer generation failed.")
        self.prompts.append(prompt)
        return self.answer


@pytest.fixture
def vector_store() -> FakeVectorStore:
    return FakeVectorStore()


@pytest.fixture
def llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def chat_app(app, vector_store: FakeVectorStore, llm: FakeLLM):
    """App with the chat service wired to fake AI providers."""

    def override(db: Annotated[AsyncSession, Depends(get_db)]) -> ChatService:
        return ChatService(
            db,
            retriever=Retriever(FakeEmbedder(), vector_store, top_k=5, min_score=0.45),
            llm=llm,
            confidence_threshold=0.55,
            max_history_turns=10,
        )

    app.dependency_overrides[get_chat_service] = override
    return app


async def send_chat(client: AsyncClient, message: str, session_id: str | None = None) -> dict:
    payload: dict = {"message": message}
    if session_id is not None:
        payload["session_id"] = session_id
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


class TestChatEndpoint:
    async def test_answers_and_starts_session(self, chat_app, client, hospital):
        data = await send_chat(client, "What are the OPD timings?")
        assert data["answer"] == ANSWER
        assert data["confidence"] == 0.91
        assert not data["escalated"]
        assert data["citations"][0]["file_name"] == "hospital_faq.pdf"
        uuid.UUID(data["session_id"])
        uuid.UUID(data["conversation_id"])

    async def test_same_session_reuses_conversation_and_history(
        self, chat_app, client, hospital, llm
    ):
        first = await send_chat(client, "What are the OPD timings?")
        second = await send_chat(client, "And on Sundays?", session_id=first["session_id"])
        assert second["conversation_id"] == first["conversation_id"]
        # The stored history reappears in the follow-up prompt.
        assert "User: What are the OPD timings?" in llm.prompts[1]
        assert f"Assistant: {ANSWER}" in llm.prompts[1]

    async def test_client_supplied_session_id_creates_conversation(
        self, chat_app, client, hospital
    ):
        session_id = str(uuid.uuid4())
        data = await send_chat(client, "Hello, what are visiting hours?", session_id=session_id)
        assert data["session_id"] == session_id

    async def test_escalates_on_low_confidence_and_flags_conversation(
        self, chat_app, client, hospital, vector_store, admin_headers
    ):
        vector_store.results = [make_chunk(0.2)]
        data = await send_chat(client, "What is the share price?")
        assert data["escalated"]
        assert data["escalation_reason"] == "no_knowledge"

        listed = await client.get("/api/v1/conversations?escalated=true", headers=admin_headers)
        assert listed.status_code == 200
        assert [c["id"] for c in listed.json()] == [data["conversation_id"]]

    async def test_emergency_uses_hospital_contact(self, chat_app, client, hospital, admin_headers):
        response = await client.put(
            f"/api/v1/hospitals/{hospital['id']}/settings",
            json={"emergency_contact": "+91 11 2345 6789"},
            headers=admin_headers,
        )
        assert response.status_code == 200, response.text
        data = await send_chat(client, "My father has chest pain!")
        assert data["escalated"]
        assert data["escalation_reason"] == "emergency"
        assert "+91 11 2345 6789" in data["answer"]

    async def test_returns_503_when_hospital_not_configured(self, chat_app, client):
        response = await client.post("/api/v1/chat", json={"message": "Hello?"})
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "HOSPITAL_NOT_CONFIGURED"

    async def test_rejects_blank_message(self, chat_app, client, hospital):
        response = await client.post("/api/v1/chat", json={"message": "   "})
        assert response.status_code == 422

    async def test_persists_messages_with_metadata(self, chat_app, client, hospital, admin_headers):
        data = await send_chat(client, "What are the OPD timings?")
        detail = await client.get(
            f"/api/v1/conversations/{data['conversation_id']}", headers=admin_headers
        )
        assert detail.status_code == 200
        messages = detail.json()["messages"]
        assert [m["sender"] for m in messages] == ["user", "ai"]
        assert [m["position"] for m in messages] == [0, 1]
        assert messages[0]["message"] == "What are the OPD timings?"
        assert messages[1]["message"] == ANSWER
        assert messages[1]["confidence_score"] == pytest.approx(0.91)
        assert messages[1]["response_time_ms"] >= 0


class TestChatReset:
    async def test_reset_issues_fresh_session(self, chat_app, client, hospital, llm):
        first = await send_chat(client, "What are the OPD timings?")
        reset = await client.post("/api/v1/chat/reset", json={"session_id": first["session_id"]})
        assert reset.status_code == 200
        new_session = reset.json()["session_id"]
        assert new_session != first["session_id"]

        data = await send_chat(client, "And on Sundays?", session_id=new_session)
        assert data["conversation_id"] != first["conversation_id"]
        # The new context contains no history from the old session.
        assert "CONVERSATION HISTORY:" not in llm.prompts[1]


class TestChatStream:
    async def test_streams_meta_delta_done_events(self, chat_app, client, hospital):
        response = await client.post("/api/v1/chat/stream", json={"message": "OPD timings?"})
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        events = parse_sse(response.text)
        assert events[0][0] == "meta"
        uuid.UUID(events[0][1]["session_id"])
        deltas = [data["text"] for name, data in events if name == "delta"]
        assert "".join(deltas) == ANSWER
        done = events[-1]
        assert done[0] == "done"
        assert done[1]["confidence"] == 0.91
        assert not done[1]["escalated"]
        assert done[1]["citations"][0]["file_name"] == "hospital_faq.pdf"


class TestConversationHistory:
    async def test_requires_authentication(self, chat_app, client, hospital):
        assert (await client.get("/api/v1/conversations")).status_code == 401
        assert (await client.get(f"/api/v1/conversations/{uuid.uuid4()}")).status_code == 401

    async def test_staff_can_read_history(self, chat_app, client, hospital, staff_headers):
        data = await send_chat(client, "What are the OPD timings?")
        listed = await client.get("/api/v1/conversations", headers=staff_headers)
        assert listed.status_code == 200
        assert [c["id"] for c in listed.json()] == [data["conversation_id"]]
        assert listed.json()[0]["message_count"] == 2

    async def test_unknown_conversation_returns_404(self, chat_app, client, staff_headers):
        response = await client.get(f"/api/v1/conversations/{uuid.uuid4()}", headers=staff_headers)
        assert response.status_code == 404


def parse_sse(body: str) -> list[tuple[str, dict]]:
    """Parse an SSE body into (event, data) tuples."""
    events = []
    for block in body.strip().split("\n\n"):
        event_name, data = None, None
        for line in block.splitlines():
            if line.startswith("event: "):
                event_name = line.removeprefix("event: ")
            elif line.startswith("data: "):
                data = json.loads(line.removeprefix("data: "))
        assert event_name is not None and data is not None, block
        events.append((event_name, data))
    return events
