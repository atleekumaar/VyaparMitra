"""
Unit tests for VyaparMitra Phase 5 Entity Extraction.
"""

import pytest
from src.copilot.intent.entities import EntityExtractor, extract_entities


def test_extract_product_id():
    extractor = EntityExtractor()
    res = extractor.extract("PRD_SNK_01 ki bikri kitni hui?")
    assert res.get("product_id") == "PRD_SNK_01"

    res2 = extract_entities("Check stock for sku-021 please")
    assert "021" in res2.get("product_id", "")


def test_extract_customer_id():
    res = extract_entities("Customer C03388 ka risk score batao")
    assert res.get("customer_id") == "C03388"


def test_extract_category():
    res = extract_entities("Bakery items ki sales kahan ja rahi hai?")
    assert res.get("category") == "Bakery"


def test_extract_time_range():
    res = extract_entities("Kal kitni sales hui thi?")
    assert res.get("time_range") == "kal"


def test_extract_anaphora():
    res = extract_entities("Aur uska demand forecast kya hai?")
    assert res.get("has_anaphora") is True
