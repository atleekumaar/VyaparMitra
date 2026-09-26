"""
Data loader module for ingesting raw tabular data into memory with standardized schemas.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
import yaml

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Loads raw CSV data files from disk and performs initial typing.
    Provides fallback handlers if non-critical auxiliary files are missing.
    """

    def __init__(self, raw_dir: str = "data/raw", config_path: Optional[str] = "configs/config.yaml") -> None:
        self.raw_dir = Path(raw_dir)
        self.config: Dict[str, Any] = {}
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)

    def load_transactions(self, filename: str = "transactions.csv") -> pd.DataFrame:
        """Load raw transaction records."""
        path = self.raw_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Required transaction file not found: {path}")
        logger.info("Loading transactions from %s", path)
        df = pd.read_csv(
            path,
            dtype={
                "transaction_id": "string",
                "merchant_id": "string",
                "customer_id": "string",
                "timestamp": "string",
                "product_id": "string",
                "product_category": "string",
                "payment_method": "string",
            },
        )
        # Numerical coercion
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
        df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0.0)
        return df

    def load_merchants(self, filename: str = "merchants.csv") -> pd.DataFrame:
        """Load merchant master data."""
        path = self.raw_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Merchant dimension table not found: {path}")
        logger.info("Loading merchants from %s", path)
        df = pd.read_csv(
            path,
            dtype={
                "merchant_id": "string",
                "merchant_name": "string",
                "business_type": "string",
                "city": "string",
                "state": "string",
                "pincode": "string",
            },
        )
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
        return df

    def load_customers(self, filename: str = "customers.csv") -> pd.DataFrame:
        """Load customer master data."""
        path = self.raw_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Customer dimension table not found: {path}")
        logger.info("Loading customers from %s", path)
        return pd.read_csv(
            path,
            dtype={
                "customer_id": "string",
                "customer_name": "string",
                "customer_type": "string",
                "city": "string",
                "signup_date": "string",
            },
        )

    def load_products(self, filename: str = "products.csv") -> pd.DataFrame:
        """Load product catalog."""
        path = self.raw_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Product catalog table not found: {path}")
        logger.info("Loading products from %s", path)
        df = pd.read_csv(
            path,
            dtype={
                "product_id": "string",
                "product_name": "string",
                "product_category": "string",
            },
        )
        df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce")
        df["selling_price"] = pd.to_numeric(df["selling_price"], errors="coerce")
        return df

    def load_festivals(self, filename: str = "festivals.csv") -> pd.DataFrame:
        """Load festival and holiday calendar."""
        path = self.raw_dir / filename
        if not path.exists():
            logger.warning("Festival file not found at %s. Returning empty festival DataFrame.", path)
            return pd.DataFrame(columns=["date", "festival_name", "festival_type", "is_festival", "festival_intensity"])
        logger.info("Loading festivals from %s", path)
        df = pd.read_csv(
            path,
            dtype={
                "date": "string",
                "festival_name": "string",
                "festival_type": "string",
            },
        )
        df["is_festival"] = pd.to_numeric(df["is_festival"], errors="coerce").fillna(0).astype(int)
        df["festival_intensity"] = pd.to_numeric(df["festival_intensity"], errors="coerce").fillna(0.0)
        return df

    def load_weather(self, filename: str = "weather.csv") -> pd.DataFrame:
        """Load weather observations."""
        path = self.raw_dir / filename
        if not path.exists():
            logger.warning("Weather file not found at %s. Returning empty weather DataFrame.", path)
            return pd.DataFrame(columns=["date", "city", "temperature", "humidity", "rainfall", "weather_condition"])
        logger.info("Loading weather data from %s", path)
        df = pd.read_csv(
            path,
            dtype={
                "date": "string",
                "city": "string",
                "weather_condition": "string",
            },
        )
        df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
        df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")
        df["rainfall"] = pd.to_numeric(df["rainfall"], errors="coerce")
        return df

    def load_all(self) -> Dict[str, pd.DataFrame]:
        """Load all core and auxiliary datasets."""
        return {
            "transactions": self.load_transactions(),
            "merchants": self.load_merchants(),
            "customers": self.load_customers(),
            "products": self.load_products(),
            "festivals": self.load_festivals(),
            "weather": self.load_weather(),
        }
