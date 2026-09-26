"""
Unit tests for deterministic conflict resolution.
Verifies precedence: DATA_QUALITY > RISK > MARGIN_PROTECTION > REVENUE_GROWTH > EXPERIMENTAL_ACTION.
"""

from src.recommendations.conflicts.resolver import ConflictResolver
from src.recommendations.schemas import (
    ConflictCategory,
    PriorityBand,
    Recommendation,
    RecommendationType,
)


def test_conflict_resolution_margin_over_growth():
    resolver = ConflictResolver()

    rec_promote = Recommendation(
        recommendation_id="REC_1",
        type=RecommendationType.PROMOTE,
        priority=0.75,
        priority_band=PriorityBand.HIGH,
        confidence=0.8,
        urgency=0.7,
        expected_impact=0.7,
        entity_type="product",
        entity_id="SKU_100",
        title="Promote",
        action="Promote",
        reason="Boost demand",
        conflict_category=ConflictCategory.REVENUE_GROWTH,
        created_at="now",
    )

    rec_margin = Recommendation(
        recommendation_id="REC_2",
        type=RecommendationType.REVIEW_MARGIN,
        priority=0.70,
        priority_band=PriorityBand.HIGH,
        confidence=0.8,
        urgency=0.7,
        expected_impact=0.7,
        entity_type="product",
        entity_id="SKU_100",
        title="Review Margin",
        action="Review Margin",
        reason="Margin is too slim",
        conflict_category=ConflictCategory.MARGIN_PROTECTION,
        created_at="now",
    )

    # In conflict, MARGIN_PROTECTION takes precedence over REVENUE_GROWTH
    resolved = resolver.resolve([rec_promote, rec_margin])
    assert len(resolved) == 1
    assert resolved[0].type == RecommendationType.REVIEW_MARGIN
