"""
Unit tests for feature engineering modules:
- Transaction features & revenue math
- Merchant aggregations
- Customer metrics (RFM)
- Product sales & pricing
- Festival merging & temporal distances
- Weather merging & imputation
- Time windows & anti-leakage lags
"""

import pandas as pd
import numpy as np
import pytest

from src.features.transaction_features import extract_transaction_features
from src.features.merchant_features import extract_merchant_features
from src.features.customer_features import extract_customer_features
from src.features.product_features import extract_product_features
from src.features.festival_features import merge_festival_features
from src.features.weather_features import merge_weather_features
from src.features.time_features import extract_daily_features, extract_time_features


def test_transaction_feature_calculations():
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002"],
        "merchant_id": ["M001", "M001"],
        "customer_id": ["C001", "C002"],
        "timestamp": ["2026-01-01 14:30:00", "2026-01-31 20:45:00"],
        "product_id": ["P001", "P002"],
        "product_category": ["Bread", "Dairy"],
        "quantity": [3, 2],
        "unit_price": [50.0, 75.0],
        "discount": [15.0, 0.0],
        "payment_method": ["UPI", "CARD"],
    })

    feats = extract_transaction_features(tx)

    # Math validations
    assert feats.iloc[0]["total_amount"] == 150.0
    assert feats.iloc[0]["discount_amount"] == 15.0
    assert feats.iloc[0]["net_amount"] == 135.0

    assert feats.iloc[1]["total_amount"] == 150.0
    assert feats.iloc[1]["discount_amount"] == 0.0
    assert feats.iloc[1]["net_amount"] == 150.0

    # Calendar validations
    assert feats.iloc[0]["hour"] == 14
    assert feats.iloc[0]["is_month_start"] == 1
    assert feats.iloc[0]["is_month_end"] == 0

    assert feats.iloc[1]["hour"] == 20
    assert feats.iloc[1]["is_month_start"] == 0
    assert feats.iloc[1]["is_month_end"] == 1


def test_merchant_feature_aggregations():
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002", "TX003"],
        "merchant_id": ["M001", "M001", "M002"],
        "customer_id": ["C001", "C002", "C001"],
        "product_id": ["P001", "P002", "P001"],
        "net_amount": [100.0, 200.0, 300.0],
        "date": ["2026-01-10", "2026-01-11", "2026-01-10"],
    })
    merchants = pd.DataFrame({
        "merchant_id": ["M001", "M002"],
        "merchant_name": ["Store 1", "Store 2"],
        "business_type": ["Bakery", "Grocery"],
    })

    m_feats = extract_merchant_features(tx, merchants)
    m1 = m_feats[m_feats["merchant_id"] == "M001"].iloc[0]

    assert m1["merchant_total_revenue"] == 300.0
    assert m1["merchant_total_orders"] == 2
    assert m1["average_order_value"] == 150.0
    assert m1["unique_customers"] == 2
    assert m1["unique_products"] == 2
    assert m1["active_days"] == 2
    assert m1["revenue_per_day"] == 150.0
    assert m1["orders_per_day"] == 1.0


def test_customer_feature_aggregations():
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002"],
        "customer_id": ["C001", "C001"],
        "net_amount": [150.0, 250.0],
        "timestamp": ["2026-01-01 10:00:00", "2026-01-11 10:00:00"],
    })
    customers = pd.DataFrame({
        "customer_id": ["C001"],
        "customer_name": ["Alice"],
        "customer_type": ["Regular"],
    })

    c_feats = extract_customer_features(tx, customers, reference_date="2026-01-15 10:00:00")
    c1 = c_feats.iloc[0]

    assert c1["customer_total_spend"] == 400.0
    assert c1["customer_order_count"] == 2
    assert c1["customer_average_order_value"] == 200.0
    assert c1["customer_recency"] == 4.0  # 15th minus 11th = 4 days
    assert c1["customer_first_purchase"] == "2026-01-01 10:00:00"
    assert c1["customer_last_purchase"] == "2026-01-11 10:00:00"


