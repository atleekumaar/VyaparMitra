"""
Unit tests for Grounding verification in VyaparMitra Copilot.
"""

import pytest
from src.copilot.schemas import BusinessContext, Fact
from src.copilot.validation.grounding import GroundingChecker


def test_extract_numbers():
    text = "Revenue was ₹15,510.50 across 25 orders with average order value ₹620.40"
    nums = GroundingChecker.extract_numbers(text)
    assert 15510.5 in nums
    assert 25.0 in nums
    assert 620.4 in nums


def test_extract_entities():
    text = "Product PRD_SNK_01 and customer C03388 need attention."
    ents = GroundingChecker.extract_entities(text)
    assert "PRD_SNK_01" in ents
    assert "C03388" in ents


def test_grounding_verification_pass():
    ctx = BusinessContext(
        intent="SALES_SUMMARY",
        query="Kal kitni sales hui?",
        language="hinglish",
        metrics={"total_revenue": 15000.0, "total_orders": 20},
        facts=[Fact(key="revenue", value=15000.0, source="test")],
    )
    answer = "Aapki total revenue ₹15,000.00 rahi hai aur 20 orders aaye hain."
    is_grounded, num_mismatches, ent_mismatches = GroundingChecker.verify(answer, ctx)
    assert is_grounded is True
    assert len(num_mismatches) == 0


def test_grounding_verification_fail_numeric_hallucination():
    ctx = BusinessContext(
        intent="SALES_SUMMARY",
        query="Kal kitni sales hui?",
        language="hinglish",
        metrics={"total_revenue": 15000.0, "total_orders": 20},
    )
    # LLM hallucinated ₹99,999
    answer = "Aapki total sales ₹99,999.00 hui hai."
    is_grounded, num_mismatches, ent_mismatches = GroundingChecker.verify(answer, ctx)
    assert is_grounded is False
    assert len(num_mismatches) > 0
