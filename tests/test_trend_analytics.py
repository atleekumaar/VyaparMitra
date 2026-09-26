"""
Unit tests for Trend & Anomaly Analytics module.
"""

import pandas as pd
import pytest
from src.analytics.trend_analytics import TrendAnalytics


@pytest.fixture
def sample_trend_data():
    dates = pd.date_range("2026-01-01", periods=15, freq="D").strftime("%Y-%m-%d")
    # Upward trend with one outlier on day 10
    values = [100.0 + (i * 20.0) for i in range(15)]
    values[9] = 1500.0  # Spike anomaly

    tx = pd.DataFrame({
        "transaction_id": [f"TX{i:02d}" for i in range(15)],
        "date": dates,
        "timestamp": [f"{d} 12:00:00" for d in dates],
        "net_amount": values,
    })
    return tx


def test_trend_classification_and_thresholds(sample_trend_data):
    cfg = {"analytics": {"trend": {"stable_threshold_percent": 5.0}}}
    engine = TrendAnalytics(sample_trend_data, config=cfg)
    trends = engine.get_trend_analysis(frequency="daily")

    assert not trends.empty
    assert "trend_classification" in trends.columns
    assert set(trends["trend_classification"]).issubset({"Increasing", "Decreasing", "Stable"})


def test_iqr_anomaly_detection(sample_trend_data):
    cfg = {"analytics": {"anomaly": {"method": "iqr", "iqr_multiplier": 1.5}}}
    engine = TrendAnalytics(sample_trend_data, config=cfg)
    anomalies_df, summary = engine.get_daily_anomalies()

    assert summary["total_anomalies"] >= 1
    assert summary["unusually_high_count"] >= 1
    assert "unusually_high" in anomalies_df["status"].values
    # Check outlier row has status unusually_high
    outlier_row = anomalies_df.iloc[9]
    assert outlier_row["status"] == "unusually_high"
