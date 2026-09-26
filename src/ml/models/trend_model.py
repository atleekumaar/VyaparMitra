"""
Short-term operational revenue trend forecasting model.
Classifies next 7-day revenue direction into INCREASING, STABLE, or DECREASING.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance

logger = logging.getLogger(__name__)

CLASS_LABEL_MAP = {
    0: "DECREASING",
    1: "STABLE",
    2: "INCREASING",
}


class BusinessTrendModel:
    """Multiclass gradient boosted classifier for business trend forecasting."""

    def __init__(
        self,
        random_seed: int = 42,
        horizon_days: int = 7,
        **kwargs: Any,
    ) -> None:
        self.random_seed = random_seed
        self.horizon_days = horizon_days
        self.model = HistGradientBoostingClassifier(
            max_iter=100,
            max_depth=5,
            min_samples_leaf=5,
            learning_rate=0.08,
            random_state=random_seed,
            **kwargs,
        )
        self.name = "HistGradientBoostingClassifier_Trend"
        self.feature_cols: List[str] = []

    def fit(self, X: pd.DataFrame, y: pd.Series) -> BusinessTrendModel:
        self.feature_cols = list(X.columns)
        self.model.fit(X, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X[self.feature_cols])

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(X[self.feature_cols])

    def get_feature_importance(self, X_val: pd.DataFrame, y_val: pd.Series) -> pd.DataFrame:
        perm = permutation_importance(
            self.model, X_val[self.feature_cols], y_val, n_repeats=5, random_state=self.random_seed
        )
        imp_df = pd.DataFrame({
            "feature": self.feature_cols,
            "importance": perm.importances_mean.round(4),
            "std": perm.importances_std.round(4),
        }).sort_values(by="importance", ascending=False).reset_index(drop=True)
        return imp_df

    def predict_current_trend(self, latest_features_df: pd.DataFrame) -> pd.DataFrame:
        """Predicts directional trend for the latest available date."""
        X = latest_features_df[self.feature_cols]
        preds = self.predict(X)
        probs = self.predict_proba(X)
        confidence = np.max(probs, axis=1).round(4)

        pred_labels = [CLASS_LABEL_MAP.get(int(p), "STABLE") for p in preds]

        out = pd.DataFrame({
            "prediction_date": latest_features_df["date"].values if "date" in latest_features_df else pd.Timestamp.now().strftime("%Y-%m-%d"),
            "horizon_days": self.horizon_days,
            "predicted_trend": pred_labels,
            "confidence": confidence,
            "model_name": self.name,
            "model_version": "v1.0",
        })
        return out
