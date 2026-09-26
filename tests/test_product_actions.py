"""
Unit tests for Product Action and Sales Opportunity Engine.
Verifies classification of Star products, high-margin opportunities, and declining SKUs.
"""

import pandas as pd
from src.recommendations.products.product_actions import ProductActionEngine
from src.recommendations.schemas import RecommendationType


def test_star_product_triggers_focus():
    engine = ProductActionEngine()

    prods_df = pd.DataFrame([
        {"product_id": "P_STAR", "product_name": "Star SKU", "product_category": "Snacks", "product_revenue": 50000.0, "selling_price": 100.0, "unit_cost": 50.0},
        {"product_id": "P_MED", "product_name": "Med SKU", "product_category": "Snacks", "product_revenue": 10000.0, "selling_price": 100.0, "unit_cost": 40.0},
    ])
    demand_df = pd.DataFrame([
        {"product_id": "P_STAR", "predicted_units": 20.0},
        {"product_id": "P_MED", "predicted_units": 3.0},
    ])

    recs = engine.generate_recommendations(prods_df, demand_df)
    star_recs = [r for r in recs if r.entity_id == "P_STAR"]

    assert len(star_recs) == 1
    assert star_recs[0].type == RecommendationType.FOCUS
    assert "Star Product" in star_recs[0].title
