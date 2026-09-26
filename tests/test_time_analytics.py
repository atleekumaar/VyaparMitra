"""
Unit tests for Time Analytics module.
"""

import pandas as pd
import pytest
from src.analytics.time_analytics import TimeAnalytics


@pytest.fixture
def sample_time_data():
    tx = pd.DataFrame({
        "transaction_id": ["TX01", "TX02", "TX03", "TX04"],
        "merchant_id": ["M01"] * 4,
        "timestamp": [
            "2026-01-10 10:15:00",  # Saturday, hour 10
            "2026-01-10 18:30:00",  # Saturday, hour 18
            "2026-01-11 18:45:00",  # Sunday, hour 18
            "2026-02-15 12:00:00",  # Sunday, hour 12
        ],
        "year": [2026, 2026, 2026, 2026],
        "quarter": [1, 1, 1, 1],
        "month": [1, 1, 1, 2],
        "quantity": [1, 2, 3, 1],
        "net_amount": [100.0, 500.0, 600.0, 200.0],
    })
    return tx


def test_hourly_analytics(sample_time_data):
    engine = TimeAnalytics(sample_time_data)
    hourly = engine.get_hourly_analytics()

    h18 = hourly.loc[hourly["hour"] == 18].iloc[0]
    assert h18["orders"] == 2
    assert h18["revenue"] == 1100.0


def test_weekday_analytics(sample_time_data):
    engine = TimeAnalytics(sample_time_data)
    weekday = engine.get_weekday_analytics()

    assert not weekday.empty
    assert "day_name" in weekday.columns
    assert "Saturday" in weekday["day_name"].values
    assert "Sunday" in weekday["day_name"].values


def test_peak_period_detection(sample_time_data):
    engine = TimeAnalytics(sample_time_data)
    peaks = engine.get_peak_periods()

    assert peaks["highest_revenue_hour"]["hour"] == 18
    assert peaks["highest_revenue_hour"]["revenue"] == 1100.0
    assert peaks["highest_revenue_weekday"]["day_name"] in ["Saturday", "Sunday"]
