"""
Regression tests ensuring AI Copilot BusinessQueryEngine never leaks
shared static demo data (e.g., 15510039.34 revenue or PRD_ACC_01) to live tenants.
"""
from src.copilot.retrieval.business_query import BusinessQueryEngine


def test_empty_live_tenant_returns_zero_metrics_and_no_demo_leak():
    engine = BusinessQueryEngine()
    empty_biz = "BIZ_E5ECD03F_EMPTY_QA"

    sales = engine.get_sales_summary(merchant_id=empty_biz)
    assert sales["total_revenue"] == 0.0
    assert sales["total_orders"] == 0
    assert sales["total_revenue"] != 15510039.34

    prod = engine.get_product_performance(merchant_id=empty_biz)
    assert prod["product_revenue"] == 0.0
    assert prod["product_units_sold"] == 0
    assert prod["product_id"] != "PRD_ACC_01"

    inv = engine.get_inventory_recommendations(merchant_id=empty_biz)
    assert inv["recommendations"] == []

    cust = engine.get_customer_risk(merchant_id=empty_biz)
    assert cust["total_customers_evaluated"] == 0
    assert cust["high_risk_customers_count"] == 0


def test_demo_merchant_still_reads_phase_artifacts():
    engine = BusinessQueryEngine()
    demo_sales = engine.get_sales_summary(merchant_id="M001")
    assert "total_revenue" in demo_sales
