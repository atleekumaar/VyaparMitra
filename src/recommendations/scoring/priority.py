"""
Scoring and multi-criteria prioritization logic for recommendations.
Calculates normalized Confidence, Business Impact, Priority, and categorical PriorityBands.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import numpy as np
from src.recommendations.schemas import PriorityBand


def compute_confidence(
    prediction_confidence: float = 0.80,
    evidence_strength: float = 0.80,
    historical_consistency: float = 0.80,
    data_quality: float = 0.90,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Computes normalized confidence score in [0.0, 1.0].
    Formula:
        confidence = w_pred * pred_conf + w_evid * evid_str + w_hist * hist_cons + w_qual * data_qual
    """
    if weights is None:
        weights = {
            "prediction_confidence": 0.35,
            "evidence_strength": 0.25,
            "historical_consistency": 0.20,
            "data_quality": 0.20,
        }

    raw = (
        weights.get("prediction_confidence", 0.35) * float(prediction_confidence)
        + weights.get("evidence_strength", 0.25) * float(evidence_strength)
        + weights.get("historical_consistency", 0.20) * float(historical_consistency)
        + weights.get("data_quality", 0.20) * float(data_quality)
    )
    return round(float(np.clip(raw, 0.0, 1.0)), 4)


def compute_impact(
    revenue_opportunity: float = 0.50,
    margin_opportunity: float = 0.50,
    customer_value: float = 0.50,
    urgency: float = 0.50,
    scale: float = 0.50,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Computes normalized business impact score in [0.0, 1.0].
    Formula:
        impact = w_rev * rev_opp + w_margin * margin_opp + w_cust * cust_val + w_urg * urgency + w_scale * scale
    """
    if weights is None:
        weights = {
            "revenue_opportunity": 0.30,
            "margin_opportunity": 0.25,
            "customer_value": 0.20,
            "urgency": 0.15,
            "scale": 0.10,
        }

    raw = (
        weights.get("revenue_opportunity", 0.30) * float(revenue_opportunity)
        + weights.get("margin_opportunity", 0.25) * float(margin_opportunity)
        + weights.get("customer_value", 0.20) * float(customer_value)
        + weights.get("urgency", 0.15) * float(urgency)
        + weights.get("scale", 0.10) * float(scale)
    )
    return round(float(np.clip(raw, 0.0, 1.0)), 4)


def compute_priority(
    impact_score: float,
    confidence_score: float,
    urgency_score: float,
) -> float:
    """
    Calculates final composite priority score in [0.0, 1.0].
    Uses normalized geometric mean: Priority = (Impact * Confidence * Urgency)^(1/3)
    Ensures well-calibrated distribution across CRITICAL, HIGH, MEDIUM, and LOW bands.
    """
    imp = np.clip(float(impact_score), 0.0, 1.0)
    conf = np.clip(float(confidence_score), 0.0, 1.0)
    urg = np.clip(float(urgency_score), 0.0, 1.0)

    raw_priority = (imp * conf * urg) ** (1.0 / 3.0)
    return round(float(np.clip(raw_priority, 0.0, 1.0)), 4)



def assign_priority_band(
    priority_score: float,
    thresholds: Optional[Dict[str, float]] = None,
) -> PriorityBand:
    """
    Assigns categorical priority band based on configured thresholds.
    Default:
        [0.80, 1.00] -> CRITICAL
        [0.60, 0.79] -> HIGH
        [0.40, 0.59] -> MEDIUM
        [0.00, 0.39] -> LOW
    """
    if thresholds is None:
        thresholds = {
            "critical": 0.80,
            "high": 0.60,
            "medium": 0.40,
        }

    crit = thresholds.get("critical", 0.80)
    high = thresholds.get("high", 0.60)
    med = thresholds.get("medium", 0.40)

    p = float(priority_score)
    if p >= crit:
        return PriorityBand.CRITICAL
    elif p >= high:
        return PriorityBand.HIGH
    elif p >= med:
        return PriorityBand.MEDIUM
    else:
        return PriorityBand.LOW
