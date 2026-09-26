"""
Unit tests for Recommendation Deduplication.
Verifies collapsing identical entity & action recommendations while preserving unique evidence.
"""

from src.recommendations.deduplication.deduplicator import RecommendationDeduplicator
from src.recommendations.schemas import (
    Evidence,
    PriorityBand,
    Recommendation,
    RecommendationType,
)


def test_deduplication_merges_evidence():
    dedup = RecommendationDeduplicator()

    r1 = Recommendation(
        recommendation_id="REC_A",
        type=RecommendationType.RESTOCK,
        priority=0.85,
        priority_band=PriorityBand.CRITICAL,
        confidence=0.85,
        urgency=0.90,
        expected_impact=0.80,
        entity_type="product",
        entity_id="SKU_55",
        title="Restock SKU 55",
        action="Order 25 units",
        reason="Rule 1 triggered",
        evidence=[Evidence(metric="forecast_7d_units", value=30, source="ML")],
        created_at="now",
    )

    r2 = Recommendation(
        recommendation_id="REC_B",
        type=RecommendationType.RESTOCK,
        priority=0.82,
        priority_band=PriorityBand.HIGH,
        confidence=0.80,
        urgency=0.85,
        expected_impact=0.78,
        entity_type="product",
        entity_id="SKU_55",
        title="Restock SKU 55",
        action="Order 25 units",
        reason="Rule 2 triggered",
        evidence=[Evidence(metric="daily_velocity", value=4.5, source="Sales Analytics")],
        created_at="now",
    )

    res = dedup.deduplicate([r1, r2])
    assert len(res) == 1
    assert res[0].recommendation_id == "REC_A"
    assert res[0].priority == 0.85

    metrics = [e.metric for e in res[0].evidence]
    assert "forecast_7d_units" in metrics
    assert "daily_velocity" in metrics
