"""
Query router and planner for VyaparMitra Copilot.
Combines language detection, intent classification, and entity resolution into an executable QueryPlan.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.copilot.intent.classifier import classify_intent
from src.copilot.intent.entities import extract_entities
from src.copilot.language.detector import detect_language
from src.copilot.language.normalizer import normalize_text
from src.copilot.schemas import Intent, Language, QueryPlan

INTENT_SOURCE_MAP: Dict[Intent, List[str]] = {
    Intent.SALES_SUMMARY: ["phase2.sales", "phase1.features"],
    Intent.SALES_TREND: ["phase2.trends", "phase3.trends"],
    Intent.SALES_FORECAST: ["phase3.sales_forecast", "phase2.sales"],
    Intent.PRODUCT_PERFORMANCE: ["phase2.products", "phase1.products"],
    Intent.PRODUCT_DEMAND_FORECAST: ["phase3.demand_forecast", "phase1.products"],
    Intent.INVENTORY_RECOMMENDATION: ["phase4.inventory", "phase3.demand_forecast", "phase1.products"],
    Intent.CUSTOMER_ANALYSIS: ["phase2.customers", "phase1.customers"],
    Intent.CUSTOMER_RISK: ["phase3.customer_risk", "phase2.customers"],
    Intent.RETENTION_RECOMMENDATION: ["phase4.customer_retention", "phase3.customer_risk"],
    Intent.CROSS_SELL: ["phase4.cross_sell", "phase1.transactions"],
    Intent.PRICING_RECOMMENDATION: ["phase4.pricing", "phase1.products"],
    Intent.BUSINESS_TREND: ["phase3.trends", "phase2.trends"],
    Intent.ANOMALY: ["phase2.anomalies", "phase2.sales"],
    Intent.DAILY_ACTION_PLAN: ["phase4.action_plan", "phase4.all_recommendations"],
    Intent.PAYMENT_ANALYSIS: ["phase2.payments"],
    Intent.CATEGORY_ANALYSIS: ["phase2.categories", "phase2.products"],
    Intent.TIME_ANALYSIS: ["phase2.time"],
    Intent.RECOMMENDATION_EXPLANATION: ["phase4.evidence", "phase4.all_recommendations", "knowledge.recommendations"],
    Intent.GENERAL_BUSINESS_SUMMARY: ["phase2.sales", "phase3.trends", "phase4.action_plan"],
    Intent.OUT_OF_DOMAIN: ["knowledge.capabilities"],
    Intent.UNKNOWN: ["knowledge.faq"],
}


class QueryRouter:
    """Parses user queries and builds structured execution plans."""

    def route(
        self,
        query: str,
        conversation_state: Optional[Any] = None,
        merchant_id: Optional[str] = None,
        language: Optional[Language] = None,
        state: Optional[Any] = None,
    ) -> QueryPlan:
        """Translates user utterance into a targeted QueryPlan."""
        c_state = state or conversation_state
        lang = language or detect_language(query)
        intent = classify_intent(query)
        entities = extract_entities(query)

        # Multi-turn conversational entity resolution (anaphora)
        if c_state is not None:
            last_prd = getattr(c_state, "last_product_id", None) or getattr(c_state, "last_product", None)
            last_cust = getattr(c_state, "last_customer_id", None) or getattr(c_state, "last_customer", None)
            last_cat = getattr(c_state, "last_category", None)

            if entities.get("has_anaphora") or intent in (Intent.PRODUCT_DEMAND_FORECAST, Intent.PRODUCT_PERFORMANCE):
                if not entities.get("product_id") and last_prd:
                    entities["product_id"] = last_prd
                if not entities.get("customer_id") and last_cust:
                    entities["customer_id"] = last_cust
                if not entities.get("category") and last_cat:
                    entities["category"] = last_cat

            # If user asks a follow up like "aur uska forecast?", adapt intent
            if entities.get("product_id") and intent in [Intent.SALES_SUMMARY, Intent.GENERAL_BUSINESS_SUMMARY]:
                if any(w in query.lower() for w in ["forecast", "demand", "bikega", "next", "anumaan"]):
                    intent = Intent.PRODUCT_DEMAND_FORECAST

        m_id = merchant_id or entities.get("merchant_id")
        if not m_id and c_state is not None:
            m_id = getattr(c_state, "merchant_id", None)

        required_sources = INTENT_SOURCE_MAP.get(intent, ["phase2.sales", "phase4.action_plan"])

        return QueryPlan(
            intent=intent,
            entities=entities,
            time_range=entities.get("time_range"),
            merchant_id=m_id,
            product_id=entities.get("product_id"),
            customer_id=entities.get("customer_id"),
            category=entities.get("category"),
            required_sources=required_sources,
            response_language=lang,
        )
