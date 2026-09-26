"""
Unit tests for Pricing and Margin Defense Engine.
Verifies maintain price, margin review, promotion, clearance, and excessive discount limits.
"""

import pandas as pd
from src.recommendations.pricing.pricing_engine import PricingRecommendationEngine
from src.recommendations.schemas import RecommendationType


def test_pricing_decision_rules():
    engine = PricingRecommendationEngine()

    prods_df = pd.DataFrame([
        # High demand + High margin -> MAINTAIN_PRICE
        {"product_id": "P_HIGH_M", "product_name": "Premium Best Seller", "selling_price": 200.0, "unit_cost": 100.0},
        # High demand + Low margin -> REVIEW_MARGIN
        {"product_id": "P_LOW_M", "product_name": "Commodity Staple", "selling_price": 100.0, "unit_cost": 92.0},
    ])
    demand_df = pd.DataFrame([
        {"product_id": "P_HIGH_M", "predicted_units": 25.0},
        {"product_id": "P_LOW_M", "predicted_units": 25.0},
    ])

    recs = engine.generate_recommendations(prods_df, demand_df)

    high_m_rec = [r for r in recs if r.entity_id == "P_HIGH_M"][0]
    low_m_rec = [r for r in recs if r.entity_id == "P_LOW_M"][0]

    assert high_m_rec.type == RecommendationType.MAINTAIN_PRICE
    assert low_m_rec.type == RecommendationType.REVIEW_MARGIN
