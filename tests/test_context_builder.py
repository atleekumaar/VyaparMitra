"""
Unit tests for VyaparMitra Phase 5 Context Builder and Knowledge Retriever.
"""

import pytest
from src.copilot.intent.router import QueryRouter
from src.copilot.retrieval.context_builder import ContextBuilder
from src.copilot.retrieval.knowledge_retriever import KnowledgeRetriever
from src.copilot.schemas import Intent


def test_knowledge_retriever_search():
    retriever = KnowledgeRetriever()
    results = retriever.search("What is VyaparMitra", top_k=2)
    assert len(results) > 0
    assert "title" in results[0]
    assert "content" in results[0]


def test_context_builder_sales():
    router = QueryRouter()
    builder = ContextBuilder()

    plan = router.route("Kal kitni bikri hui thi?")
    ctx = builder.build_context(query_plan=plan, query="Kal kitni bikri hui thi?")

    assert ctx.intent == Intent.SALES_SUMMARY.value
    assert "total_revenue" in ctx.metrics
    assert len(ctx.facts) > 0
    assert len(ctx.source_references) > 0


def test_context_builder_daily_plan():
    router = QueryRouter()
    builder = ContextBuilder()

    plan = router.route("Aaj mujhe kya karna chahiye?")
    ctx = builder.build_context(query_plan=plan, query="Aaj mujhe kya karna chahiye?")

    assert ctx.intent == Intent.DAILY_ACTION_PLAN.value
    assert len(ctx.recommendations) > 0
