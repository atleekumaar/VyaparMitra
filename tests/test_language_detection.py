"""
Unit tests for VyaparMitra Phase 5 Language Detection & Normalization.
"""

import pytest
from src.copilot.language.detector import LanguageDetector, detect_language
from src.copilot.language.normalizer import LanguageNormalizer, normalize_text
from src.copilot.schemas import Language


def test_detect_hindi_devanagari():
    detector = LanguageDetector()
    assert detector.detect("मेरी कुल बिक्री कितनी रही है?") == Language.HINDI
    assert detect_language("नमस्ते, मुझे आज का प्लान बताएं") == Language.HINDI
    assert detect_language("दुकान में कौन सा सामान खत्म होने वाला है?") == Language.HINDI


def test_detect_hinglish():
    detector = LanguageDetector()
    assert detector.detect("Kal kitni bikri hui thi?") == Language.HINGLISH
    assert detect_language("Agle hafte sales kitni hogi?") == Language.HINGLISH
    assert detect_language("Kaunsa maal khatam hone wala hai?") == Language.HINGLISH
    assert detect_language("Aaj dukaan mein kya karna chahiye?") == Language.HINGLISH
    assert detect_language("mera munafa aur sales batao") == Language.HINGLISH


def test_detect_english():
    detector = LanguageDetector()
    assert detector.detect("What is the 7-day sales forecast?") == Language.ENGLISH
    assert detect_language("Show me high-risk customers") == Language.ENGLISH
    assert detect_language("Give me the daily action plan") == Language.ENGLISH
    assert detect_language("Which products need restocking today?") == Language.ENGLISH


def test_normalize_text():
    normalizer = LanguageNormalizer()
    raw = "bhaiya zyaada bikri pehele hui thi kyuu???"
    norm = normalizer.normalize(raw)
    assert "zyada" in norm
    assert "pehle" in norm
    assert "kyun" in norm
    assert not norm.endswith("???")


def test_empty_query_fallback():
    assert detect_language("") == Language.HINGLISH
    assert normalize_text("") == ""
