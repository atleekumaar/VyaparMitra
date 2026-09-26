"""
Unit tests for human-readable explanation generation.
Verifies WHAT, WHY, EVIDENCE, CONFIDENCE, URGENCY, EXPECTED IMPACT formatting.
"""

from src.recommendations.explanations.evidence import format_explanation
from src.recommendations.schemas import (
    Evidence,
    PriorityBand,
    Recommendation,
    RecommendationType,
)


def test_format_explanation_6_parts():
    rec = Recommendation(
        recommendation_id="REC_EXP_1",
        type=RecommendationType.RESTOCK,
        priority=0.86,
        priority_band=PriorityBand.CRITICAL,
        confidence=0.88,
        urgency=0.90,
        expected_impact=0.82,
        entity_type="product",
        entity_id="SKU_99",
        title="Restock Premium Coffee",
        action="Order 30 units immediately",
        reason="Demand spike expected from weekend forecast",
        evidence=[
            Evidence(metric="forecast_7d_units", value=42, source="Demand Model", description="7-day demand"),
            Evidence(metric="safety_stock", value=12, source="Statistical Formula"),
        ],
        created_at="now",
    )

    text = format_explanation(rec)

    assert "WHAT:" in text
    assert "WHY:" in text
    assert "EVIDENCE:" in text
    assert "CONFIDENCE:" in text
    assert "URGENCY:" in text
    assert "EXPECTED IMPACT:" in text
    assert "PRIORITY:" in text
    assert "forecast_7d_units = 42" in text
