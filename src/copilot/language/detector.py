"""
Language detection module for Hindi, Hinglish, and English merchant queries.
Distinguishes Devanagari Hindi, Latin Hinglish, and English with conflict resolution.
"""

from __future__ import annotations

import re
from src.copilot.schemas import Language

# Devanagari Unicode character range
DEVANAGARI_REGEX = re.compile(r"[\u0900-\u097F]")

# Exclusive Latin Hinglish markers (unambiguous Hindi words in Latin script)
UNAMBIGUOUS_HINGLISH_MARKERS = {
    "aaj", "kal", "parson", "meri", "mera", "mere", "humara", "apna", "apni",
    "kitni", "kitna", "kitne", "bikri", "bikta", "bikti", "batao", "bataiye", "bata",
    "karna", "chahiye", "chahie", "karein", "kare", "karo", "kaunsa", "kaunse", "kaunsi",
    "grahak", "dukan", "dukaan", "hai", "hain", "tha", "thi", "raha", "rahi", "rahe",
    "hogi", "hoga", "honge", "kisko", "kise", "kyun", "kyu", "maal", "kya", "zyada", "jyada",
    "kam", "saath", "bech", "bechna", "pehle", "kaise", "kaisa", "kaisi", "kahan",
    "khareedte", "kharid", "kharidte", "bacha", "pichle", "pichhla", "pichhle", "agle",
    "sabse", "badhegi", "badh", "gir", "girna", "chhod", "rok", "mujhko", "mujhe",
    "ab", "abhi", "bhai", "sahab", "fayda", "nuksan", "munafa",
    "namaste", "pranam", "dhanyawad", "shukriya",
}

# Strong English markers
ENGLISH_MARKERS = {
    "what", "is", "are", "how", "why", "who", "which", "where", "when", "can",
    "you", "tell", "give", "show", "me", "my", "our", "the", "this", "that",
    "these", "those", "forecast", "revenue", "sales", "order", "orders", "product",
    "products", "customer", "customers", "inventory", "stock", "price", "pricing",
    "plan", "today", "yesterday", "tomorrow", "week", "month", "days",
}


def detect_language(query: str) -> Language:
    """
    Detects whether a merchant query is in Hindi (Devanagari), Hinglish (Latin Hindi), or English.
    """
    text = query.strip()
    if not text:
        return Language.HINGLISH

    # 1. Check for Devanagari script presence
    devanagari_chars = DEVANAGARI_REGEX.findall(text)
    total_alpha = sum(1 for c in text if c.isalpha())
    if devanagari_chars and total_alpha > 0:
        dev_ratio = len(devanagari_chars) / total_alpha
        if dev_ratio >= 0.15:
            return Language.HINDI

    # 2. Tokenize Latin text and count language markers
    tokens = [t.lower().strip(".,?!:;\"'()") for t in text.split()]

    hinglish_count = sum(1 for t in tokens if t in UNAMBIGUOUS_HINGLISH_MARKERS)
    english_count = sum(1 for t in tokens if t in ENGLISH_MARKERS)

    # 3. Decision logic
    if hinglish_count > 0 and hinglish_count >= english_count:
        return Language.HINGLISH
    elif hinglish_count > 0 and english_count > 0:
        # Code-mixed query with both Hindi verbs/pronouns and English nouns -> Hinglish
        return Language.HINGLISH
    elif english_count > 0:
        return Language.ENGLISH

    # Fallback to English if standard Latin without Hinglish indicators
    return Language.ENGLISH


class LanguageDetector:
    """Class wrapper for language detection."""

    def detect(self, query: str) -> Language:
        return detect_language(query)
