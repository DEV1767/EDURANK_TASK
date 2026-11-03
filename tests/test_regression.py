import os
import sys
import pytest
from pathlib import Path

# Ensure project root is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.assistant import SupportAssistant
from src.order_service import OrderService
from src.retriever import KnowledgeBaseRetriever
from src.guardrails import EscalationGuardrail


@pytest.fixture(scope="module")
def assistant():
    docs_dir = str(Path(__file__).resolve().parent.parent / "data" / "docs")
    orders_path = str(Path(__file__).resolve().parent.parent / "data" / "orders.json")
    return SupportAssistant(docs_dir, orders_path)


@pytest.fixture(scope="module")
def order_service():
    orders_path = str(Path(__file__).resolve().parent.parent / "data" / "orders.json")
    return OrderService(orders_path)


def test_retrieval_filters_obsolete():
    """Verify that obsolete 2022 policies are never retrieved for public queries."""
    docs_dir = str(Path(__file__).resolve().parent.parent / "data" / "docs")
    retriever = KnowledgeBaseRetriever(docs_dir)
    results = retriever.retrieve("Can I return opened items?", top_k=5)
    for doc in results:
        assert doc.metadata.get("status") == "ACTIVE"
        assert "2022" not in doc.metadata.get("source", "")


def test_order_service_cancellation_window(order_service):
    """Verify 30-minute order cancellation policy logic."""
    # ORD-1002 placed 10 mins ago -> Eligible
    res_eligible = order_service.check_cancellation_eligibility("ORD-1002")
    assert res_eligible["success"] is True
    assert res_eligible["can_cancel"] is True

    # ORD-1001 placed 45 days ago -> Ineligible
    res_ineligible = order_service.check_cancellation_eligibility("ORD-1001")
    assert res_ineligible["success"] is True
    assert res_ineligible["can_cancel"] is False


def test_order_service_missing_order(order_service):
    """Verify missing orders return graceful error without crashing."""
    res = order_service.get_order("ORD-0000-NONEXISTENT")
    assert res["success"] is False
    assert "not found" in res["error"].lower()


def test_safety_escalation_guardrail():
    """Verify fire emergency triggers critical escalation immediately."""
    guard = EscalationGuardrail()
    res = guard.evaluate("The charger caught fire and is smoking on my rug!")
    assert res["should_escalate"] is True
    assert res["priority"] == "CRITICAL"
    assert res["target_queue"] == "#support-safety"


def test_legal_threat_escalation():
    """Verify attorney/FTC threat triggers legal escalation queue."""
    guard = EscalationGuardrail()
    res = guard.evaluate("I am contacting my attorney to file a formal FTC lawsuit!")
    assert res["should_escalate"] is True
    assert res["priority"] == "HIGH"
    assert res["target_queue"] == "#legal-escalate"


def test_assistant_restocking_fee(assistant):
    """Verify that assistant correctly states the $5.00 restocking fee on electronics."""
    res = assistant.answer_query("How much is the restocking fee for returned electronics?")
    assert "$5" in res["answer"]
    assert any("Return_refund_policy_2024.md" in src for src in res["sources"])


def test_assistant_safe_refusal(assistant):
    """Verify assistant safely refuses to invent policy on unanswerable topics."""
    res = assistant.answer_query("Do you offer custom gold foil engraving on insulated bottles?")
    lower_ans = res["answer"].lower()
    refusal_indicators = ["do not have information", "not have information", "cannot", "please contact", "not available"]
    assert any(ind in lower_ans for ind in refusal_indicators)

