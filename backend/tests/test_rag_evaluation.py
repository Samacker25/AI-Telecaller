"""Tests for the RAG evaluation framework and the shipped golden dataset."""

import json
import uuid
from pathlib import Path

import pytest

from app.ai.evaluation import GoldenDatasetError, evaluate_rag, load_golden_dataset
from tests.test_rag import FakeLLM, make_chunk, make_service

GOLDEN_DATASET_PATH = Path(__file__).resolve().parent.parent / "evals" / "golden_dataset.json"


class TestLoadGoldenDataset:
    def test_loads_shipped_dataset(self):
        cases = load_golden_dataset(GOLDEN_DATASET_PATH)
        assert cases
        assert all(case.question for case in cases)
        assert any(case.expect_escalation for case in cases)

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(GoldenDatasetError):
            load_golden_dataset(tmp_path / "missing.json")

    def test_invalid_json_raises(self, tmp_path: Path):
        path = tmp_path / "bad.json"
        path.write_text("not json", encoding="utf-8")
        with pytest.raises(GoldenDatasetError):
            load_golden_dataset(path)

    def test_entry_without_question_raises(self, tmp_path: Path):
        path = tmp_path / "cases.json"
        path.write_text(json.dumps([{"id": "x"}]), encoding="utf-8")
        with pytest.raises(GoldenDatasetError):
            load_golden_dataset(path)

    def test_empty_dataset_raises(self, tmp_path: Path):
        path = tmp_path / "cases.json"
        path.write_text("[]", encoding="utf-8")
        with pytest.raises(GoldenDatasetError):
            load_golden_dataset(path)


class TestEvaluateRag:
    async def test_report_scores_answers_and_escalations(self, tmp_path: Path):
        path = tmp_path / "cases.json"
        path.write_text(
            json.dumps(
                [
                    {
                        "id": "answerable",
                        "question": "What are the OPD timings?",
                        "expected_keywords": ["9 AM"],
                    },
                    {
                        "id": "keyword-miss",
                        "question": "What are the OPD timings?",
                        "expected_keywords": ["midnight"],
                    },
                    {
                        "id": "emergency",
                        "question": "He is having a heart attack",
                        "expect_escalation": True,
                    },
                ]
            ),
            encoding="utf-8",
        )
        cases = load_golden_dataset(path)
        service, _ = make_service([make_chunk(0.9)], llm=FakeLLM("OPD runs 9 AM to 5 PM [1]."))

        report = await evaluate_rag(service, hospital_id=uuid.uuid4(), cases=cases)

        by_id = {result.case_id: result for result in report.results}
        assert by_id["answerable"].passed
        assert not by_id["keyword-miss"].passed
        assert by_id["keyword-miss"].missing_keywords == ["midnight"]
        assert by_id["emergency"].passed and by_id["emergency"].escalated
        assert report.total == 3
        assert report.passed == 2
        assert report.pass_rate == round(2 / 3, 4)
        assert report.escalation_accuracy == 1.0

    async def test_unexpected_escalation_fails_case(self):
        # Nothing relevant in the knowledge base -> escalation, but the case expects an answer.
        cases = load_golden_dataset(GOLDEN_DATASET_PATH)
        answerable = [case for case in cases if not case.expect_escalation][:1]
        service, _ = make_service([make_chunk(0.1)])

        report = await evaluate_rag(service, hospital_id=uuid.uuid4(), cases=answerable)

        assert report.results[0].escalated
        assert not report.results[0].passed
        assert report.escalation_accuracy == 0.0
