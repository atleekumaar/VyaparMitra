"""
Benchmark baseline models for Phase 3 ML tasks.
Serves as compulsory performance hurdles that candidate ML models must beat.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np
import pandas as pd


class NaiveSalesBaseline:
    """Baseline A: Predicts tomorrow's revenue equals yesterday's revenue (lag 1)."""

    def __init__(self, lag_1_col: str = "lag_1d_revenue") -> None:
        self.lag_1_col = lag_1_col
        self.name = "Naive (Lag 1)"

    def fit(self, X: pd.DataFrame, y: Any = None) -> NaiveSalesBaseline:
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.lag_1_col in X.columns:
            return np.maximum(0.0, X[self.lag_1_col].values.astype(float))
        return np.zeros(len(X), dtype=float)


class SeasonalNaiveSalesBaseline:
    """Baseline B: Predicts revenue equals the same weekday from previous week (lag 7)."""

    def __init__(self, lag_7_col: str = "lag_7d_revenue", fallback_col: str = "lag_1d_revenue") -> None:
        self.lag_7_col = lag_7_col
        self.fallback_col = fallback_col
        self.name = "Seasonal Naive (Lag 7)"

    def fit(self, X: pd.DataFrame, y: Any = None) -> SeasonalNaiveSalesBaseline:
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.lag_7_col in X.columns:
            val = X[self.lag_7_col].values.astype(float)
            # Fallback if zero or nan
            if self.fallback_col in X.columns:
                fallback = X[self.fallback_col].values.astype(float)
                val = np.where(val > 0, val, fallback)
            return np.maximum(0.0, val)
        return np.zeros(len(X), dtype=float)


class MovingAverageSalesBaseline:
    """Baseline C: 7-day trailing moving average."""

    def __init__(self, rolling_7_col: str = "rolling_7d_avg_revenue") -> None:
        self.rolling_7_col = rolling_7_col
        self.name = "7-Day Moving Average"

    def fit(self, X: pd.DataFrame, y: Any = None) -> MovingAverageSalesBaseline:
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.rolling_7_col in X.columns:
            return np.maximum(0.0, X[self.rolling_7_col].values.astype(float))
        return np.zeros(len(X), dtype=float)


class RuleBasedChurnBaseline:
    """Rule-based churn baseline: Predicts high probability if recency > threshold."""

    def __init__(self, recency_threshold: float = 60.0) -> None:
        self.recency_threshold = recency_threshold
        self.name = "Rule-Based Recency Baseline"

    def fit(self, X: pd.DataFrame, y: Any = None) -> RuleBasedChurnBaseline:
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        recency = X["recency"].values.astype(float) if "recency" in X.columns else np.zeros(len(X))
        # Simple heuristic probability
        prob_churn = np.clip(recency / (self.recency_threshold * 1.5), 0.05, 0.95)
        # Return 2D array [prob_active, prob_churn]
        return np.column_stack([1.0 - prob_churn, prob_churn])

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        prob = self.predict_proba(X)[:, 1]
        return (prob >= 0.50).astype(int)


class MajorityTrendBaseline:
    """Majority class baseline for trend prediction."""

    def __init__(self) -> None:
        self.name = "Majority Class Baseline"
        self.majority_class: int = 1  # default STABLE

    def fit(self, X: pd.DataFrame, y: pd.Series) -> MajorityTrendBaseline:
        if len(y) > 0:
            self.majority_class = int(y.mode()[0])
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return np.full(len(X), self.majority_class, dtype=int)


class ProductDemandBaseline:
    """Predicts next day product demand equals lag 7 units (or lag 1 fallback)."""

    def __init__(self, lag_col: str = "lag_7_units", fallback_col: str = "lag_1_units") -> None:
        self.lag_col = lag_col
        self.fallback_col = fallback_col
        self.name = "Seasonal Naive Demand (Lag 7)"

    def fit(self, X: pd.DataFrame, y: Any = None) -> ProductDemandBaseline:
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.lag_col in X.columns:
            val = X[self.lag_col].values.astype(float)
            if self.fallback_col in X.columns:
                fallback = X[self.fallback_col].values.astype(float)
                val = np.where(val > 0, val, fallback)
            return np.maximum(0.0, val)
        return np.zeros(len(X), dtype=float)

