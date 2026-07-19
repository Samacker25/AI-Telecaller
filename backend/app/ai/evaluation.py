"""RAG evaluation framework: run golden-dataset cases through the RAG service.

Each golden case states what a correct response looks like: keywords the
answer must contain and whether the conversation should escalate. The
report gives answer accuracy, escalation accuracy, and an overall pass
rate, so RAG changes can be compared before release.
"""

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from app.ai.memory import ConversationMemory
from app.services.rag_service import RagService


class GoldenDatasetError(Exception):
    """Raised when the golden dataset file is missing or malformed."""


@dataclass(frozen=True)
class GoldenCase:
    """One evaluation scenario with its expected outcome."""

    id: str
    question: str
    expected_keywords: list[str] = field(default_factory=list)
    expect_escalation: bool = False


@dataclass(frozen=True)
class CaseResult:
    """Outcome of a single golden case."""

    case_id: str
    passed: bool
    escalated: bool
    escalation_correct: bool
    missing_keywords: list[str]
    confidence: float


@dataclass(frozen=True)
class EvaluationReport:
    """Aggregate metrics across all golden cases."""

    results: list[CaseResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def pass_rate(self) -> float:
        return round(self.passed / self.total, 4) if self.results else 0.0

    @property
    def escalation_accuracy(self) -> float:
        if not self.results:
            return 0.0
        correct = sum(1 for result in self.results if result.escalation_correct)
        return round(correct / self.total, 4)


def load_golden_dataset(path: Path) -> list[GoldenCase]:
    """Load and validate golden cases from a JSON file."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GoldenDatasetError(f"Golden dataset not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GoldenDatasetError(f"Golden dataset is not valid JSON: {path}") from exc

    if not isinstance(raw, list) or not raw:
        raise GoldenDatasetError("Golden dataset must be a non-empty JSON array.")

    cases: list[GoldenCase] = []
    for entry in raw:
        try:
            cases.append(
                GoldenCase(
                    id=str(entry["id"]),
                    question=str(entry["question"]),
                    expected_keywords=[str(k) for k in entry.get("expected_keywords", [])],
                    expect_escalation=bool(entry.get("expect_escalation", False)),
                )
            )
        except (KeyError, TypeError) as exc:
            raise GoldenDatasetError(f"Invalid golden case entry: {entry!r}") from exc
    return cases


async def evaluate_rag(
    service: RagService,
    *,
    hospital_id: uuid.UUID,
    cases: list[GoldenCase],
    max_turns: int = 10,
) -> EvaluationReport:
    """Run each case through the service in a fresh conversation.

    A case passes when the escalation outcome matches and, for
    non-escalation cases, every expected keyword appears in the answer
    (case-insensitive).
    """
    results: list[CaseResult] = []
    for case in cases:
        memory = ConversationMemory(max_turns=max_turns)
        answer = await service.answer(
            hospital_id=hospital_id, question=case.question, memory=memory
        )
        escalation_correct = answer.escalated == case.expect_escalation
        answer_lower = answer.answer.lower()
        missing = [
            keyword for keyword in case.expected_keywords if keyword.lower() not in answer_lower
        ]
        passed = escalation_correct and (case.expect_escalation or not missing)
        results.append(
            CaseResult(
                case_id=case.id,
                passed=passed,
                escalated=answer.escalated,
                escalation_correct=escalation_correct,
                missing_keywords=missing,
                confidence=answer.confidence,
            )
        )
    return EvaluationReport(results=results)
