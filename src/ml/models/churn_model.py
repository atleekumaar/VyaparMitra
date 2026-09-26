"""
Customer churn and inactivity risk classification model.
Predicts likelihood of customer lapsing within next 30 days and assigns risk bands.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance

logger = logging.getLogger(__name__)


class CustomerChurnModel:
    """Supervised classifier for customer inactivity / churn prediction."""

    def __init__(
        self,
        model_type: str = "hist_gb",
        random_seed: int = 42,
        low_threshold: float = 0.30,
        medium_threshold: float = 0.60,
        **kwargs: Any,
    ) -> None:
        self.model_type = model_type
        self.random_seed = random_seed
        self.low_threshold = low_threshold
        self.medium_threshold = medium_threshold
        self.feature_cols: List[str] = []

        if model_type == "logistic":
            self.model = Pipeline([
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=1000, random_state=random_seed, class_weight="balanced")),
            ])
            self.name = "LogisticRegression"
        elif model_type == "rf":
            self.model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=random_seed, class_weight="balanced")
            self.name = "RandomForestClassifier"
        else:
            self.model = HistGradientBoostingClassifier(
                max_iter=100,
                max_depth=5,
                min_samples_leaf=10,
                learning_rate=0.08,
                random_state=random_seed,
                class_weight="balanced",
                **kwargs,
            )
            self.name = "HistGradientBoostingClassifier"

    def fit(self, X: pd.DataFrame, y: pd.Series) -> CustomerChurnModel:
        self.feature_cols = list(X.columns)
        self.model.fit(X, y)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(X[self.feature_cols])

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X[self.feature_cols])

    def get_feature_importance(self, X_val: pd.DataFrame, y_val: pd.Series) -> pd.DataFrame:
        """Computes permutation feature importance."""
        perm = permutation_importance(
            self.model, X_val[self.feature_cols], y_val, n_repeats=5, random_state=self.random_seed
        )
        imp_df = pd.DataFrame({
            "feature": self.feature_cols,
            "importance": perm.importances_mean.round(4),
            "std": perm.importances_std.round(4),
        }).sort_values(by="importance", ascending=False).reset_index(drop=True)
        return imp_df

    def score_customers(self, snapshot_df: pd.DataFrame) -> pd.DataFrame:
        """Assigns risk probability and categorical risk band to each customer."""
        probs = self.predict_proba(snapshot_df[self.feature_cols])[:, 1]
        probs = np.round(probs, 4)

        def assign_risk_band(p: float) -> str:
            if p >= self.medium_threshold:
                return "high"
            elif p >= self.low_threshold:
                return "medium"
            else:
                return "low"

        scored = pd.DataFrame({
            "customer_id": snapshot_df["customer_id"].values,
            "snapshot_date": snapshot_df["snapshot_date"].values if "snapshot_date" in snapshot_df else "2026-07-15",
            "risk_probability": probs,
            "risk_band": [assign_risk_band(p) for p in probs],
            "model_name": self.name,
            "model_version": "v1.0",
        })
        return scored
