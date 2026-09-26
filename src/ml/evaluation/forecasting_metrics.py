"""
Time-series forecasting evaluation metrics.
Implements MAE, RMSE, MAPE (zero-safe), sMAPE, and WAPE.
"""

from __future__ import annotations

from typing import Dict
import numpy as np


def compute_forecasting_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes standard regression & business forecasting metrics:
    - MAE: Mean Absolute Error
    - RMSE: Root Mean Squared Error
    - MAPE: Mean Absolute Percentage Error (safe against y=0)
    - sMAPE: Symmetric Mean Absolute Percentage Error
    - WAPE: Weighted Absolute Percentage Error (Sum(|y - y_hat|) / Sum(y))
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)

    if len(y_t) == 0:
        return {"mae": 0.0, "rmse": 0.0, "mape": 0.0, "smape": 0.0, "wape": 0.0}

    # MAE
    errors = np.abs(y_t - y_p)
    mae = float(np.mean(errors))

    # RMSE
    rmse = float(np.sqrt(np.mean((y_t - y_p) ** 2)))

    # WAPE = sum(|y - y_hat|) / sum(y)
    sum_actual = np.sum(np.abs(y_t))
    wape = float((np.sum(errors) / max(1e-9, sum_actual)) * 100.0)

    # sMAPE = (100 / n) * sum(2 * |y - y_hat| / (|y| + |y_hat|))
    denominator = (np.abs(y_t) + np.abs(y_p)) / 2.0
    # Avoid zero division when both true and pred are zero
    non_zero_mask = denominator > 1e-9
    if np.any(non_zero_mask):
        smape = float(np.mean(errors[non_zero_mask] / denominator[non_zero_mask]) * 100.0)
    else:
        smape = 0.0

    # Safe MAPE: only on elements where actual > 0
    positive_mask = np.abs(y_t) > 1e-9
    if np.any(positive_mask):
        mape = float(np.mean(errors[positive_mask] / np.abs(y_t[positive_mask])) * 100.0)
    else:
        mape = 0.0

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mape": round(mape, 2),
        "smape": round(smape, 2),
        "wape": round(wape, 2),
    }
