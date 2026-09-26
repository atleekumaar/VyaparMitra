"""
Unit tests for ResponseValidator and anti-hallucination auto-correction.
"""

import pytest
from src.copilot.schemas import BusinessContext
from src.copilot.validation.response_validator import ResponseValidator


def test_validator_passes_grounded_response():
    validator = ResponseValidator(enforce_strict=True)
    ctx = BusinessContext(
        intent="SALES_SUMMARY",
        query="Kitni bikri hui?",
        language="hinglish",
        metrics={"total_revenue": 50000.0, "total_orders": 40, "average_order_value": 1250.0},
    )
    grounded_ans = "Aapki total bikri ₹50,000.00 rahi hai, jisme 40 orders aaye hain."
    res = validator.validate(grounded_ans, ctx)
    assert res.valid is True


def test_validator_detects_empty_response():
    validator = ResponseValidator(enforce_strict=True)
    ctx = BusinessContext(
        intent="SALES_SUMMARY",
        query="Kitni bikri hui?",
        language="hinglish",
    )
    res = validator.validate("", ctx)
    assert res.valid is False
    assert "empty" in res.unsupported_claims[0].lower()


def test_validator_auto_corrects_hallucinated_response():
    validator = ResponseValidator(enforce_strict=True)
    ctx = BusinessContext(
        intent="SALES_SUMMARY",
        query="Kitni bikri hui?",
        language="hinglish",
        metrics={"total_revenue": 50000.0, "total_orders": 40, "average_order_value": 1250.0},
    )
    hallucinated = "Total sales were ₹999,999 with 5000 orders."
    safe_ans, val_res = validator.validate_and_sanitize(hallucinated, ctx)

    assert val_res.valid is True
    assert "₹50,000.00" in safe_ans
    assert "999,999" not in safe_ans
