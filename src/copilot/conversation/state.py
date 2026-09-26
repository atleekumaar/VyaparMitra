"""
Conversational State and Context Memory for VyaparMitra Copilot.
Maintains bounded turn history, tracks entities across turns, and resolves anaphoric references.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from src.copilot.schemas import Intent, Language


class ConversationState:
    """
    Maintains active multi-turn session state for a merchant conversation.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        merchant_id: Optional[str] = None,
        max_turns: int = 10,
    ):
        self.session_id: str = session_id or str(uuid.uuid4())
        self.merchant_id: Optional[str] = merchant_id
        self.max_turns: int = max_turns

        self.last_language: Optional[Language] = None
        self.last_intent: Optional[Intent] = None
        self.last_product_id: Optional[str] = None
        self.last_customer_id: Optional[str] = None
        self.last_category: Optional[str] = None

        self.turns: List[Dict[str, Any]] = []

    def update_with_query_entities(
        self,
        intent: Intent,
        entities: Dict[str, Any],
        language: Optional[Language] = None,
    ) -> Dict[str, Any]:
        """
        Resolves anaphora and missing entities using state, then updates state.
        Returns the resolved entities dictionary.
        """
        resolved = dict(entities)

        # 1. Product resolution
        if not resolved.get("product_id") and self.last_product_id:
            # If query mentions anaphoric pronoun or intent relates to products
            if resolved.get("has_anaphora") or intent in (
                Intent.PRODUCT_PERFORMANCE,
                Intent.PRODUCT_DEMAND_FORECAST,
                Intent.INVENTORY_RECOMMENDATION,
                Intent.PRICING_RECOMMENDATION,
                Intent.CROSS_SELL,
            ):
                resolved["product_id"] = self.last_product_id

        # 2. Customer resolution
        if not resolved.get("customer_id") and self.last_customer_id:
            if resolved.get("has_anaphora") or intent in (
                Intent.CUSTOMER_RISK,
            ):
                resolved["customer_id"] = self.last_customer_id

        # 3. Category resolution
        if not resolved.get("category") and self.last_category:
            if resolved.get("has_anaphora") or intent in (
                Intent.PRODUCT_PERFORMANCE,
            ):
                resolved["category"] = self.last_category

        return resolved

    def record_turn(
        self,
        query: str,
        answer: str,
        intent: Intent,
        entities: Dict[str, Any],
        language: Language,
    ) -> None:
        """
        Records a completed conversation turn and saves active entities.
        """
        self.last_intent = intent
        self.last_language = language

        if entities.get("product_id"):
            self.last_product_id = entities["product_id"]
        if entities.get("customer_id"):
            self.last_customer_id = entities["customer_id"]
        if entities.get("category"):
            self.last_category = entities["category"]

        turn_entry = {
            "query": query,
            "answer": answer,
            "intent": intent.value,
            "entities": entities,
            "language": language.value,
        }

        self.turns.append(turn_entry)
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def clear(self) -> None:
        """Clears conversational state."""
        self.turns.clear()
        self.last_intent = None
        self.last_product_id = None
        self.last_customer_id = None
        self.last_category = None
