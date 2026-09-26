"""
Unit tests for Customer Retention and Engagement Engine.
Tests segmentation, retention vs personalization rules, and evidence attachments.
"""

import pandas as pd
from src.recommendations.customers.customer_actions import CustomerActionEngine
from src.recommendations.schemas import RecommendationType


def test_high_value_high_risk_triggers_retention():
    engine = CustomerActionEngine()

    risk_df = pd.DataFrame([
        {"customer_id": "C_VIP", "risk_probability": 0.85, "risk_band": "high"},
        {"customer_id": "C_LOW", "risk_probability": 0.20, "risk_band": "low"},
    ])
    cust_df = pd.DataFrame([
        {"customer_id": "C_VIP", "customer_name": "VIP User", "customer_total_spend": 25000.0, "customer_order_count": 8, "customer_average_order_value": 3125.0},
        {"customer_id": "C_LOW", "customer_name": "Low User", "customer_total_spend": 500.0, "customer_order_count": 1, "customer_average_order_value": 500.0},
    ])
    seg_df = pd.DataFrame([
        {"customer_id": "C_VIP", "customer_recency": 45.0},
        {"customer_id": "C_LOW", "customer_recency": 10.0},
    ])

    recs = engine.generate_recommendations(risk_df, cust_df, seg_df)

    vip_recs = [r for r in recs if r.entity_id == "C_VIP"]
    assert len(vip_recs) == 1
    assert vip_recs[0].type == RecommendationType.RETENTION
    assert vip_recs[0].priority >= 0.70
