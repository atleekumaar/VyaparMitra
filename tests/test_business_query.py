"""
Unit tests for VyaparMitra Phase 5 Business Query Engine.
Verifies controlled retrieval across Phases 1-4 Parquet data marts.
"""

import pytest
from src.copilot.retrieval.business_query import BusinessQueryEngine


@pytest.fixture
def query_engine():
    return BusinessQueryEngine()


def test_get_sales_summary(query_engine):
    res = query_engine.get_sales_summary()
    assert "metrics" in res
    assert res["metrics"]["total_revenue"] > 0
    assert res["metrics"]["total_orders"] > 0
    assert len(res["facts"]) >= 1
    assert len(res["sources"]) >= 1


def test_get_sales_forecast(query_engine):
    res = query_engine.get_sales_forecast()
    assert "metrics" in res
    assert res["metrics"]["forecast_total_revenue"] > 0
    assert len(res["sources"]) >= 1


def test_get_product_demand_forecast(query_engine):
    res = query_engine.get_product_demand_forecast(product_id="PRD_SNK_01")
    assert "metrics" in res
    assert "forecast_units" in res["metrics"]
    assert len(res["facts"]) >= 1


def test_get_customer_risk(query_engine):
    res = query_engine.get_customer_risk(customer_id="C03388")
    assert "metrics" in res
    assert res["metrics"]["total_customers_evaluated"] > 0


def test_get_inventory_recommendations(query_engine):
    res = query_engine.get_inventory_recommendations()
    assert "recommendations" in res
    assert len(res["recommendations"]) > 0
    assert "sku" in res["recommendations"][0]


def test_get_daily_action_plan(query_engine):
    res = query_engine.get_daily_action_plan(limit=3)
    assert "recommendations" in res
    assert len(res["recommendations"]) <= 3
