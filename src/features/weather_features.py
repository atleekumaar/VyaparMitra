"""
Weather feature engineering.
Merges meteorological observations on (date, city), derives is_rainy flag,
and gracefully imputes any missing weather data.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


def merge_weather_features(
    transactions_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    merchants_df: Optional[pd.DataFrame] = None,
    defaults: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Merge weather data onto transactions by (date, city).
    Derives:
    - temperature
    - humidity
    - rainfall
    - weather_condition
    - is_rainy (1 if rainfall > 0 or condition contains 'rain')
    Gracefully handles missing weather records through city-level and global imputation.
    """
    logger.info("Merging weather features for %d transaction rows...", len(transactions_df))
    out = transactions_df.copy()

    default_temp = 27.0
    default_humidity = 55.0
    default_rainfall = 0.0
    default_condition = "Clear"

    if defaults:
        default_temp = defaults.get("default_temp", default_temp)
        default_humidity = defaults.get("default_humidity", default_humidity)
        default_rainfall = defaults.get("default_rainfall", default_rainfall)
        default_condition = defaults.get("default_condition", default_condition)

    # Ensure transaction has city. If not, merge from merchants
    if "city" not in out.columns and merchants_df is not None and "merchant_id" in out.columns:
        merchant_cities = merchants_df[["merchant_id", "city"]].drop_duplicates()
        out = pd.merge(out, merchant_cities, on="merchant_id", how="left")

    if weather_df is None or weather_df.empty:
        logger.warning("Weather dataset empty or missing; applying default weather attributes.")
        out["temperature"] = default_temp
        out["humidity"] = default_humidity
        out["rainfall"] = default_rainfall
        out["weather_condition"] = default_condition
        out["is_rainy"] = 0
        return out

    # Ensure date is string YYYY-MM-DD
    weather_clean = weather_df.copy()
    weather_clean["date"] = pd.to_datetime(weather_clean["date"]).dt.strftime("%Y-%m-%d")
    weather_clean["city"] = weather_clean["city"].astype(str).str.strip()

    # Deduplicate weather per (date, city)
    weather_dedup = weather_clean.drop_duplicates(subset=["date", "city"]).copy()

    # Merge
    out = pd.merge(out, weather_dedup, on=["date", "city"], how="left")

    # City-level imputation for any missing dates
    city_means = (
        weather_clean.groupby("city")[["temperature", "humidity", "rainfall"]]
        .mean()
        .to_dict()
    )

    for city in out["city"].unique():
        city_mask = out["city"] == city
        t_val = city_means["temperature"].get(city, default_temp)
        h_val = city_means["humidity"].get(city, default_humidity)
        r_val = city_means["rainfall"].get(city, default_rainfall)

        out.loc[city_mask & out["temperature"].isna(), "temperature"] = t_val
        out.loc[city_mask & out["humidity"].isna(), "humidity"] = h_val
        out.loc[city_mask & out["rainfall"].isna(), "rainfall"] = r_val

    # Global fallback for any remaining NaNs
    out["temperature"] = out["temperature"].fillna(default_temp).astype(float).round(1)
    out["humidity"] = out["humidity"].fillna(default_humidity).astype(float).round(1)
    out["rainfall"] = out["rainfall"].fillna(default_rainfall).astype(float).round(1)
    out["weather_condition"] = out["weather_condition"].fillna(default_condition).astype(str).str.strip()

    # Derive is_rainy binary flag
    is_rainy_condition = out["weather_condition"].str.lower().str.contains("rain")
    has_rainfall = out["rainfall"] > 0.0
    out["is_rainy"] = (is_rainy_condition | has_rainfall).astype(int)

    return out
