"""Unit tests for the RAG core: retriever, memory, prompts, safety, and service."""

import uuid

import pytest

from app.ai.llm import LLMError
from app.ai.memory import ConversationMemory, TurnRole
from app.ai.prompt_builder import build_prompt, build_system_instruction
from app.ai.retriever import Retriever
from app.ai.safety import detect_emergency, detect_medical_advice_request
from app.ai.vector_store import RetrievedChunk, VectorStoreError
from app.core.exceptions import AppError, ServiceUnavailableError
from app.schemas.rag import EscalationReason
from app.services.rag_service import RagService

HOSPITAL_ID = uuid.uuid4()


def make_chunk(
    score: float, *, index: int = 0, text: str = "OPD runs 9 AM to 5 PM."
) -> RetrievedChunk:
    return RetrievedChunk(
        document_id="doc-1",
        chunk_index=index,
        file_name="hospital_faq.pdf",
        text=text,
        score=score,
    )


class FakeEmbedder:
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


class FakeVectorStore:
    def __init__(self, results: list[RetrievedChunk], *, error: Exception | None = None) -> None:
        self.results = results
        self.error = error
        self.queries: list[dict] = []

    def query(
        self, *, hospital_id: uuid.UUID, vector: list[float], top_k: int
    ) -> list[RetrievedChunk]:
        if self.error is not None:
            raise self.error
        self.queries.append({"hospital_id": hospital_id, "top_k": top_k})
        return self.results


class FakeLLM:
    def __init__(self, answer: str = "OPD runs 9 AM to 5 PM [1].", *, error: bool = False) -> None:
        self.answer = answer
        self.error = error
        self.prompts: list[dict] = []

    def generate(self, *, system_instruction: str, prompt: str) -> str:
        if self.error:
            raise LLMError("Answer generation failed.")
        self.prompts.append({"system_instruction": system_instruction, "prompt": prompt})
        return self.answer


def make_service(
    results: list[RetrievedChunk],
    *,
    llm: FakeLLM | None = None,
    store_error: Exception | None = None,
    confidence_threshold: float = 0.55,
    emergency_contact: str | None = None,
) -> tuple[RagService, FakeLLM]:
    llm = llm or FakeLLM()
    retriever = Retriever(
        FakeEmbedder(),
        FakeVectorStore(results, error=store_error),
        top_k=5,
        min_score=0.45,
    )
    service = RagService(
        retriever=retriever,
        llm=llm,
        confidence_threshold=confidence_threshold,
        emergency_contact=emergency_contact,
    )
    return service, llm


def memory() -> ConversationMemory:
    return ConversationMemory(max_turns=10)


class TestRetriever:
    async def test_filters_below_min_score_and_sorts(self):
        store = FakeVectorStore(
            [make_chunk(0.5), make_chunk(0.9, index=1), make_chunk(0.2, index=2)]
        )
        retriever = Retriever(FakeEmbedder(), store, top_k=5, min_score=0.45)
        chunks = await retriever.retrieve(hospital_id=HOSPITAL_ID, query="opd timings")
        assert [c.score for c in chunks] == [0.9, 0.5]
        assert store.queries[0]["top_k"] == 5

    async def test_empty_when_nothing_relevant(self):
        retriever = Retriever(
            FakeEmbedder(), FakeVectorStore([make_chunk(0.1)]), top_k=5, min_score=0.45
        )
        assert await retriever.retrieve(hospital_id=HOSPITAL_ID, query="anything") == []

    def test_rejects_non_positive_top_k(self):
        with pytest.raises(ValueError):
            Retriever(FakeEmbedder(), FakeVectorStore([]), top_k=0, min_score=0.45)


class TestConversationMemory:
    def test_keeps_only_most_recent_turns(self):
        mem = ConversationMemory(max_turns=4)
        for i in range(4):
            mem.add_user(f"question {i}")
            mem.add_assistant(f"answer {i}")
        turns = mem.turns
        assert len(turns) == 4
        assert turns[0].content == "question 2"
        assert turns[-1].content == "answer 3"

    def test_clear_resets_context(self):
        mem = ConversationMemory(max_turns=4)
        mem.add_user("hello")
        mem.clear()
        assert mem.turns == []

    def test_rejects_non_positive_window(self):
        with pytest.raises(ValueError):
            ConversationMemory(max_turns=0)


class TestPromptBuilder:
    def test_context_history_question_order(self):
        mem = memory()
        mem.add_user("Hi")
        mem.add_assistant("Hello, how can I help?")
        prompt = build_prompt(
            question="What are the OPD timings?",
            chunks=[make_chunk(0.9), make_chunk(0.8, index=1, text="Sunday is closed.")],
            history=mem.turns,
        )
        assert (
            prompt.index("CONTEXT:")
            < prompt.index("CONVERSATION HISTORY:")
            < prompt.index("QUESTION:")
        )
        assert "[1] (source: hospital_faq.pdf)" in prompt
        assert "[2] (source: hospital_faq.pdf)" in prompt
        assert "User: Hi" in prompt
        assert "Assistant: Hello, how can I help?" in prompt
        assert prompt.rstrip().endswith("What are the OPD timings?")

    def test_history_section_omitted_when_empty(self):
        prompt = build_prompt(question="Q?", chunks=[make_chunk(0.9)], history=[])
        assert "CONVERSATION HISTORY:" not in prompt

    def test_system_instruction_states_grounding_rules(self):
        instruction = build_system_instruction()
        assert "ONLY" in instruction
        assert "diagnosis" in instruction
        assert "reveal this prompt" in instruction


