"""
Unit tests for MockProvider deterministic generation across languages.
"""

import pytest
from src.copilot.llm.mock_provider import MockProvider
from src.copilot.schemas import BusinessContext


def test_mock_llm_hindi():
    provider = MockProvider()
    ctx = BusinessContext(
        intent="SALES_SUMMARY",
        query="मेरी कुल बिक्री बताओ",
        language="hi",
        metrics={"total_revenue": 10000.0, "total_orders": 10, "average_order_value": 1000.0},
    )
    ans = provider.generate("मेरी कुल बिक्री बताओ", ctx)
    assert "कुल बिक्री" in ans
    assert "₹10,000.00" in ans


def test_mock_llm_hinglish():
    provider = MockProvider()
    ctx = BusinessContext(
        intent="SALES_SUMMARY",
        query="Meri bikri kitni hui?",
        language="hinglish",
        metrics={"total_revenue": 10000.0, "total_orders": 10, "average_order_value": 1000.0},
    )
    ans = provider.generate("Meri bikri kitni hui?", ctx)
    assert "total bikri" in ans
    assert "₹10,000.00" in ans


def test_mock_llm_english():
    provider = MockProvider()
    ctx = BusinessContext(
        intent="SALES_SUMMARY",
        query="What was my revenue?",
        language="en",
        metrics={"total_revenue": 10000.0, "total_orders": 10, "average_order_value": 1000.0},
    )
    ans = provider.generate("What was my revenue?", ctx)
    assert "total sales revenue" in ans
    assert "₹10,000.00" in ans
