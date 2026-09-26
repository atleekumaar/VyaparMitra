"""
Feature engineering pipelines for Phase 3 ML models.
Guarantees strict historical causality and target leakage prevention.
"""

from src.ml.features.sales_features import extract_sales_forecasting_features
from src.ml.features.demand_features import extract_demand_forecasting_features
from src.ml.features.churn_features import prepare_churn_feature_matrix
from src.ml.features.trend_features import extract_trend_forecasting_features

__all__ = [
    "extract_sales_forecasting_features",
    "extract_demand_forecasting_features",
    "prepare_churn_feature_matrix",
    "extract_trend_forecasting_features",
]