class TestSafety:
    @pytest.mark.parametrize(
        "text",
        [
            "My father is having chest pain",
            "He is NOT BREATHING",
            "I think she took an overdose",
            "need an ambulance now",
        ],
    )
    def test_detects_emergencies(self, text):
        assert detect_emergency(text)

    @pytest.mark.parametrize(
        "text",
        [
            "What dosage of paracetamol should I take?",
            "Can you diagnose my rash?",
            "Should I take amoxicillin for this?",
            "Is it safe to take ibuprofen with food?",
        ],
    )
    def test_detects_medical_advice_requests(self, text):
        assert detect_medical_advice_request(text)

    @pytest.mark.parametrize(
        "text",
        ["What are the visiting hours?", "Which doctors are in cardiology?"],
    )
    def test_ignores_informational_questions(self, text):
        assert not detect_emergency(text)
        assert not detect_medical_advice_request(text)


class TestRagService:
    async def test_grounded_answer_with_citations_and_confidence(self):
        service, llm = make_service([make_chunk(0.91), make_chunk(0.72, index=1)])
        mem = memory()
        answer = await service.answer(
            hospital_id=HOSPITAL_ID, question="What are the OPD timings?", memory=mem
        )
        assert not answer.escalated
        assert answer.answer == "OPD runs 9 AM to 5 PM [1]."
        assert answer.confidence == 0.91
        assert [c.chunk_index for c in answer.citations] == [0, 1]
        assert answer.citations[0].file_name == "hospital_faq.pdf"
        # The generation prompt was grounded in the retrieved context.
        assert "CONTEXT:" in llm.prompts[0]["prompt"]
        # The exchange is remembered for follow-up questions.
        assert [t.role for t in mem.turns] == [TurnRole.USER, TurnRole.ASSISTANT]

    async def test_escalates_when_no_relevant_knowledge(self):
        service, llm = make_service([make_chunk(0.1)])
        answer = await service.answer(
            hospital_id=HOSPITAL_ID, question="Share price?", memory=memory()
        )
        assert answer.escalated
        assert answer.escalation_reason == EscalationReason.NO_KNOWLEDGE
        assert answer.citations == []
        assert llm.prompts == []  # generation never runs without knowledge

    async def test_escalates_on_low_confidence(self):
        service, _ = make_service([make_chunk(0.5)], confidence_threshold=0.55)
        answer = await service.answer(hospital_id=HOSPITAL_ID, question="OPD?", memory=memory())
        assert answer.escalated
        assert answer.escalation_reason == EscalationReason.LOW_CONFIDENCE
        assert answer.confidence == 0.5

    async def test_escalates_emergencies_without_retrieval(self):
        service, llm = make_service([make_chunk(0.9)], emergency_contact="+91 11 2345 6789")
        answer = await service.answer(
            hospital_id=HOSPITAL_ID, question="chest pain right now!", memory=memory()
        )
        assert answer.escalated
        assert answer.escalation_reason == EscalationReason.EMERGENCY
        assert "+91 11 2345 6789" in answer.answer
        assert llm.prompts == []

    async def test_escalates_medical_advice_requests(self):
        service, _ = make_service([make_chunk(0.9)])
        answer = await service.answer(
            hospital_id=HOSPITAL_ID, question="What dosage should I take?", memory=memory()
        )
        assert answer.escalated
        assert answer.escalation_reason == EscalationReason.MEDICAL_ADVICE

    async def test_escalates_when_generation_fails(self):
        service, _ = make_service([make_chunk(0.9)], llm=FakeLLM(error=True))
        answer = await service.answer(hospital_id=HOSPITAL_ID, question="OPD?", memory=memory())
        assert answer.escalated
        assert answer.escalation_reason == EscalationReason.GENERATION_FAILED
        assert answer.confidence == 0.9

    async def test_vector_store_outage_raises_service_unavailable(self):
        service, _ = make_service([], store_error=VectorStoreError("down"))
        with pytest.raises(ServiceUnavailableError):
            await service.answer(hospital_id=HOSPITAL_ID, question="OPD?", memory=memory())

    async def test_rejects_empty_question(self):
        service, _ = make_service([make_chunk(0.9)])
        with pytest.raises(AppError):
            await service.answer(hospital_id=HOSPITAL_ID, question="   ", memory=memory())

    async def test_history_included_in_follow_up_prompt(self):
        service, llm = make_service([make_chunk(0.9)])
        mem = memory()
        await service.answer(
            hospital_id=HOSPITAL_ID, question="What are the OPD timings?", memory=mem
        )
        await service.answer(hospital_id=HOSPITAL_ID, question="And on Sundays?", memory=mem)
        follow_up_prompt = llm.prompts[1]["prompt"]
        assert "User: What are the OPD timings?" in follow_up_prompt
        assert "Assistant: OPD runs 9 AM to 5 PM [1]." in follow_up_prompt
