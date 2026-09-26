"""
Unit tests for Sales Analytics module.
"""

import pandas as pd
import pytest
from src.analytics.sales_analytics import SalesAnalytics


@pytest.fixture
def sample_sales_data():
    tx = pd.DataFrame({
        "transaction_id": ["TX01", "TX02", "TX03", "TX04"],
        "merchant_id": ["M1", "M1", "M2", "M1"],
        "timestamp": ["2026-01-01 10:00:00", "2026-01-02 12:00:00", "2026-02-01 14:00:00", "2026-02-02 16:00:00"],
        "date": ["2026-01-01", "2026-01-02", "2026-02-01", "2026-02-02"],
        "quantity": [2, 1, 3, 2],
        "total_amount": [200.0, 100.0, 300.0, 200.0],
        "discount_amount": [20.0, 0.0, 30.0, 0.0],
        "net_amount": [180.0, 100.0, 270.0, 200.0],
    })
    return tx


def test_core_kpis_calculation(sample_sales_data):
    engine = SalesAnalytics(sample_sales_data)
    kpis = engine.get_core_kpis()

    assert kpis.total_orders == 4
    assert kpis.total_units == 8
    assert kpis.total_revenue == 750.0  # 180 + 100 + 270 + 200
    assert kpis.average_order_value == 187.5  # 750 / 4
    assert kpis.average_units_per_order == 2.0  # 8 / 4
    assert kpis.discount_total == 50.0
    assert kpis.discount_rate == 0.0625  # 50 / 800


def test_period_comparison_growth(sample_sales_data):
    engine = SalesAnalytics(sample_sales_data)
    monthly = engine.get_period_comparison(frequency="monthly")

    assert len(monthly) == 2
    # Jan 2026: 280, Feb 2026: 470
    jan_row = monthly.iloc[0]
    feb_row = monthly.iloc[1]

    assert jan_row["revenue"] == 280.0
    assert feb_row["revenue"] == 470.0
    assert feb_row["revenue_change"] == 190.0
    assert feb_row["revenue_growth_pct"] == round((190.0 / 280.0) * 100.0, 2)


def test_zero_division_guard():
    empty_df = pd.DataFrame(columns=["transaction_id", "merchant_id", "timestamp", "date", "quantity", "net_amount", "discount_amount", "total_amount"])
    engine = SalesAnalytics(empty_df)
    kpis = engine.get_core_kpis()

    assert kpis.total_orders == 0
    assert kpis.total_revenue == 0.0
    assert kpis.average_order_value == 0.0


def test_daily_sales_analytics(sample_sales_data):
    engine = SalesAnalytics(sample_sales_data)
    daily_df, stats = engine.get_daily_sales_analytics()

    assert len(daily_df) == 4
    assert stats["highest_revenue_day"]["date"] == "2026-02-01"
    assert stats["highest_revenue_day"]["revenue"] == 270.0
    assert stats["lowest_revenue_day"]["date"] == "2026-01-02"
    assert stats["lowest_revenue_day"]["revenue"] == 100.0
