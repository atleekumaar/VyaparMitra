"""
Unit tests for Market Basket and Cross-Sell Association Engine.
Verifies Support, Confidence, Lift, and rule filtering.
"""

import pandas as pd
from src.recommendations.cross_sell.association_engine import CrossSellAssociationEngine
from src.recommendations.schemas import RecommendationType


def test_cross_sell_rule_mining():
    engine = CrossSellAssociationEngine()

    # Create synthetic co-purchase data: 10 customers all buy P1 and P2
    rows = []
    for i in range(10):
        cid = f"C_{i}"
        rows.append({"customer_id": cid, "product_id": "P1"})
        rows.append({"customer_id": cid, "product_id": "P2"})
    # 5 other customers only buy P3
    for i in range(10, 15):
        cid = f"C_{i}"
        rows.append({"customer_id": cid, "product_id": "P3"})

    tx_df = pd.DataFrame(rows)
    prod_df = pd.DataFrame([
        {"product_id": "P1", "product_name": "Product 1", "selling_price": 100.0},
        {"product_id": "P2", "product_name": "Product 2", "selling_price": 50.0},
        {"product_id": "P3", "product_name": "Product 3", "selling_price": 20.0},
    ])

    rules_df = engine.extract_association_rules(tx_df)
    assert not rules_df.empty

    # Check pair P1 -> P2
    p1_p2 = rules_df[(rules_df["antecedent_product"] == "P1") & (rules_df["consequent_product"] == "P2")].iloc[0]
    # Support = 10 / 15 = 0.6667
    assert p1_p2["support"] > 0.60
    # Confidence = 10 / 10 = 1.0
    assert p1_p2["confidence"] == 1.0
    # Lift = 1.0 / (10/15) = 1.5
    assert p1_p2["lift"] == 1.5

    recs = engine.generate_recommendations(tx_df, prod_df)
    assert len(recs) >= 1
    assert recs[0].type == RecommendationType.CROSS_SELL
