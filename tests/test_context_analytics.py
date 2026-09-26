"""
Unit tests for Contextual Analytics module (Festivals & Weather).
"""

import pandas as pd
import pytest
from src.analytics.context_analytics import ContextAnalytics


@pytest.fixture
def sample_context_data():
    tx = pd.DataFrame({
        "transaction_id": ["TX01", "TX02", "TX03", "TX04"],
        "merchant_id": ["M01"] * 4,
        "date": ["2025-10-20", "2025-10-21", "2025-11-01", "2025-11-02"],
        "net_amount": [1000.0, 1500.0, 500.0, 600.0],
        "is_festival": [1, 1, 0, 0],
        "festival_name": ["Dhanteras", "Diwali", "None", "None"],
        "is_rainy": [0, 1, 0, 1],
        "weather_condition": ["Clear", "Rainy", "Clear", "Rainy"],
        "temperature": [28.0, 24.0, 22.0, 20.0],
        "rainfall": [0.0, 12.0, 0.0, 5.0],
        "humidity": [50.0, 85.0, 45.0, 80.0],
    })
    return tx


def test_festival_comparison_and_sample_sizes(sample_context_data):
    engine = ContextAnalytics(sample_context_data)
    per_fest, summary = engine.get_festival_analysis()

    assert summary["festival_days_count"] == 2
    assert summary["non_festival_days_count"] == 2
    assert summary["festival_day_avg_revenue"] == 1250.0  # (1000 + 1500) / 2
    assert summary["non_festival_day_avg_revenue"] == 550.0  # (500 + 600) / 2
    assert summary["festival_revenue_difference"] == 700.0
    assert len(per_fest) == 2


def test_weather_comparison_and_correlations(sample_context_data):
    engine = ContextAnalytics(sample_context_data)
    cond_df, summary = engine.get_weather_analysis()

    assert summary["rainy_days_count"] == 2
    assert summary["non_rainy_days_count"] == 2
    assert "rainfall_revenue_correlation" in summary
    assert not cond_df.empty
    assert "weather_condition" in cond_df.columns
