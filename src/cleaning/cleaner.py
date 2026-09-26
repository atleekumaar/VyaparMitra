"""
Data cleaning and quarantine pipeline.
Isolates rejected records to data/quarantine/ with explanations.
Standardizes types, categories, timestamps, and numerical scales into data/processed/.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Cleans raw datasets, isolates corrupt/invalid records into quarantine,
    and produces standardized datasets in data/processed.
    """

    def __init__(
        self,
        processed_dir: str = "data/processed",
        quarantine_dir: str = "data/quarantine",
    ) -> None:
        self.processed_dir = Path(processed_dir)
        self.quarantine_dir = Path(quarantine_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def clean_transactions(
        self,
        transactions: pd.DataFrame,
        rejection_reasons: pd.Series,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split transactions into valid and quarantined subsets, standardize fields.
        """
        logger.info("Cleaning transactions dataset (total: %d)...", len(transactions))
        is_invalid = rejection_reasons != ""
        
        # 1. Quarantine records
        quarantined_df = transactions[is_invalid].copy()
        quarantined_df["rejection_reason"] = rejection_reasons[is_invalid]
        
        quarantine_file = self.quarantine_dir / "quarantined_transactions.csv"
        quarantined_df.to_csv(quarantine_file, index=False)
        logger.info("Quarantined %d invalid records to %s", len(quarantined_df), quarantine_file)

        # 2. Valid records
        clean_df = transactions[~is_invalid].copy()

        # Deduplicate on transaction_id if any remained
        clean_df = clean_df.drop_duplicates(subset=["transaction_id"], keep="first")

        # Standardize strings & categorical
        clean_df["transaction_id"] = clean_df["transaction_id"].astype(str).str.strip()
        clean_df["merchant_id"] = clean_df["merchant_id"].astype(str).str.strip()
        clean_df["customer_id"] = clean_df["customer_id"].astype(str).str.strip()
        clean_df["product_id"] = clean_df["product_id"].astype(str).str.strip()
        clean_df["product_category"] = clean_df["product_category"].astype(str).str.strip()
        clean_df["payment_method"] = clean_df["payment_method"].astype(str).str.strip().str.upper()

        # Standardize timestamps
        clean_df["timestamp"] = pd.to_datetime(clean_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")

        # Standardize numeric columns
        clean_df["quantity"] = clean_df["quantity"].astype(int)
        clean_df["unit_price"] = clean_df["unit_price"].astype(float).round(2)
        clean_df["discount"] = clean_df["discount"].astype(float).round(2)

        # Reset index
        clean_df.reset_index(drop=True, inplace=True)

        # Persist processed
        clean_df.to_parquet(self.processed_dir / "clean_transactions.parquet", index=False)
        clean_df.to_csv(self.processed_dir / "clean_transactions.csv", index=False)
        logger.info("Processed clean transactions: %d records saved", len(clean_df))

        return clean_df, quarantined_df

    def clean_merchants(self, merchants: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize merchant master records."""
        df = merchants.drop_duplicates(subset=["merchant_id"]).copy()
        df["merchant_id"] = df["merchant_id"].astype(str).str.strip()
        df["merchant_name"] = df["merchant_name"].astype(str).str.strip()
        df["business_type"] = df["business_type"].astype(str).str.strip().str.title()
        df["city"] = df["city"].astype(str).str.strip()
        df["state"] = df["state"].astype(str).str.strip()
        df["pincode"] = df["pincode"].astype(str).str.strip()
        df["latitude"] = df["latitude"].astype(float).round(4)
        df["longitude"] = df["longitude"].astype(float).round(4)
        df.reset_index(drop=True, inplace=True)

        df.to_parquet(self.processed_dir / "clean_merchants.parquet", index=False)
        df.to_csv(self.processed_dir / "clean_merchants.csv", index=False)
        return df

    def clean_customers(self, customers: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize customer master records."""
        df = customers.drop_duplicates(subset=["customer_id"]).copy()
        df["customer_id"] = df["customer_id"].astype(str).str.strip()
        df["customer_name"] = df["customer_name"].astype(str).str.strip()
        df["customer_type"] = df["customer_type"].astype(str).str.strip().str.title()
        df["city"] = df["city"].astype(str).str.strip()
        df["signup_date"] = pd.to_datetime(df["signup_date"]).dt.strftime("%Y-%m-%d")
        df.reset_index(drop=True, inplace=True)

        df.to_parquet(self.processed_dir / "clean_customers.parquet", index=False)
        df.to_csv(self.processed_dir / "clean_customers.csv", index=False)
        return df

    def clean_products(self, products: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize product master records."""
        df = products.drop_duplicates(subset=["product_id"]).copy()
        df["product_id"] = df["product_id"].astype(str).str.strip()
        df["product_name"] = df["product_name"].astype(str).str.strip()
        df["product_category"] = df["product_category"].astype(str).str.strip()
        df["unit_cost"] = df["unit_cost"].astype(float).round(2)
        df["selling_price"] = df["selling_price"].astype(float).round(2)
        df.reset_index(drop=True, inplace=True)

        df.to_parquet(self.processed_dir / "clean_products.parquet", index=False)
        df.to_csv(self.processed_dir / "clean_products.csv", index=False)
        return df

    def clean_festivals(self, festivals: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize festival calendar records."""
        df = festivals.copy()
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df["festival_name"] = df["festival_name"].astype(str).str.strip()
            df["festival_type"] = df["festival_type"].astype(str).str.strip()
            df["is_festival"] = df["is_festival"].astype(int)
            df["festival_intensity"] = df["festival_intensity"].astype(float).round(2)
            df = df.drop_duplicates().sort_values(by=["date", "festival_name"]).reset_index(drop=True)

        df.to_parquet(self.processed_dir / "clean_festivals.parquet", index=False)
        df.to_csv(self.processed_dir / "clean_festivals.csv", index=False)
        return df

    def clean_weather(self, weather: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize weather observations."""
        df = weather.copy()
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df["city"] = df["city"].astype(str).str.strip()
            df["temperature"] = df["temperature"].astype(float).round(1)
            df["humidity"] = df["humidity"].astype(float).round(1)
            df["rainfall"] = df["rainfall"].astype(float).round(1)
            df["weather_condition"] = df["weather_condition"].astype(str).str.strip()
            df = df.drop_duplicates(subset=["date", "city"]).sort_values(by=["date", "city"]).reset_index(drop=True)

        df.to_parquet(self.processed_dir / "clean_weather.parquet", index=False)
        df.to_csv(self.processed_dir / "clean_weather.csv", index=False)
        return df

    def clean_all(
        self,
        raw_data: Dict[str, pd.DataFrame],
        rejection_reasons: pd.Series,
    ) -> Dict[str, pd.DataFrame]:
        """Execute complete cleaning routine on all loaded datasets."""
        clean_tx, quarantined_tx = self.clean_transactions(
            raw_data["transactions"], rejection_reasons
        )
        clean_merchants = self.clean_merchants(raw_data["merchants"])
        clean_customers = self.clean_customers(raw_data["customers"])
        clean_products = self.clean_products(raw_data["products"])
        clean_festivals = self.clean_festivals(raw_data["festivals"])
        clean_weather = self.clean_weather(raw_data["weather"])

        return {
            "transactions": clean_tx,
            "quarantined": quarantined_tx,
            "merchants": clean_merchants,
            "customers": clean_customers,
            "products": clean_products,
            "festivals": clean_festivals,
            "weather": clean_weather,
        }
