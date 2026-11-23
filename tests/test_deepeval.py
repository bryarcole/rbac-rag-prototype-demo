import json
import os
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from rag_app import index_seed_documents
from workflow import run_enterprise_workflow

# Configurable quality gate thresholds
FAITHFULNESS_THRESHOLD = float(os.getenv("FAITHFULNESS_THRESHOLD", "0.85"))
RELEVANCY_THRESHOLD = float(os.getenv("RELEVANCY_THRESHOLD", "0.80"))
PRECISION_THRESHOLD = float(os.getenv("PRECISION_THRESHOLD", "0.75"))
RECALL_THRESHOLD = float(os.getenv("RECALL_THRESHOLD", "0.75"))
MAX_LATENCY_MS = int(os.getenv("MAX_LATENCY_MS", "6000"))
MAX_COST_USD = float(os.getenv("MAX_COST_USD", "0.01"))

DATASET_PATH = Path(__file__).resolve().parent.parent / "eval_dataset.json"


@pytest.fixture(scope="module", autouse=True)
def boot_vector_store():
    index_seed_documents()


def _load_answered_cases():
    """Returns happy-path & multi-doc cases for full RAG metric scoring."""
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)
    # Limit count via env var (e.g. DEEPEVAL_LIMIT=5) for fast local runs
    answered = [c for c in cases if c["expected_status"] == "answered"]
    limit = int(os.getenv("DEEPEVAL_LIMIT", str(len(answered))))
    return answered[:limit]


@pytest.mark.parametrize("case", _load_answered_cases(), ids=lambda c: c["id"])
def test_rag_deepeval_quality_and_slas(case):
    """
    Scores Faithfulness (>=0.85), Answer Relevancy (>=0.80), Contextual Precision (>=0.75),
    and Contextual Recall (>=0.75), plus hard latency and token-cost SLAs per query.
    Note: DeepEval defaults to OPENAI_API_KEY for its judge LLM; set OPENAI_API_KEY in CI secrets
    or pass a custom Bedrock DeepEvalBaseLLM to each metric.
    """
    rec = run_enterprise_workflow(question=case["question"], user_role=case["role"])

    # 1. Deterministic SLA assertions (latency & token cost)
    assert rec.status == "answered", f"{case['id']}: expected answered, got {rec.status}"
    assert rec.latency_ms <= MAX_LATENCY_MS, f"{case['id']}: latency {rec.latency_ms}ms > {MAX_LATENCY_MS}ms"
    assert rec.estimated_cost_usd <= MAX_COST_USD, (
        f"{case['id']}: cost ${rec.estimated_cost_usd:.6f} > ${MAX_COST_USD:.6f}"
    )

    # 2. DeepEval RAG Triad + Precision/Recall
    test_case = LLMTestCase(
        input=case["question"],
        actual_output=rec.answer,
        expected_output=case["expected_output"],
        retrieval_context=rec.retrieved_contexts,
    )

    metrics = [
        FaithfulnessMetric(threshold=FAITHFULNESS_THRESHOLD, include_reason=True),
        AnswerRelevancyMetric(threshold=RELEVANCY_THRESHOLD, include_reason=True),
        ContextualPrecisionMetric(threshold=PRECISION_THRESHOLD, include_reason=True),
        ContextualRecallMetric(threshold=RECALL_THRESHOLD, include_reason=True),
    ]
    assert_test(test_case, metrics)
