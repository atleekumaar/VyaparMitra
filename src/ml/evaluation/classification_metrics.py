"""
Classification evaluation metrics for customer churn and business trend prediction.
Calculates ROC-AUC, PR-AUC, Precision, Recall, F1, Balanced Accuracy, and Confusion Matrices.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    precision_recall_curve,
    recall_score,
    roc_auc_score,
    auc,
)


def compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
    is_multiclass: bool = False,
) -> Dict[str, Any]:
    """
    Computes comprehensive classification metrics.
    Robust to single-class samples and class imbalance.
    """
    y_t = np.asarray(y_true)
    y_p = np.asarray(y_pred)

    if len(y_t) == 0:
        return {}

    acc = float(accuracy_score(y_t, y_p))
    bal_acc = float(balanced_accuracy_score(y_t, y_p))
    cm = confusion_matrix(y_t, y_p).tolist()

    if is_multiclass:
        prec = float(precision_score(y_t, y_p, average="macro", zero_division=0))
        rec = float(recall_score(y_t, y_p, average="macro", zero_division=0))
        f1 = float(f1_score(y_t, y_p, average="macro", zero_division=0))
        roc_auc = None
        pr_auc = None

        if y_prob is not None and len(np.unique(y_t)) > 1:
            try:
                roc_auc = float(roc_auc_score(y_t, y_prob, multi_class="ovr", average="macro"))
            except Exception:
                roc_auc = None

        return {
            "accuracy": round(acc, 4),
            "balanced_accuracy": round(bal_acc, 4),
            "precision_macro": round(prec, 4),
            "recall_macro": round(rec, 4),
            "f1_macro": round(f1, 4),
            "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
            "confusion_matrix": cm,
        }

    else:
        # Binary classification (Churn)
        prec = float(precision_score(y_t, y_p, zero_division=0))
        rec = float(recall_score(y_t, y_p, zero_division=0))
        f1 = float(f1_score(y_t, y_p, zero_division=0))

        roc_auc = None
        pr_auc = None

        if y_prob is not None and len(np.unique(y_t)) > 1:
            try:
                roc_auc = float(roc_auc_score(y_t, y_prob))
                precision_curve, recall_curve, _ = precision_recall_curve(y_t, y_prob)
                pr_auc = float(auc(recall_curve, precision_curve))
            except Exception:
                roc_auc = None
                pr_auc = None

        return {
            "accuracy": round(acc, 4),
            "balanced_accuracy": round(bal_acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
            "pr_auc": round(pr_auc, 4) if pr_auc is not None else None,
            "confusion_matrix": cm,
        }
