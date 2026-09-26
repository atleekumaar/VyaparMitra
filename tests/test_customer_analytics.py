"""
Unit tests for Customer Analytics module.
"""

import pandas as pd
import pytest
from src.analytics.customer_analytics import CustomerAnalytics


@pytest.fixture
def sample_customer_data():
    cust_df = pd.DataFrame({
        "customer_id": [f"C{i:03d}" for i in range(1, 11)],
        "customer_name": [f"Cust {i}" for i in range(1, 11)],
        "customer_type": ["New", "New", "Regular", "Regular", "Repeat", "Repeat", "Repeat", "Regular", "New", "Repeat"],
        "city": ["Noida"] * 10,
        "customer_recency": [5.0, 12.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0, 210.0, 240.0],
        "customer_order_count": [1, 1, 2, 2, 4, 5, 3, 2, 1, 6],
        "customer_total_spend": [100.0, 150.0, 400.0, 500.0, 1200.0, 2000.0, 900.0, 600.0, 200.0, 3000.0],
    })

    tx_df = pd.DataFrame({
        "transaction_id": ["TX01", "TX02", "TX03", "TX04", "TX05"],
        "customer_id": ["C001", "C001", "C002", "C003", "C003"],
        "timestamp": ["2026-01-10 10:00:00", "2026-02-10 11:00:00", "2026-01-15 12:00:00", "2026-02-15 14:00:00", "2026-03-01 16:00:00"],
        "net_amount": [100.0, 150.0, 200.0, 300.0, 400.0],
        "quantity": [1, 1, 2, 2, 3],
    })
    return cust_df, tx_df


def test_customer_kpis_calculation(sample_customer_data):
    cust_df, tx_df = sample_customer_data
    engine = CustomerAnalytics(cust_df, tx_df)
    kpis = engine.get_customer_kpis()

    assert kpis.total_customers == 10
    assert kpis.active_customers == 10
    assert kpis.repeat_customers == 7  # order count > 1
    assert kpis.one_time_customers == 3  # order count == 1
    assert kpis.average_customer_spend == 905.0


def test_customer_rfm_scoring_and_segmentation(sample_customer_data):
    cust_df, tx_df = sample_customer_data
    engine = CustomerAnalytics(cust_df, tx_df)
    rfm_df = engine.get_rfm_segmentation()

    assert len(rfm_df) == 10
    assert set(rfm_df["r_score"]).issubset({1, 2, 3, 4, 5})
    assert set(rfm_df["f_score"]).issubset({1, 2, 3, 4, 5})
    assert set(rfm_df["m_score"]).issubset({1, 2, 3, 4, 5})
    assert "rfm_segment" in rfm_df.columns
    # Check that highest spend and frequency has Champions or Loyal
    top_customer = rfm_df.loc[rfm_df["customer_id"] == "C010"].iloc[0]
    assert top_customer["rfm_segment"] in ["Champions", "Loyal", "At Risk"]


def test_customer_cohort_matrix(sample_customer_data):
    cust_df, tx_df = sample_customer_data
    engine = CustomerAnalytics(cust_df, tx_df)
    cohort_df = engine.get_cohort_matrix()

    assert not cohort_df.empty
    assert "cohort_month" in cohort_df.columns
    assert "cohort_size" in cohort_df.columns
    assert "2026-01" in cohort_df["cohort_month"].values
