"""
Model architectures, benchmarks, and baseline implementations for Phase 3.
"""

from src.ml.models.baselines import (
    NaiveSalesBaseline,
    SeasonalNaiveSalesBaseline,
    MovingAverageSalesBaseline,
    RuleBasedChurnBaseline,
    MajorityTrendBaseline,
)
from src.ml.models.sales_forecaster import SalesForecaster
from src.ml.models.demand_forecaster import ProductDemandForecaster
from src.ml.models.churn_model import CustomerChurnModel
from src.ml.models.trend_model import BusinessTrendModel

__all__ = [
    "NaiveSalesBaseline",
    "SeasonalNaiveSalesBaseline",
    "MovingAverageSalesBaseline",
    "RuleBasedChurnBaseline",
    "MajorityTrendBaseline",
    "SalesForecaster",
    "ProductDemandForecaster",
    "CustomerChurnModel",
    "BusinessTrendModel",
]
