"""
Unit tests for forecasting and classification evaluation metrics in Phase 3.
Verifies MAE, RMSE, WAPE, sMAPE, zero-safe MAPE, ROC-AUC, PR-AUC, and F1 calculations.
"""

import numpy as np
import pytest
from src.ml.evaluation.forecasting_metrics import compute_forecasting_metrics
from src.ml.evaluation.classification_metrics import compute_classification_metrics


def test_forecasting_metrics_exact_match():
    y_true = np.array([100.0, 200.0, 300.0])
    y_pred = np.array([100.0, 200.0, 300.0])

    metrics = compute_forecasting_metrics(y_true, y_pred)
    assert metrics["mae"] == 0.0
    assert metrics["rmse"] == 0.0
    assert metrics["wape"] == 0.0
    assert metrics["smape"] == 0.0
    assert metrics["mape"] == 0.0


def test_forecasting_metrics_with_zeros():
    y_true = np.array([0.0, 10.0, 20.0])
    y_pred = np.array([5.0, 15.0, 25.0])

    # Should not raise ZeroDivisionError
    metrics = compute_forecasting_metrics(y_true, y_pred)
    assert metrics["mae"] == 5.0
    assert metrics["rmse"] == 5.0
    assert metrics["wape"] == pytest.approx(50.0, rel=1e-2)


def test_classification_metrics_binary():
    y_true = np.array([1, 0, 1, 1, 0, 0])
    y_pred = np.array([1, 0, 1, 0, 0, 1])
    y_prob = np.array([0.9, 0.1, 0.8, 0.4, 0.2, 0.7])

    metrics = compute_classification_metrics(y_true, y_pred, y_prob)
    assert "roc_auc" in metrics
    assert "pr_auc" in metrics
    assert "f1" in metrics
    assert "confusion_matrix" in metrics
    assert metrics["accuracy"] == pytest.approx(4 / 6, rel=1e-2)


def test_classification_metrics_multiclass():
    y_true = np.array([0, 1, 2, 1, 0, 2])
    y_pred = np.array([0, 1, 2, 1, 0, 2])

    metrics = compute_classification_metrics(y_true, y_pred, is_multiclass=True)
    assert metrics["accuracy"] == 1.0
    assert metrics["f1_macro"] == 1.0
