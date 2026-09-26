"""
Text normalization for merchant business queries.
Cleans punctuation, standardizes spacing, and normalizes common phonetic spellings.
"""

from __future__ import annotations

import re

PHONETIC_REPLACEMENTS = {
    r"\bzyaada\b": "zyada",
    r"\bjyada\b": "zyada",
    r"\bpehele\b": "pehle",
    r"\bchahie\b": "chahiye",
    r"\bkyuu\b": "kyun",
    r"\bkyu\b": "kyun",
    r"\bdukaan\b": "dukan",
    r"\bbatao\b": "batao",
    r"\bbataiye\b": "batao",
    r"\bpichley\b": "pichle",
}


def normalize_text(text: str) -> str:
    """Standardizes input query text for entity and intent extraction."""
    if not text:
        return ""

    cleaned = text.strip()
    # Normalize excessive punctuation
    cleaned = re.sub(r"[?!.,:;]+$", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    lower = cleaned.lower()
    for pattern, repl in PHONETIC_REPLACEMENTS.items():
        lower = re.sub(pattern, repl, lower)

    return lower



class LanguageNormalizer:
    """Class wrapper for language text normalization."""

    @staticmethod
    def normalize(text: str) -> str:
        return normalize_text(text)

