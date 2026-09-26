"""
Context Builder for VyaparMitra Copilot.
Orchestrates business query retrieval from Phases 1-4 and domain knowledge retrieval,
producing a structured BusinessContext object for grounded prompt synthesis.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.copilot.retrieval.business_query import BusinessQueryEngine
from src.copilot.retrieval.knowledge_retriever import KnowledgeRetriever
from src.copilot.schemas import BusinessContext, Fact, Intent, QueryPlan, SourceReference


class ContextBuilder:
    """
    Constructs a complete, grounded BusinessContext from Phase 1-4 data marts and knowledge base.
    """

    def __init__(
        self,
        query_engine: Optional[BusinessQueryEngine] = None,
        knowledge_retriever: Optional[KnowledgeRetriever] = None,
    ):
        self.query_engine = query_engine or BusinessQueryEngine()
        self.knowledge_retriever = knowledge_retriever or KnowledgeRetriever()

    def build_context(
        self,
        query_plan: QueryPlan,
        query: str,
        merchant_id: Optional[str] = None,
    ) -> BusinessContext:
        """
        Builds the consolidated BusinessContext based on the query plan.
        """
        m_id = merchant_id or query_plan.merchant_id
        intent = query_plan.intent
        entities = query_plan.entities

        facts: List[Fact] = []
        metrics: Dict[str, Any] = {}
        recommendations: List[Dict[str, Any]] = []
        evidence: List[Dict[str, Any]] = []
        source_refs: List[SourceReference] = []
        limitations: List[str] = []
        knowledge_snippets: List[str] = []

        # 1. Dispatch to BusinessQueryEngine based on intent
        if intent == Intent.SALES_SUMMARY:
            time_range = query_plan.time_range or entities.get("time_range")
            res = self.query_engine.get_sales_summary(merchant_id=m_id, time_range=time_range)
            metrics.update(res.get("metrics", {}))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent == Intent.SALES_TREND:
            time_range = query_plan.time_range or entities.get("time_range")
            res = self.query_engine.get_sales_trend(merchant_id=m_id, time_range=time_range)
            metrics.update(res.get("metrics", {}))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent == Intent.SALES_FORECAST:
            time_range = query_plan.time_range or entities.get("time_range")
            res = self.query_engine.get_sales_forecast(merchant_id=m_id, horizon=time_range)
            metrics.update(res.get("metrics", {}))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))
            limitations.append("Sales forecast horizon is currently trained for 7-day predictive window.")

        elif intent == Intent.PRODUCT_PERFORMANCE:
            product_id = query_plan.product_id or entities.get("product_id")
            category = query_plan.category or entities.get("category")
            res = self.query_engine.get_product_performance(merchant_id=m_id, product_id=product_id, category=category)
            metrics.update(res.get("metrics", {}))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent == Intent.PRODUCT_DEMAND_FORECAST:
            product_id = query_plan.product_id or entities.get("product_id")
            res = self.query_engine.get_product_demand_forecast(merchant_id=m_id, product_id=product_id)
            metrics.update(res.get("metrics", {}))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))
            limitations.append("SKU-level demand forecast is projected over the upcoming 7-day cycle.")

        elif intent == Intent.CUSTOMER_RISK:
            customer_id = query_plan.customer_id or entities.get("customer_id")
            res = self.query_engine.get_customer_risk(merchant_id=m_id, customer_id=customer_id)
            metrics.update(res.get("metrics", {}))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent == Intent.INVENTORY_RECOMMENDATION:
            product_id = query_plan.product_id or entities.get("product_id")
            res = self.query_engine.get_inventory_recommendations(merchant_id=m_id, product_id=product_id)
            recommendations.extend(res.get("recommendations", []))
            evidence.extend(res.get("evidence", []))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent == Intent.CROSS_SELL:
            product_id = query_plan.product_id or entities.get("product_id")
            res = self.query_engine.get_cross_sell_recommendations(merchant_id=m_id, product_id=product_id)
            recommendations.extend(res.get("recommendations", []))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent == Intent.PRICING_RECOMMENDATION:
            product_id = query_plan.product_id or entities.get("product_id")
            res = self.query_engine.get_pricing_recommendations(merchant_id=m_id, product_id=product_id)
            recommendations.extend(res.get("recommendations", []))
            evidence.extend(res.get("evidence", []))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent == Intent.DAILY_ACTION_PLAN:
            res = self.query_engine.get_daily_action_plan(merchant_id=m_id)
            recommendations.extend(res.get("recommendations", []))
            metrics.update(res.get("metrics", {}))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent == Intent.RECOMMENDATION_EXPLANATION:
            rec_id = entities.get("recommendation_id")
            res = self.query_engine.get_recommendation_explanation(merchant_id=m_id, recommendation_id=rec_id)
            evidence.extend(res.get("evidence", []))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent in (Intent.GENERAL_BUSINESS_SUMMARY, Intent.EXECUTIVE_BRIEF):
            res = self.query_engine.get_general_business_summary(merchant_id=m_id)
            metrics.update(res.get("metrics", {}))
            recommendations.extend(res.get("recommendations", []))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent == Intent.BENCHMARK:
            res = self.query_engine.get_benchmark(merchant_id=m_id)
            metrics.update(res.get("metrics", {}))
            recommendations.extend(res.get("recommendations", []))
            facts.extend(res.get("facts", []))
            source_refs.extend(res.get("sources", []))

        elif intent == Intent.OUT_OF_DOMAIN:
            limitations.append("Query is outside VyaparMitra's merchant intelligence domain.")

        # 2. Domain Knowledge Retrieval
        needs_kb = (
            query_plan.needs_knowledge
            or intent in (
                Intent.GLOSSARY_EXPLANATION,
                Intent.HELP_CAPABILITIES,
                Intent.GREETING,
            )
            or len(facts) == 0
        )

        if needs_kb:
            kb_query = query
            kb_facts, kb_sources = self.knowledge_retriever.get_facts_and_sources(kb_query, top_k=2)
            facts.extend(kb_facts)
            source_refs.extend(kb_sources)
            for f in kb_facts:
                knowledge_snippets.append(f"{f.key}: {f.value}")

        # Always add standard grounded limitation
        limitations.append("VyaparMitra answers are strictly grounded in validated transaction, ML, and decision artifacts.")

        return BusinessContext(
            intent=intent.value,
            query=query,
            language=query_plan.response_language.value,
            facts=facts,
            metrics=metrics,
            recommendations=recommendations,
            evidence=evidence,
            source_references=source_refs,
            limitations=limitations,
            knowledge_snippets=knowledge_snippets,
        )
