"""
Unit tests for ConversationState and multi-turn anaphora tracking.
"""

import pytest
from src.copilot.conversation.state import ConversationState
from src.copilot.schemas import Intent, Language


def test_state_records_turns():
    state = ConversationState(max_turns=3)
    state.record_turn(
        query="PRD_SNK_01 ka sales batao",
        answer="Sales is ₹5000",
        intent=Intent.PRODUCT_PERFORMANCE,
        entities={"product_id": "PRD_SNK_01"},
        language=Language.HINGLISH,
    )
    assert len(state.turns) == 1
    assert state.last_product_id == "PRD_SNK_01"
    assert state.last_intent == Intent.PRODUCT_PERFORMANCE


def test_state_anaphora_resolution():
    state = ConversationState()
    state.record_turn(
        query="PRD_SNK_01 ka sales batao",
        answer="Sales is ₹5000",
        intent=Intent.PRODUCT_PERFORMANCE,
        entities={"product_id": "PRD_SNK_01"},
        language=Language.HINGLISH,
    )

    resolved = state.update_with_query_entities(
        intent=Intent.PRODUCT_DEMAND_FORECAST,
        entities={"has_anaphora": True},
    )
    assert resolved.get("product_id") == "PRD_SNK_01"


def test_state_bounded_history():
    state = ConversationState(max_turns=2)
    for i in range(5):
        state.record_turn(
            query=f"Query {i}",
            answer=f"Answer {i}",
            intent=Intent.SALES_SUMMARY,
            entities={},
            language=Language.ENGLISH,
        )
    assert len(state.turns) == 2
    assert state.turns[-1]["query"] == "Query 4"
