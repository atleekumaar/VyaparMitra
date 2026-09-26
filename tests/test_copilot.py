"""
End-to-End tests for VyaparMitraCopilot facade.
"""

import pytest
from src.copilot.copilot import VyaparMitraCopilot
from src.copilot.schemas import Language


@pytest.fixture
def copilot():
    return VyaparMitraCopilot()


def test_copilot_ask_sales(copilot):
    resp = copilot.ask("Kal kitni bikri hui thi?")
    assert resp.answer != ""
    assert resp.intent == "SALES_SUMMARY"
    assert resp.language == "hinglish"
    assert len(resp.sources) > 0
    assert resp.validation.valid is True


def test_copilot_ask_hindi(copilot):
    resp = copilot.ask("मेरी कुल बिक्री कितनी रही है?", language_override=Language.HINDI)
    assert resp.language == "hi"
    assert "कुल बिक्री" in resp.answer
    assert resp.validation.valid is True


def test_copilot_ask_english(copilot):
    resp = copilot.ask("What is the 7-day sales forecast?", language_override=Language.ENGLISH)
    assert resp.language == "en"
    assert "forecasted total revenue" in resp.answer
    assert resp.validation.valid is True


def test_copilot_daily_brief(copilot):
    brief = copilot.generate_daily_brief()
    assert brief.answer != ""
    assert len(brief.recommendations) > 0
    assert brief.validation.valid is True


def test_copilot_out_of_domain(copilot):
    resp = copilot.ask("Who is the prime minister?")
    assert resp.intent == "OUT_OF_DOMAIN"
    assert "dukaan" in resp.answer.lower() or "vyapar" in resp.answer.lower() or "business" in resp.answer.lower()
