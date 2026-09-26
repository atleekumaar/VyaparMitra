"""
Unit tests for multi-criteria priority scoring.
Verifies normalization, priority monotonicity, and priority band thresholds.
"""

from src.recommendations.scoring.priority import (
    assign_priority_band,
    compute_confidence,
    compute_impact,
    compute_priority,
)
from src.recommendations.schemas import PriorityBand


def test_priority_scores_and_bands():
    impact = compute_impact(revenue_opportunity=0.9, margin_opportunity=0.9, urgency=0.9)
    conf = compute_confidence(prediction_confidence=0.9, evidence_strength=0.9)
    urg = 0.9

    prio = compute_priority(impact, conf, urg)
    assert 0.0 <= prio <= 1.0

    band = assign_priority_band(prio)
    assert band == PriorityBand.CRITICAL

    # Low priority case
    prio_low = compute_priority(0.2, 0.4, 0.3)
    band_low = assign_priority_band(prio_low)
    assert band_low == PriorityBand.LOW
