"""
Unit tests for data cleaning and quarantine isolation.
"""

from pathlib import Path
import pandas as pd
import pytest
from src.cleaning.cleaner import DataCleaner


def test_quarantine_isolation(tmp_path):
    proc_dir = tmp_path / "processed"
    quar_dir = tmp_path / "quarantine"

    cleaner = DataCleaner(processed_dir=str(proc_dir), quarantine_dir=str(quar_dir))

    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002", "TX003"],
        "merchant_id": ["M001", "M001", "M001"],
        "customer_id": ["C001", "C001", "C001"],
        "timestamp": ["2026-01-10 10:30:00", "2026-01-10 10:35:00", "2026-01-10 10:40:00"],
        "product_id": ["P001", "P001", "P001"],
        "product_category": ["Bread", "Bread", "Bread"],
        "quantity": [1, 0, 2],
        "unit_price": [50.0, 50.0, -10.0],
        "discount": [0.0, 0.0, 0.0],
        "payment_method": ["upi", "cash", "upi"],
    })

    reasons = pd.Series(["", "INVALID_QUANTITY", "INVALID_UNIT_PRICE"])

    clean_tx, quar_tx = cleaner.clean_transactions(tx, reasons)

    assert len(clean_tx) == 1
    assert len(quar_tx) == 2
    assert clean_tx.iloc[0]["transaction_id"] == "TX001"
    assert clean_tx.iloc[0]["payment_method"] == "UPI"  # Standardized casing

    # Check files created
    quar_file = quar_dir / "quarantined_transactions.csv"
    assert quar_file.exists()
    saved_quar = pd.read_csv(quar_file)
    assert len(saved_quar) == 2
    assert "rejection_reason" in saved_quar.columns


def test_merchant_and_customer_cleaning(tmp_path):
    proc_dir = tmp_path / "processed"
    quar_dir = tmp_path / "quarantine"

    cleaner = DataCleaner(processed_dir=str(proc_dir), quarantine_dir=str(quar_dir))

    merchants = pd.DataFrame({
        "merchant_id": ["M001", "M001"],  # Duplicate
        "merchant_name": [" store one ", "store one duplicate"],
        "business_type": ["bakery", "bakery"],
        "city": [" Noida ", " Noida "],
        "state": ["Uttar Pradesh", "Uttar Pradesh"],
        "pincode": ["201301", "201301"],
        "latitude": [28.535512, 28.535512],
        "longitude": [77.391012, 77.391012],
    })

    clean_m = cleaner.clean_merchants(merchants)
    assert len(clean_m) == 1
    assert clean_m.iloc[0]["merchant_name"] == "store one"
    assert clean_m.iloc[0]["business_type"] == "Bakery"
    assert clean_m.iloc[0]["city"] == "Noida"
    assert clean_m.iloc[0]["latitude"] == 28.5355
