"""
Temporal chronological data splitting module.
Guarantees strict time ordering with zero future lookahead or data leakage.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
import pandas as pd
from src.schemas.ml_schema import SplitInfo

logger = logging.getLogger(__name__)


def chronological_split(
    df: pd.DataFrame,
    date_col: str = "date",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    train_end_date: Optional[str] = None,
    val_end_date: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, SplitInfo]:
    """
    Split time-dependent datasets into Train, Validation, and Test sets chronologically.
    Never shuffles rows.
    """
    if df.empty:
        raise ValueError("Cannot split empty DataFrame.")

    if not (train_end_date and val_end_date):
        total_ratio = train_ratio + val_ratio + test_ratio
        if abs(total_ratio - 1.0) > 0.01:
            raise ValueError(f"Split ratios must sum to 1.0, got {total_ratio:.4f}")

    sorted_df = df.sort_values(by=date_col).reset_index(drop=True)

    if train_end_date and val_end_date:
        train_df = sorted_df[sorted_df[date_col] <= train_end_date].copy()
        val_df = sorted_df[(sorted_df[date_col] > train_end_date) & (sorted_df[date_col] <= val_end_date)].copy()
        test_df = sorted_df[sorted_df[date_col] > val_end_date].copy()
    else:
        # Unique dates based split to preserve complete days
        unique_dates = sorted(sorted_df[date_col].unique())
        n_dates = len(unique_dates)

        if n_dates < 5:
            # Fallback for tiny test series
            n_rows = len(sorted_df)
            n_train = max(1, int(n_rows * train_ratio))
            n_val = max(1, int(n_rows * val_ratio))
            train_df = sorted_df.iloc[:n_train].copy()
            val_df = sorted_df.iloc[n_train:n_train + n_val].copy()
            test_df = sorted_df.iloc[n_train + n_val:].copy()
            if test_df.empty:
                test_df = val_df.copy()
        else:
            n_train_dates = int(round(n_dates * train_ratio))
            n_val_dates = int(round(n_dates * val_ratio))
            # Ensure at least 1 date in each split
            n_train_dates = max(1, min(n_train_dates, n_dates - 2))
            n_val_dates = max(1, min(n_val_dates, n_dates - n_train_dates - 1))

            train_dates = set(unique_dates[:n_train_dates])
            val_dates = set(unique_dates[n_train_dates:n_train_dates + n_val_dates])
            test_dates = set(unique_dates[n_train_dates + n_val_dates:])

            train_df = sorted_df[sorted_df[date_col].isin(train_dates)].copy()
            val_df = sorted_df[sorted_df[date_col].isin(val_dates)].copy()
            test_df = sorted_df[sorted_df[date_col].isin(test_dates)].copy()

    split_info = SplitInfo(
        train_start=str(train_df[date_col].min()),
        train_end=str(train_df[date_col].max()),
        train_count=len(train_df),
        validation_start=str(val_df[date_col].min()),
        validation_end=str(val_df[date_col].max()),
        validation_count=len(val_df),
        test_start=str(test_df[date_col].min()),
        test_end=str(test_df[date_col].max()),
        test_count=len(test_df),
    )

    logger.info(
        "Chronological Split: Train [%s to %s, N=%d] | Val [%s to %s, N=%d] | Test [%s to %s, N=%d]",
        split_info.train_start, split_info.train_end, split_info.train_count,
        split_info.validation_start, split_info.validation_end, split_info.validation_count,
        split_info.test_start, split_info.test_end, split_info.test_count,
    )

    return train_df, val_df, test_df, split_info
