"""
Entity extraction for merchant business queries.
Extracts product IDs, customer IDs, categories, dates, time ranges, and business metrics.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

KNOWN_CATEGORIES = [
    "accessories", "apparel", "art supplies", "baby care", "bakery", "beverages",
    "books", "cleaning", "dairy", "electronics", "footwear", "grocery", "health",
    "home decor", "kitchen", "personal care", "pet supplies", "snacks", "sports",
    "stationery", "toys",
]

PRODUCT_ID_REGEX = re.compile(r"\b(prd_[a-z0-9_]+|sku[-_][0-9]+|product\s+[a-z0-9]+)\b", re.IGNORECASE)
CUSTOMER_ID_REGEX = re.compile(r"\b(c[0-9]{3,6}|customer[-_]c[0-9]{3,6})\b", re.IGNORECASE)
TIME_RANGE_REGEX = re.compile(
    r"\b(today|yesterday|aaj|kal|parson|march|april|may|june|july|august|september|"
    r"october|november|december|next 7 days|last 7 days|last 30 days|agle hafte|pichle hafte)\b",
    re.IGNORECASE
)
METRIC_REGEX = re.compile(
    r"\b(sales|revenue|bikri|units|demand|margin|munafa|discount|aov|churn|risk|volume)\b",
    re.IGNORECASE
)
ANAPHORA_REGEX = re.compile(r"\b(uska|uski|iske|iska|iski|unka|it|that|this product)\b", re.IGNORECASE)


def extract_entities(query: str) -> Dict[str, Any]:
    """Extracts structured entities from merchant query string."""
    q_lower = query.lower()
    entities: Dict[str, Any] = {}

    # 1. Product ID
    p_match = PRODUCT_ID_REGEX.search(q_lower)
    if p_match:
        raw_p = p_match.group(1).upper()
        # Normalize SKU-021 or Product A
        if raw_p.startswith("PRODUCT "):
            raw_p = "PRD_" + raw_p.split()[1]
        elif raw_p.startswith("SKU-"):
            raw_p = "PRD_SKU_" + raw_p.split("-")[1]
        entities["product_id"] = raw_p

    # 2. Customer ID
    c_match = CUSTOMER_ID_REGEX.search(q_lower)
    if c_match:
        entities["customer_id"] = c_match.group(1).upper()

    # 3. Category
    for cat in KNOWN_CATEGORIES:
        if cat in q_lower:
            entities["category"] = cat.title()
            break

    # 4. Time Range
    t_match = TIME_RANGE_REGEX.search(q_lower)
    if t_match:
        entities["time_range"] = t_match.group(1).lower()

    # 5. Metric
    m_match = METRIC_REGEX.search(q_lower)
    if m_match:
        entities["metric"] = m_match.group(1).lower()

    # 6. Has Anaphoric Reference (pronoun referring to previous turn)
    if ANAPHORA_REGEX.search(q_lower):
        entities["has_anaphora"] = True

    return entities


class EntityExtractor:
    """Class wrapper for entity extraction."""

    def extract(self, query: str) -> Dict[str, Any]:
        return extract_entities(query)

