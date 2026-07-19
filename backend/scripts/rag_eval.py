"""Run the RAG golden-dataset evaluation against the live providers.

Usage (from ``backend/``, with AI credentials in the environment):

    python -m scripts.rag_eval [path/to/golden_dataset.json]

Requires the hospital profile and an indexed knowledge base. Prints a
per-case table and aggregate metrics; exits non-zero if any case fails.
"""

import asyncio
import sys
from pathlib import Path

from app.ai.embeddings import GeminiEmbeddingClient
from app.ai.evaluation import evaluate_rag, load_golden_dataset
from app.ai.llm import GeminiLLMClient
from app.ai.retriever import Retriever
from app.ai.vector_store import PineconeVectorStore
from app.core.config import get_settings
from app.database.session import dispose_engine, get_session_factory
from app.services.hospital_service import HospitalService
from app.services.rag_service import RagService

_DEFAULT_DATASET = Path(__file__).resolve().parent.parent / "evals" / "golden_dataset.json"


def _build_service(settings) -> RagService:
    if not (settings.gemini_api_key and settings.pinecone_api_key and settings.pinecone_index):
        raise SystemExit("GEMINI_API_KEY, PINECONE_API_KEY, and PINECONE_INDEX must be set.")
    embedder = GeminiEmbeddingClient(
        api_key=settings.gemini_api_key,
        model=settings.embedding_model,
        dimension=settings.embedding_dimension,
    )
    vector_store = PineconeVectorStore(
        api_key=settings.pinecone_api_key, index_name=settings.pinecone_index
    )
    retriever = Retriever(
        embedder,
        vector_store,
        top_k=settings.retrieval_top_k,
        min_score=settings.retrieval_min_score,
    )
    llm = GeminiLLMClient(
        api_key=settings.gemini_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_output_tokens=settings.llm_max_output_tokens,
    )
    return RagService(
        retriever=retriever, llm=llm, confidence_threshold=settings.rag_confidence_threshold
    )


async def main() -> int:
    settings = get_settings()
    dataset_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT_DATASET
    cases = load_golden_dataset(dataset_path)
    service = _build_service(settings)

    try:
        async with get_session_factory()() as session:
            hospital = await HospitalService(session).get_default_hospital()
        report = await evaluate_rag(
            service,
            hospital_id=hospital.id,
            cases=cases,
            max_turns=settings.conversation_max_turns,
        )
    finally:
        await dispose_engine()

    for result in report.results:
        status = "PASS" if result.passed else "FAIL"
        detail = f"escalated={result.escalated} confidence={result.confidence}"
        if result.missing_keywords:
            detail += f" missing={result.missing_keywords}"
        print(f"[{status}] {result.case_id}: {detail}")
    print(
        f"\n{report.passed}/{report.total} passed "
        f"(pass rate {report.pass_rate}, escalation accuracy {report.escalation_accuracy})"
    )
    return 0 if report.passed == report.total else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
