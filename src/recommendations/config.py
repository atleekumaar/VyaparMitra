"""
Configuration loader and validator for VyaparMitra Phase 4 Recommendation Engine.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict
import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG: Dict[str, Any] = {
    "scoring": {
        "confidence_weights": {
            "prediction_confidence": 0.35,
            "evidence_strength": 0.25,
            "historical_consistency": 0.20,
            "data_quality": 0.20,
        },
        "impact_weights": {
            "revenue_opportunity": 0.30,
            "margin_opportunity": 0.25,
            "customer_value": 0.20,
            "urgency": 0.15,
            "scale": 0.10,
        },
    },
    "priority_thresholds": {
        "critical": 0.79,
        "high": 0.70,
        "medium": 0.55,
    },
    "inventory": {
        "service_level": 0.95,
        "z_score": 1.645,
        "lead_time_days": 3,
        "safety_stock_method": "stddev",
        "inventory_estimation_mode": True,
        "min_reorder_units": 5,
        "acceleration_threshold": 0.15,
    },
    "cross_sell": {
        "min_support": 0.005,
        "min_confidence": 0.08,
        "min_lift": 1.15,
        "max_rules_per_product": 3,
    },
    "customer": {
        "churn_high_risk": 0.60,
        "churn_medium_risk": 0.30,
        "high_value_spend_percentile": 75.0,
        "active_frequency_orders_per_month": 1.5,
    },
    "pricing": {
        "high_margin_threshold": 0.25,
        "low_margin_threshold": 0.15,
        "high_demand_percentile": 70.0,
        "low_demand_percentile": 30.0,
        "excessive_discount_rate": 0.15,
    },
    "conflict_resolution_order": [
        "DATA_QUALITY",
        "RISK",
        "MARGIN_PROTECTION",
        "REVENUE_GROWTH",
        "EXPERIMENTAL_ACTION",
    ],
}


def load_recommendation_config(config_path: str = "configs/recommendations.yaml") -> Dict[str, Any]:
    """Loads YAML recommendations config with resilient fallback paths."""
    candidates = [
        Path(config_path),
        Path("configs/recommendations.yaml"),
        Path("config/recommendations.yaml"),
    ]
    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}
                # Merge loaded with defaults for missing keys
                merged = {**DEFAULT_CONFIG, **cfg}
                return merged
            except Exception as e:
                logger.warning("Failed to parse config file %s: %s. Using default config.", p, e)

    return DEFAULT_CONFIG.copy()
