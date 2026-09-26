"""
Unit tests for CopilotService session coordinator.
"""

import pytest
from src.copilot.service import CopilotService


def test_copilot_service_query():
    service = CopilotService()
    res = service.query(session_id="s1", query="Kal kitni sales hui thi?")
    assert "answer" in res
    assert res["intent"] == "SALES_SUMMARY"
    assert res["validation"]["valid"] is True


def test_copilot_service_daily_brief():
    service = CopilotService()
    brief = service.daily_brief(session_id="s2")
    assert "answer" in brief
    assert "recommendations" in brief


def test_copilot_service_sessions():
    service = CopilotService()
    service.get_or_create_copilot("session_a")
    service.get_or_create_copilot("session_b")

    health = service.health_check()
    assert health["active_sessions"] >= 2

    cleared = service.clear_session("session_a")
    assert cleared is True
    assert service.clear_session("non_existent") is False