def test_product_feature_aggregations():
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002", "TX003"],
        "product_id": ["P001", "P001", "P002"],
        "customer_id": ["C001", "C002", "C001"],
        "quantity": [2, 3, 1],
        "net_amount": [100.0, 150.0, 60.0],
    })
    products = pd.DataFrame({
        "product_id": ["P001", "P002"],
        "product_name": ["Bread", "Milk"],
        "product_category": ["Bakery", "Dairy"],
        "unit_cost": [30.0, 40.0],
        "selling_price": [50.0, 60.0],
    })

    p_feats = extract_product_features(tx, products)
    p1 = p_feats[p_feats["product_id"] == "P001"].iloc[0]

    assert p1["product_sales"] == 5
    assert p1["product_revenue"] == 250.0
    assert p1["product_order_count"] == 2
    assert p1["unique_customers"] == 2
    assert p1["average_quantity"] == 2.5
    assert p1["average_selling_price"] == 50.0


def test_festival_merge_and_distances():
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002", "TX003"],
        "date": ["2026-04-10", "2026-04-14", "2026-04-18"],
    })
    # Multi-festival support: Two festivals on the same date (2026-04-14)
    festivals = pd.DataFrame([
        {"date": "2026-04-14", "festival_name": "Ambedkar Jayanti", "festival_type": "National", "is_festival": 1, "festival_intensity": 0.8},
        {"date": "2026-04-14", "festival_name": "Baisakhi", "festival_type": "Regional", "is_festival": 1, "festival_intensity": 0.9},
    ])

    f_merged = merge_festival_features(tx, festivals, date_col="date")

    # April 10: 4 days before April 14
    row1 = f_merged.iloc[0]
    assert row1["is_festival"] == 0
    assert row1["days_to_festival"] == 4

    # April 14: Festival day itself (merged name and maximum intensity 0.9)
    row2 = f_merged.iloc[1]
    assert row2["is_festival"] == 1
    assert "Ambedkar Jayanti" in row2["festival_name"]
    assert "Baisakhi" in row2["festival_name"]
    assert row2["festival_intensity"] == 0.9
    assert row2["days_to_festival"] == 0
    assert row2["days_after_festival"] == 0

    # April 18: 4 days after April 14
    row3 = f_merged.iloc[2]
    assert row3["is_festival"] == 0
    assert row3["days_after_festival"] == 4


def test_weather_merge_and_graceful_imputation():
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002"],
        "merchant_id": ["M001", "M002"],
        "date": ["2026-01-10", "2026-01-10"],
        "city": ["Noida", "UnknownCity"],
    })
    weather = pd.DataFrame([
        {"date": "2026-01-10", "city": "Noida", "temperature": 22.5, "humidity": 60.0, "rainfall": 5.0, "weather_condition": "Rainy"},
    ])

    w_merged = merge_weather_features(tx, weather)

    # Noida record
    noida_row = w_merged.iloc[0]
    assert noida_row["temperature"] == 22.5
    assert noida_row["rainfall"] == 5.0
    assert noida_row["is_rainy"] == 1

    # Unknown city (missing in weather dataset) -> gracefully imputed without failure
    unknown_row = w_merged.iloc[1]
    assert not pd.isna(unknown_row["temperature"])
    assert unknown_row["rainfall"] == 0.0
    assert unknown_row["is_rainy"] == 0


def test_daily_time_window_features_no_future_leakage():
    tx = pd.DataFrame({
        "transaction_id": [f"TX{i:03d}" for i in range(1, 11)],
        "merchant_id": ["M001"] * 10,
        "customer_id": [f"C{i:03d}" for i in range(1, 11)],
        "net_amount": [100.0 * i for i in range(1, 11)],  # 100, 200, 300, ...
        "quantity": [1] * 10,
        "date": [f"2026-01-{i:02d}" for i in range(1, 11)],
    })

    daily = extract_daily_features(tx, date_col="date")

    # Day 1: lag_1d_revenue should be initialized without future data
    assert daily.iloc[0]["daily_total_revenue"] == 100.0
    # Day 2: lag_1d_revenue must equal Day 1 revenue (100.0)
    assert daily.iloc[1]["daily_total_revenue"] == 200.0
    assert daily.iloc[1]["lag_1d_revenue"] == 100.0
    # Day 3: lag_1d_revenue must equal Day 2 revenue (200.0)
    assert daily.iloc[2]["lag_1d_revenue"] == 200.0
    # rolling_7d_avg_revenue for day 3 uses only past days (day 1 & 2: (100+200)/2 = 150.0)
    assert daily.iloc[2]["rolling_7d_avg_revenue"] == 150.0
