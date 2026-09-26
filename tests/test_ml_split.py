"""
Unit tests for chronological data splitting in Phase 3.
Ensures strict temporal ordering without row shuffling.
"""

import numpy as np
import pandas as pd
import pytest
from src.ml.data.split import chronological_split


def test_chronological_split_ordering():
    dates = pd.date_range("2026-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "date": dates,
        "revenue": np.random.uniform(100, 500, size=100),
    })

    train_df, val_df, test_df, info = chronological_split(
        df, date_col="date", train_ratio=0.70, val_ratio=0.15, test_ratio=0.15
    )

    assert len(train_df) == 70
    assert len(val_df) == 15
    assert len(test_df) == 15

    # Check temporal continuity
    assert pd.to_datetime(train_df["date"].max()) < pd.to_datetime(val_df["date"].min())
    assert pd.to_datetime(val_df["date"].max()) < pd.to_datetime(test_df["date"].min())

    # Metadata check
    assert info.train_count == 70
    assert info.validation_count == 15
    assert info.test_count == 15


def test_chronological_split_invalid_ratios():
    df = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=10), "val": range(10)})
    with pytest.raises(ValueError):
        chronological_split(df, train_ratio=0.8, val_ratio=0.2, test_ratio=0.2)
