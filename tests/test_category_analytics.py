"""
Unit tests for Category Analytics module.
"""

import pandas as pd
import pytest
from src.analytics.category_analytics import CategoryAnalytics


@pytest.fixture
def sample_category_data():
    tx = pd.DataFrame({
        "transaction_id": ["TX01", "TX02", "TX03", "TX04"],
        "merchant_id": ["M01", "M01", "M02", "M02"],
        "product_category": ["Bakery", "Bakery", "Electronics", "Electronics"],
        "quantity": [2, 1, 1, 2],
        "net_amount": [200.0, 100.0, 1500.0, 3000.0],
        "timestamp": ["2026-01-10 10:00:00", "2026-02-10 11:00:00", "2026-01-15 12:00:00", "2026-02-15 14:00:00"],
        "customer_id": ["C1", "C2", "C3", "C4"],
    })
    return tx


def test_category_summary_calculation(sample_category_data):
    engine = CategoryAnalytics(sample_category_data)
    cat_summary = engine.get_category_summary()

    assert len(cat_summary) == 2
    elec = cat_summary.loc[cat_summary["product_category"] == "Electronics"].iloc[0]
    assert elec["category_revenue"] == 4500.0
    assert elec["category_orders"] == 2
    assert elec["average_order_value"] == 2250.0
    assert round(elec["revenue_share"], 2) == round(4500.0 / 4800.0, 2)


def test_category_monthly_slice(sample_category_data):
    engine = CategoryAnalytics(sample_category_data)
    cat_monthly = engine.get_category_monthly()

    assert not cat_monthly.empty
    assert "month_key" in cat_monthly.columns
    assert "category_revenue" in cat_monthly.columns
