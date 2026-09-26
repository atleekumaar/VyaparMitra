"""
Chronological walk-forward backtesting for time-series forecasting models.
Simulates realistic out-of-sample forward deployment across multiple temporal folds.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Tuple
import numpy as np
import pandas as pd
from src.ml.evaluation.forecasting_metrics import compute_forecasting_metrics

logger = logging.getLogger(__name__)


def walk_forward_backtest(
    df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str,
    date_col: str,
    model_factory: Callable[[], Any],
    n_splits: int = 3,
    test_horizon: int = 14,
) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """
    Executes walk-forward rolling-origin evaluation on chronological series.
    Returns individual fold results and mean metrics across folds.
    """
    sorted_df = df.sort_values(by=date_col).reset_index(drop=True)
    n = len(sorted_df)

    if n < (test_horizon * (n_splits + 1)):
        # Series too short for requested splits, adapt
        n_splits = max(1, n // (test_horizon * 2))

    fold_metrics = []

    # Calculate origin dates for splits
    for fold in range(n_splits, 0, -1):
        cutoff_idx = n - (fold * test_horizon)
        if cutoff_idx <= test_horizon:
            continue

        train_fold = sorted_df.iloc[:cutoff_idx]
        val_fold = sorted_df.iloc[cutoff_idx:cutoff_idx + test_horizon]

        X_train, y_train = train_fold[feature_cols], train_fold[target_col]
        X_val, y_val = val_fold[feature_cols], val_fold[target_col]

        model = model_factory()
        model.fit(X_train, y_train)
        preds = model.predict(X_val)

        metrics = compute_forecasting_metrics(y_val.values, preds)
        metrics["fold"] = n_splits - fold + 1
        metrics["train_dates"] = f"{train_fold[date_col].min()} to {train_fold[date_col].max()}"
        metrics["val_dates"] = f"{val_fold[date_col].min()} to {val_fold[date_col].max()}"
        fold_metrics.append(metrics)

    if not fold_metrics:
        return [], {"mae": 0.0, "wape": 0.0, "rmse": 0.0}

    # Aggregate means
    avg_metrics = {
        "mae": round(float(np.mean([m["mae"] for m in fold_metrics])), 2),
        "rmse": round(float(np.mean([m["rmse"] for m in fold_metrics])), 2),
        "wape": round(float(np.mean([m["wape"] for m in fold_metrics])), 2),
        "smape": round(float(np.mean([m["smape"] for m in fold_metrics])), 2),
    }

    return fold_metrics, avg_metrics
