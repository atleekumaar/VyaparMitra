"""
Payment method analytics module for VyaparMitra Phase 2.
Analyzes tender types (UPI, Cash, Card, NetBanking), volume, revenue shares, and AOV.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class PaymentAnalytics:
    """Computes payment channel volume, revenue contribution, and average ticket size."""

    def __init__(self, transactions_df: pd.DataFrame) -> None:
        self.transactions_df = transactions_df.copy()

    def get_payment_summary(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """
        Calculates payment method breakdown:
        [payment_method, payment_method_orders, payment_method_revenue,
         orders_share, revenue_share, payment_method_aov]
        """
        tx = self.transactions_df
        if merchant_id:
            tx = tx[tx["merchant_id"] == merchant_id]
        if tx.empty:
            return pd.DataFrame(columns=[
                "payment_method", "payment_method_orders", "payment_method_revenue",
                "orders_share", "revenue_share", "payment_method_aov"
            ])

        total_orders = len(tx)
        total_revenue = tx["net_amount"].sum()

        grouped = tx.groupby("payment_method").agg(
            payment_method_orders=("transaction_id", "count"),
            payment_method_revenue=("net_amount", "sum"),
        ).reset_index()

        grouped["payment_method_revenue"] = grouped["payment_method_revenue"].round(2)
        grouped["orders_share"] = (grouped["payment_method_orders"] / max(1, total_orders)).round(4)
        grouped["revenue_share"] = (grouped["payment_method_revenue"] / max(1e-9, total_revenue)).round(4)
        grouped["payment_method_aov"] = (
            grouped["payment_method_revenue"] / grouped["payment_method_orders"].clip(lower=1)
        ).round(2)

        return grouped.sort_values(by="payment_method_revenue", ascending=False).reset_index(drop=True)
