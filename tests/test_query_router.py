"""
Unit tests for VyaparMitra Phase 5 Query Router.
"""

import pytest
from src.copilot.conversation.state import ConversationState
from src.copilot.intent.router import QueryRouter
from src.copilot.schemas import Intent, Language


def test_route_simple_query():
    router = QueryRouter()
    plan = router.route("Kal kitni bikri hui thi?")
    assert plan.intent == Intent.SALES_SUMMARY
    assert plan.response_language == Language.HINGLISH
    assert "phase2.sales" in plan.required_sources


def test_route_anaphora_resolution():
    router = QueryRouter()
    state = ConversationState()
    state.last_product_id = "PRD_SNK_01"

    plan = router.route("Aur iska demand forecast kitna hai?", state=state)
    assert plan.intent == Intent.PRODUCT_DEMAND_FORECAST
    assert plan.product_id == "PRD_SNK_01"


def test_route_language_override():
    router = QueryRouter()
    plan = router.route("Kal kitni bikri hui thi?", language=Language.ENGLISH)
    assert plan.response_language == Language.ENGLISH
