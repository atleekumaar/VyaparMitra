"""
Unit tests for data validation, quality reporting, and referential integrity.
"""

import pandas as pd
import pytest
from src.validation.validator import DataValidator


@pytest.fixture
def sample_reference_data():
    merchants = pd.DataFrame({
        "merchant_id": ["M001", "M002"],
        "merchant_name": ["Store 1", "Store 2"],
        "city": ["Noida", "Delhi"],
    })
    customers = pd.DataFrame({
        "customer_id": ["C001", "C002"],
        "customer_name": ["Alice", "Bob"],
    })
    products = pd.DataFrame({
        "product_id": ["P001", "P002"],
        "product_name": ["Bread", "Milk"],
        "selling_price": [50.0, 60.0],
    })
    return merchants, customers, products


def test_clean_transactions_pass_validation(sample_reference_data):
    merchants, customers, products = sample_reference_data
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002"],
        "merchant_id": ["M001", "M002"],
        "customer_id": ["C001", "C002"],
        "timestamp": ["2026-01-10 10:30:00", "2026-01-11 12:00:00"],
        "product_id": ["P001", "P002"],
        "product_category": ["Bread", "Dairy"],
        "quantity": [2, 1],
        "unit_price": [50.0, 60.0],
        "discount": [5.0, 0.0],
        "payment_method": ["UPI", "CASH"],
    })

    validator = DataValidator()
    report, reasons = validator.validate(tx, merchants, customers, products)

    assert report.total_records == 2
    assert report.valid_records == 2
    assert report.invalid_records == 0
    assert report.referential_integrity_status == "PASS"
    assert report.timestamp_validation_status == "PASS"
    assert report.overall_status == "PASS"
    assert (reasons == "").all()


def test_duplicate_transaction_detection(sample_reference_data):
    merchants, customers, products = sample_reference_data
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX001"],  # Duplicate ID
        "merchant_id": ["M001", "M001"],
        "customer_id": ["C001", "C001"],
        "timestamp": ["2026-01-10 10:30:00", "2026-01-10 10:35:00"],
        "product_id": ["P001", "P001"],
        "product_category": ["Bread", "Bread"],
        "quantity": [1, 1],
        "unit_price": [50.0, 50.0],
        "discount": [0.0, 0.0],
        "payment_method": ["UPI", "UPI"],
    })

    validator = DataValidator()
    report, reasons = validator.validate(tx, merchants, customers, products)

    assert report.duplicate_ids_count == 1
    assert "DUPLICATE_TRANSACTION_ID" in reasons.iloc[1]


def test_invalid_prices_and_quantities(sample_reference_data):
    merchants, customers, products = sample_reference_data
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002"],
        "merchant_id": ["M001", "M002"],
        "customer_id": ["C001", "C002"],
        "timestamp": ["2026-01-10 10:30:00", "2026-01-11 12:00:00"],
        "product_id": ["P001", "P002"],
        "product_category": ["Bread", "Dairy"],
        "quantity": [0, 2],         # Invalid quantity: 0
        "unit_price": [50.0, -10.0],  # Invalid price: negative
        "discount": [0.0, 0.0],
        "payment_method": ["UPI", "CASH"],
    })

    validator = DataValidator()
    report, reasons = validator.validate(tx, merchants, customers, products)

    assert report.invalid_quantities_count == 1
    assert report.invalid_prices_count == 1
    assert "INVALID_QUANTITY" in reasons.iloc[0]
    assert "INVALID_UNIT_PRICE" in reasons.iloc[1]


def test_referential_integrity_violation(sample_reference_data):
    merchants, customers, products = sample_reference_data
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002"],
        "merchant_id": ["M999", "M001"],  # M999 does not exist
        "customer_id": ["C001", "C999"],  # C999 does not exist
        "timestamp": ["2026-01-10 10:30:00", "2026-01-11 12:00:00"],
        "product_id": ["P001", "P999"],  # P999 does not exist
        "product_category": ["Bread", "Dairy"],
        "quantity": [1, 1],
        "unit_price": [50.0, 60.0],
        "discount": [0.0, 0.0],
        "payment_method": ["UPI", "CASH"],
    })

    validator = DataValidator()
    report, reasons = validator.validate(tx, merchants, customers, products)

    assert report.referential_integrity_status == "FAIL"
    assert "FOREIGN_KEY_MERCHANT_NOT_FOUND" in reasons.iloc[0]
    assert "FOREIGN_KEY_CUSTOMER_NOT_FOUND" in reasons.iloc[1]
    assert "FOREIGN_KEY_PRODUCT_NOT_FOUND" in reasons.iloc[1]


def test_invalid_discounts(sample_reference_data):
    merchants, customers, products = sample_reference_data
    tx = pd.DataFrame({
        "transaction_id": ["TX001", "TX002"],
        "merchant_id": ["M001", "M002"],
        "customer_id": ["C001", "C002"],
        "timestamp": ["2026-01-10 10:30:00", "2026-01-11 12:00:00"],
        "product_id": ["P001", "P002"],
        "product_category": ["Bread", "Dairy"],
        "quantity": [1, 2],
        "unit_price": [50.0, 50.0],
        "discount": [-5.0, 150.0],  # Negative discount and discount > total_amount
        "payment_method": ["UPI", "CASH"],
    })

    validator = DataValidator()
    report, reasons = validator.validate(tx, merchants, customers, products)

    assert report.invalid_discounts_count == 2
    assert "INVALID_DISCOUNT_AMOUNT" in reasons.iloc[0]
    assert "INVALID_DISCOUNT_AMOUNT" in reasons.iloc[1]
