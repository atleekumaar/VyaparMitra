"""
Data quality validation module.
Validates missing values, duplicates, numeric sanity, referential integrity, and timestamps.
Produces structured JSON and Markdown quality reports.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class TransactionPydanticSchema(BaseModel):
    """Pydantic model for individual transaction record validation."""
    transaction_id: str = Field(..., min_length=1)
    merchant_id: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    timestamp: str = Field(..., min_length=1)
    product_id: str = Field(..., min_length=1)
    product_category: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0.0)
    discount: float = Field(default=0.0, ge=0.0)
    payment_method: str = Field(..., min_length=1)

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        allowed = {"UPI", "CASH", "CARD", "NETBANKING", "WALLET"}
        if v.upper() not in allowed:
            raise ValueError(f"Invalid payment method: {v}")
        return v.upper()


@dataclass
class ValidationReport:
    """Encapsulates validation metrics and statuses."""
    total_records: int
    valid_records: int
    invalid_records: int
    missing_values_count: int
    missing_values_pct: float
    duplicate_ids_count: int
    invalid_prices_count: int
    invalid_quantities_count: int
    invalid_discounts_count: int
    invalid_timestamps_count: int
    referential_integrity_status: str
    timestamp_validation_status: str
    overall_status: str
    issues_breakdown: Dict[str, int]

    def to_markdown(self) -> str:
        """Render report as human-readable markdown matching specification."""
        return f"""# DATA QUALITY REPORT

**Total Records:** {self.total_records:,}
**Valid Records:** {self.valid_records:,}
**Quarantined / Rejected:** {self.invalid_records:,}

### Summary Metrics
* **Missing Values:** {self.missing_values_pct:.2f}% ({self.missing_values_count:,} fields)
* **Duplicate IDs:** {self.duplicate_ids_count}
* **Invalid Prices:** {self.invalid_prices_count}
* **Invalid Quantities:** {self.invalid_quantities_count}
* **Invalid Discounts:** {self.invalid_discounts_count}
* **Invalid Timestamps:** {self.invalid_timestamps_count}

### Integrity Checks
* **Referential Integrity:** {self.referential_integrity_status}
* **Timestamp Validation:** {self.timestamp_validation_status}

### Rejection Breakdown
{chr(10).join(f"- **{k}**: {v}" for k, v in self.issues_breakdown.items()) if self.issues_breakdown else "- No issues detected."}

