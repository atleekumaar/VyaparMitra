"""
Unit tests for Product Analytics module.
"""

import pandas as pd
import pytest
from src.analytics.product_analytics import ProductAnalytics


@pytest.fixture
def sample_product_data():
    prod_df = pd.DataFrame({
        "product_id": ["P1", "P2", "P3", "P4"],
        "product_name": ["Bread", "Milk", "Cake", "Butter"],
        "product_category": ["Bakery", "Dairy", "Bakery", "Dairy"],
        "product_sales": [10, 20, 5, 15],
        "product_revenue": [500.0, 1200.0, 1500.0, 900.0],
        "product_order_count": [8, 15, 5, 10],
        "unique_customers": [7, 12, 5, 9],
    })
    tx_df = pd.DataFrame()
    return prod_df, tx_df


def test_product_performance_matrix(sample_product_data):
    prod_df, tx_df = sample_product_data
    engine = ProductAnalytics(prod_df, tx_df)
    matrix = engine.get_performance_matrix()

    assert len(matrix) == 4
    total_rev = 500.0 + 1200.0 + 1500.0 + 900.0  # 4100.0
    cake_row = matrix.loc[matrix["product_id"] == "P3"].iloc[0]
    assert cake_row["revenue"] == 1500.0
    assert cake_row["revenue_share"] == round(1500.0 / total_rev, 4)
    assert cake_row["average_price"] == 300.0  # 1500 / 5


def test_product_rankings(sample_product_data):
    prod_df, tx_df = sample_product_data
    engine = ProductAnalytics(prod_df, tx_df)
    rankings = engine.get_product_rankings()

    # P3 has highest revenue (1500.0) -> rank 1 by revenue
    p3 = rankings.loc[rankings["product_id"] == "P3"].iloc[0]
    assert p3["rank_by_revenue"] == 1

    # P2 has highest units (20) -> rank 1 by units
    p2 = rankings.loc[rankings["product_id"] == "P2"].iloc[0]
    assert p2["rank_by_units"] == 1


def test_pareto_concentration_analysis(sample_product_data):
    prod_df, tx_df = sample_product_data
    engine = ProductAnalytics(prod_df, tx_df)
    pareto_df, summary = engine.get_pareto_concentration()

    assert summary["total_products"] == 4
    assert summary["total_catalog_revenue"] == 4100.0
    assert pareto_df.iloc[-1]["cumulative_revenue_pct"] == 100.0
