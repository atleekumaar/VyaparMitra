"""
Unit tests for Recommendation domain schemas.
Verifies field validation, score ranges [0.0, 1.0], enum integrity, and lifecycle states.
"""

import pytest
from pydantic import ValidationError
from src.recommendations.schemas import (
    ConflictCategory,
    Evidence,
    FeedbackRecord,
    LifecycleState,
    PriorityBand,
    Recommendation,
    RecommendationType,
)


def test_valid_recommendation_creation():
    rec = Recommendation(
        recommendation_id="REC_TEST_001",
        type=RecommendationType.RESTOCK,
        priority=0.85,
        priority_band=PriorityBand.CRITICAL,
        confidence=0.88,
        urgency=0.90,
        expected_impact=0.82,
        entity_type="product",
        entity_id="PRD_001",
        title="Restock Product 001",
        action="Order 20 units",
        reason="Demand is accelerating",
        evidence=[
            Evidence(metric="forecast_7d_units", value=45, source="Phase 3 ML")
        ],
        created_at="2026-09-25 12:00:00",
        status=LifecycleState.GENERATED,
    )
    assert rec.recommendation_id == "REC_TEST_001"
    assert rec.priority == 0.85
    assert rec.priority_band == PriorityBand.CRITICAL
    assert len(rec.evidence) == 1
    assert rec.evidence[0].metric == "forecast_7d_units"


def test_invalid_score_ranges_raise():
    with pytest.raises(ValidationError):
        Recommendation(
            recommendation_id="REC_BAD",
            type=RecommendationType.RESTOCK,
            priority=1.5,  # Exceeds 1.0
            priority_band=PriorityBand.CRITICAL,
            confidence=0.8,
            urgency=0.8,
            expected_impact=0.8,
            entity_type="product",
            entity_id="P1",
            title="Bad",
            action="Bad",
            reason="Bad",
            created_at="now",
        )


def test_feedback_record():
    fb = FeedbackRecord(
        recommendation_id="REC_001",
        action="RESTOCK",
        generated_at="2026-09-25",
        accepted=True,
        executed=True,
        actual_revenue_change=1500.0,
    )
    assert fb.accepted is True
    assert fb.actual_revenue_change == 1500.0
