"""
Unit tests for product name normalization and fuzzy matching.
"""
from src.cleaning.normalizer import normalize_product_string, ProductFuzzyMatcher

def test_normalize_product_string():
    assert normalize_product_string("  surf   excel  500 gm ") == "Surf Excel 500g"
    assert normalize_product_string("Aashirvaad Atta 5 kg!") == "Aashirvaad Atta 5kg"
    assert normalize_product_string("Fortune Oil 1 ltr") == "Fortune Oil 1l"

def test_fuzzy_matcher_close_match():
    catalog = ["Surf Excel Quick Wash 500g", "Aashirvaad Superior MP Sharbati Atta 5kg", "Fortune Sunlite Oil 1l"]
    matcher = ProductFuzzyMatcher(catalog, cutoff=0.75)
    
    # Slight typos or spacing variations
    assert matcher.match("Surf Excel Quick Wash 500 gm") == "Surf Excel Quick Wash 500g"
    assert matcher.match("Fortune Sunlite 1l") == "Fortune Sunlite Oil 1l"
