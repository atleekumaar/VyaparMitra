"""
Unit tests for Inventory Recommendation Engine and Reorder Logic.
Verifies safety stock calculation, reorder point, batch quantity, and estimation mode.
"""

import pandas as pd
import pytest
from src.recommendations.inventory.reorder_logic import (
    calculate_reorder_point,
    calculate_reorder_quantity,
    calculate_safety_stock,
)
from src.recommendations.inventory.inventory_engine import InventoryRecommendationEngine
from src.recommendations.schemas import RecommendationType


def test_safety_stock_calculation():
    # SS = Z * sigma * sqrt(L). Z=1.645, sigma=2.0, L=3 -> 1.645 * 2 * 1.732 = 5.70
    ss = calculate_safety_stock(demand_std=2.0, lead_time_days=3, z_score=1.645)
    assert ss == pytest.approx(5.70, rel=1e-2)


def test_reorder_point_calculation():
    # ROP = (velocity * L) + SS. vel=5.0, L=3, SS=6.0 -> 15.0 + 6.0 = 21.0
    rop = calculate_reorder_point(daily_velocity=5.0, lead_time_days=3, safety_stock=6.0)
    assert rop == 21.0


def test_reorder_quantity_calculation():
    # Q = max(min_units, forecast + SS). forecast=30, SS=10 -> 40
    qty = calculate_reorder_quantity(forecast_demand_7d=30.0, safety_stock=10.0, min_units=5)
    assert qty == 40


def test_inventory_engine_recommendations():
    engine = InventoryRecommendationEngine()

    demand_df = pd.DataFrame([
        {"product_id": "P1", "predicted_units": 10.0},
        {"product_id": "P1", "predicted_units": 15.0},
    ])
    prod_df = pd.DataFrame([
        {"product_id": "P1", "product_name": "Test SKU", "product_category": "Snacks", "unit_cost": 40.0, "selling_price": 80.0}
    ])
    tx_df = pd.DataFrame([
        {"product_id": "P1", "date": "2026-09-01", "quantity": 4},
        {"product_id": "P1", "date": "2026-09-02", "quantity": 6},
    ])

    recs = engine.generate_recommendations(demand_df, prod_df, tx_df)
    assert len(recs) == 1
    assert recs[0].type == RecommendationType.RESTOCK
    assert recs[0].entity_id == "P1"
    # Ensure inventory estimation mode is reported in evidence
    evidence_metrics = [e.metric for e in recs[0].evidence]
    assert "inventory_estimation_mode" in evidence_metrics