---
### **Overall Status: {self.overall_status}**
"""


class DataValidator:
    """
    Automated validator for transaction data quality and referential integrity.
    """

    def __init__(
        self,
        max_discount_rate: float = 0.90,
        allowed_payment_methods: Optional[List[str]] = None,
    ) -> None:
        self.max_discount_rate = max_discount_rate
        self.allowed_payment_methods = allowed_payment_methods or ["UPI", "CASH", "CARD", "NETBANKING", "WALLET"]

    def validate(
        self,
        transactions: pd.DataFrame,
        merchants: pd.DataFrame,
        customers: pd.DataFrame,
        products: pd.DataFrame,
    ) -> Tuple[ValidationReport, pd.Series]:
        """
        Validate transaction dataset and return a ValidationReport plus a Series of rejection reasons.
        Empty rejection reason string means the record is valid.
        """
        n_records = len(transactions)
        logger.info("Starting validation on %d transaction records...", n_records)

        rejection_reasons = pd.Series([""] * n_records, index=transactions.index)
        issues_breakdown: Dict[str, int] = {}

        def record_issue(mask: pd.Series, reason: str) -> None:
            count = int(mask.sum())
            if count > 0:
                issues_breakdown[reason] = count
                # Append reason to existing reasons
                rejection_reasons[mask] = rejection_reasons[mask].apply(
                    lambda r: f"{r}; {reason}" if r else reason
                )

        # 1. Missing Values (null, NaN, empty strings)
        missing_mask = pd.Series(False, index=transactions.index)
        critical_fields = ["transaction_id", "merchant_id", "customer_id", "timestamp", "product_id", "quantity", "unit_price"]
        total_missing_fields = 0
        for col in critical_fields:
            if col in transactions.columns:
                null_or_empty = transactions[col].isna() | (transactions[col].astype(str).str.strip() == "") | (transactions[col].astype(str).str.lower() == "nan")
                col_missing = int(null_or_empty.sum())
                total_missing_fields += col_missing
                missing_mask = missing_mask | null_or_empty

        record_issue(missing_mask, "MISSING_CRITICAL_FIELD")

        # 2. Duplicate transaction IDs
        duplicate_mask = transactions["transaction_id"].duplicated(keep="first")
        record_issue(duplicate_mask, "DUPLICATE_TRANSACTION_ID")

        # 3. Numeric Sanity: Quantities
        qty_numeric = pd.to_numeric(transactions["quantity"], errors="coerce")
        invalid_qty_mask = qty_numeric.isna() | (qty_numeric <= 0) | (qty_numeric % 1 != 0)
        record_issue(invalid_qty_mask, "INVALID_QUANTITY")

        # 4. Numeric Sanity: Unit Prices
        price_numeric = pd.to_numeric(transactions["unit_price"], errors="coerce")
        invalid_price_mask = price_numeric.isna() | (price_numeric < 0)
        record_issue(invalid_price_mask, "INVALID_UNIT_PRICE")

        # 5. Numeric Sanity: Discounts
        disc_numeric = pd.to_numeric(transactions["discount"], errors="coerce").fillna(0.0)
        total_expected_amt = qty_numeric * price_numeric
        invalid_discount_mask = (disc_numeric < 0) | (disc_numeric > total_expected_amt)
        record_issue(invalid_discount_mask, "INVALID_DISCOUNT_AMOUNT")

        # 6. Referential Integrity
        known_merchants = set(merchants["merchant_id"].dropna().astype(str))
        known_customers = set(customers["customer_id"].dropna().astype(str))
        known_products = set(products["product_id"].dropna().astype(str))

        missing_merchant_ref = ~transactions["merchant_id"].astype(str).isin(known_merchants)
        missing_customer_ref = ~transactions["customer_id"].astype(str).isin(known_customers)
        missing_product_ref = ~transactions["product_id"].astype(str).isin(known_products)

        record_issue(missing_merchant_ref, "FOREIGN_KEY_MERCHANT_NOT_FOUND")
        record_issue(missing_customer_ref, "FOREIGN_KEY_CUSTOMER_NOT_FOUND")
        record_issue(missing_product_ref, "FOREIGN_KEY_PRODUCT_NOT_FOUND")

        ref_integrity_passed = not (missing_merchant_ref.any() or missing_customer_ref.any() or missing_product_ref.any())

        # 7. Timestamp validation
        parsed_ts = pd.to_datetime(transactions["timestamp"], errors="coerce")
        invalid_ts_mask = parsed_ts.isna() | (parsed_ts.dt.year < 2020) | (parsed_ts.dt.year > 2035)
        record_issue(invalid_ts_mask, "INVALID_TIMESTAMP")
        ts_validation_passed = bool((~invalid_ts_mask).all())

        # Calculate counts
        invalid_mask = rejection_reasons != ""
        invalid_count = int(invalid_mask.sum())
        valid_count = n_records - invalid_count
        missing_pct = (total_missing_fields / (n_records * len(critical_fields))) * 100 if n_records > 0 else 0.0

        overall_status = "PASS" if (invalid_count / max(1, n_records) < 0.05 and ref_integrity_passed) else "FAIL"

        report = ValidationReport(
            total_records=n_records,
            valid_records=valid_count,
            invalid_records=invalid_count,
            missing_values_count=total_missing_fields,
            missing_values_pct=missing_pct,
            duplicate_ids_count=int(duplicate_mask.sum()),
            invalid_prices_count=int(invalid_price_mask.sum()),
            invalid_quantities_count=int(invalid_qty_mask.sum()),
            invalid_discounts_count=int(invalid_discount_mask.sum()),
            invalid_timestamps_count=int(invalid_ts_mask.sum()),
            referential_integrity_status="PASS" if ref_integrity_passed else "FAIL",
            timestamp_validation_status="PASS" if ts_validation_passed else "FAIL",
            overall_status=overall_status,
            issues_breakdown=issues_breakdown,
        )

        logger.info(
            "Validation finished: %d valid, %d invalid (Overall: %s)",
            valid_count,
            invalid_count,
            overall_status,
        )
        return report, rejection_reasons

    def save_reports(
        self,
        report: ValidationReport,
        reports_dir: str = "data/quality_reports",
    ) -> Tuple[Path, Path]:
        """Save report to JSON and Markdown files."""
        out_dir = Path(reports_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        json_path = out_dir / "data_quality_report.json"
        md_path = out_dir / "data_quality_report.md"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report.to_markdown())

        logger.info("Saved data quality reports to %s and %s", json_path, md_path)
        return json_path, md_path
