"""
End-to-End Integration Tests for Phase 4 AI Recommendation & Decision Engine.
Verifies full pipeline execution, subsystem APIs, artifact generation, and data integrity.
"""

from pathlib import Path
import pandas as pd
import pytest
from src.recommendations.recommendation_engine import RecommendationEngine
from src.recommendations.schemas import Recommendation


@pytest.fixture(scope="module")
def rec_engine():
    engine = RecommendationEngine()
    engine.generate_all(export=True)
    return engine


def test_recommendation_subsystem_methods(rec_engine):
    inv_recs = rec_engine.inventory_recommendations()
    assert len(inv_recs) > 0
    assert all(isinstance(r, Recommendation) for r in inv_recs)

    sales_recs = rec_engine.sales_opportunities()
    assert len(sales_recs) > 0

    cust_recs = rec_engine.customer_recommendations()
    assert len(cust_recs) > 0

    cross_recs = rec_engine.cross_sell_recommendations()
    assert len(cross_recs) > 0

    price_recs = rec_engine.pricing_recommendations()
    assert len(price_recs) > 0

    action_plan = rec_engine.daily_action_plan(limit=10)
    assert len(action_plan) == 10
    # Ensure ranked by priority descending
    priorities = [r.priority for r in action_plan]
    assert priorities == sorted(priorities, reverse=True)


def test_product_specific_recommendations(rec_engine):
    prod_recs = rec_engine.product_recommendations(product_id="PRD_ACC_01")
    assert len(prod_recs) > 0
    for r in prod_recs:
        assert "PRD_ACC_01" in r.entity_id


def test_recommendation_artifacts_exist():
    out_dir = Path("data/recommendations")
    expected_parquets = [
        out_dir / "inventory_recommendations.parquet",
        out_dir / "sales_opportunities.parquet",
        out_dir / "customer_recommendations.parquet",
        out_dir / "cross_sell_recommendations.parquet",
        out_dir / "pricing_recommendations.parquet",
        out_dir / "all_recommendations.parquet",
        out_dir / "merchant_action_plan.parquet",
        out_dir / "recommendation_evidence.parquet",
    ]
    for p in expected_parquets:
        assert p.exists(), f"Missing parquet artifact: {p}"
        df = pd.read_parquet(p)
        assert not df.empty, f"Artifact is empty: {p}"

    expected_mds = [
        out_dir / "daily_action_plan.md",
        out_dir / "recommendation_summary.md",
    ]
    for m in expected_mds:
        assert m.exists(), f"Missing markdown artifact: {m}"
        assert len(m.read_text(encoding="utf-8")) > 100
