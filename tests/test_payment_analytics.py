"""
Unit tests for Payment Analytics module.
"""

import pandas as pd
import pytest
from src.analytics.payment_analytics import PaymentAnalytics


@pytest.fixture
def sample_payment_data():
    tx = pd.DataFrame({
        "transaction_id": ["TX01", "TX02", "TX03", "TX04"],
        "merchant_id": ["M01"] * 4,
        "payment_method": ["UPI", "UPI", "CARD", "CASH"],
        "net_amount": [500.0, 700.0, 1000.0, 300.0],
    })
    return tx


def test_payment_summary_and_shares(sample_payment_data):
    engine = PaymentAnalytics(sample_payment_data)
    pay_df = engine.get_payment_summary()

    assert len(pay_df) == 3
    upi = pay_df.loc[pay_df["payment_method"] == "UPI"].iloc[0]
    assert upi["payment_method_orders"] == 2
    assert upi["payment_method_revenue"] == 1200.0
    assert upi["orders_share"] == 0.5  # 2 / 4
    assert upi["payment_method_aov"] == 600.0  # 1200 / 2
