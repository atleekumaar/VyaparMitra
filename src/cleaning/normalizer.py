"""
Product Name Normalization and Fuzzy Matching Utility for Retail Ingestion.
Standardizes noisy merchant entries, variations in casing, punctuation, and units.
"""
from __future__ import annotations
import difflib
import re
from typing import Dict, List, Optional, Sequence


def normalize_product_string(name: str) -> str:
    """Cleans punctuation, extra spacing, and standardizes retail unit notations."""
    if not isinstance(name, str):
        return ""
    
    text = name.strip().lower()
    # Normalize unit variations (e.g., 500 gm -> 500g, 1 kg -> 1kg, 1 ltr -> 1l)
    text = re.sub(r'(\d+)\s*(gm|grms|grams)\b', r'\1g', text)
    text = re.sub(r'(\d+)\s*(kg|kgs|kilo|kilograms)\b', r'\1kg', text)
    text = re.sub(r'(\d+)\s*(ml|milliliters)\b', r'\1ml', text)
    text = re.sub(r'(\d+)\s*(l|ltr|liters|litre)\b', r'\1l', text)
    
    # Strip non-alphanumeric punctuation (keep letters, digits, whitespace)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = [tok for tok in text.split() if tok]
    
    # Capitalize brand/product words while preserving unit casing (e.g., 500g, 1kg)
    formatted_tokens = []
    for tok in tokens:
        if re.match(r'^\d+[a-z]+$', tok):
            formatted_tokens.append(tok)
        else:
            formatted_tokens.append(tok.capitalize())
            
    return " ".join(formatted_tokens)


class ProductFuzzyMatcher:
    """Fuzzy matching engine to map noisy retail spellings to canonical SKUs."""
    def __init__(self, canonical_names: Sequence[str], cutoff: float = 0.75):
        self.canonical_names = list(canonical_names)
        self.normalized_map: Dict[str, str] = {
            normalize_product_string(name): name for name in self.canonical_names
        }
        self.cutoff = cutoff

    def match(self, query: str) -> str:
        """Returns the best canonical product match if above cutoff, else normalized query."""
        cleaned_query = normalize_product_string(query)
        if not cleaned_query:
            return query
        
        # Exact normalized match
        if cleaned_query in self.normalized_map:
            return self.normalized_map[cleaned_query]

        # Fuzzy lookup using SequenceMatcher
        matches = difflib.get_close_matches(
            cleaned_query, 
            list(self.normalized_map.keys()), 
            n=1, 
            cutoff=self.cutoff
        )
        if matches:
            return self.normalized_map[matches[0]]
        
        return cleaned_query
