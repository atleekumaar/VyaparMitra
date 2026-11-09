"""
Sales Analytics Engine for VyaparMitra
Implements verified statistical sales intelligence matching SalesKPISet schema.
"""
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from src.schemas.analytics_schema import SalesKPISet


class SalesAnalytics:
    def __init__(self, transactions_df: pd.DataFrame, daily_df: Optional[pd.DataFrame] = None):
        self.df = transactions_df.copy()
        self.daily_df = daily_df.copy() if daily_df is not None else pd.DataFrame()
        if not self.df.empty and 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
            if 'timestamp' in self.df.columns:
                self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])

    def _filter_dataset(
        self,
        merchant_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        df = self.df.copy()
        if merchant_id and not df.empty and 'merchant_id' in df.columns:
            df = df[df['merchant_id'] == merchant_id]
        if start_date and not df.empty and 'date' in df.columns:
            df = df[df['date'] >= pd.to_datetime(start_date)]
        if end_date and not df.empty and 'date' in df.columns:
            df = df[df['date'] <= pd.to_datetime(end_date)]
        return df

    def get_core_kpis(
        self,
        merchant_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> SalesKPISet:
        """Calculates core sales KPIs with strict zero-division safeguards."""
        df = self._filter_dataset(merchant_id, start_date, end_date)
        if df.empty:
            return SalesKPISet(
                total_revenue=0.0,
                total_orders=0,
                total_units=0,
                average_order_value=0.0,
                average_units_per_order=0.0,
                discount_total=0.0,
                discount_rate=0.0,
                revenue_per_active_day=0.0
            )

        total_rev = float(df['net_amount'].sum()) if 'net_amount' in df.columns else float(df.get('total_amount', pd.Series([0])).sum())
        total_orders = int(len(df))
        total_units = int(df['quantity'].sum()) if 'quantity' in df.columns else total_orders

        aov = total_rev / total_orders if total_orders > 0 else 0.0
        avg_units = total_units / total_orders if total_orders > 0 else 0.0

        disc_total = float(df['discount_amount'].sum()) if 'discount_amount' in df.columns else 0.0
        gross_total = float(df['total_amount'].sum()) if 'total_amount' in df.columns else (total_rev + disc_total)
        disc_rate = (disc_total / gross_total) if gross_total > 0 else 0.0

        active_days = df['date'].dt.date.nunique() if 'date' in df.columns else 1
        rev_per_day = total_rev / active_days if active_days > 0 else 0.0

        return SalesKPISet(
            total_revenue=round(total_rev, 2),
            total_orders=total_orders,
            total_units=total_units,
            average_order_value=round(aov, 2),
            average_units_per_order=round(avg_units, 2),
            discount_total=round(disc_total, 2),
            discount_rate=round(disc_rate, 4),
            revenue_per_active_day=round(rev_per_day, 2)
        )

    def get_period_comparison(
        self,
        frequency: str = "monthly",
        merchant_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Groups sales by frequency and computes period-over-period differences."""
        df = self._filter_dataset(merchant_id, start_date, end_date)
        if df.empty:
            return pd.DataFrame(columns=["period", "period_key", "revenue", "revenue_change", "revenue_growth_pct"])

        period_col = df['date'].dt.to_period('M') if frequency == "monthly" else df['date'].dt.to_period('W')
        grouped = df.groupby(period_col).agg(
            revenue=('net_amount', 'sum'),
            orders=('transaction_id', 'count') if 'transaction_id' in df.columns else ('net_amount', 'count'),
            units=('quantity', 'sum') if 'quantity' in df.columns else ('net_amount', 'count')
        ).reset_index()

        grouped['period'] = grouped['date'].astype(str)
        grouped['period_key'] = grouped['period']
        grouped['revenue_change'] = grouped['revenue'].diff().fillna(0.0).round(2)
        grouped['revenue_growth_pct'] = (
            (grouped['revenue_change'] / grouped['revenue'].shift(1)) * 100.0
        ).fillna(0.0).round(2)

        return grouped

    def get_daily_sales_analytics(self, merchant_id: Optional[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Aggregates daily sales and identifies highest/lowest revenue days."""
        df = self._filter_dataset(merchant_id)
        if df.empty:
            return pd.DataFrame(), {}

        daily_df = df.groupby(df['date'].dt.strftime('%Y-%m-%d')).agg(
            revenue=('net_amount', 'sum'),
            orders=('transaction_id', 'count') if 'transaction_id' in df.columns else ('net_amount', 'count')
        ).reset_index().rename(columns={'date': 'date'})

        daily_df = daily_df.sort_values('date').reset_index(drop=True)

        highest_row = daily_df.loc[daily_df['revenue'].idxmax()]
        lowest_row = daily_df.loc[daily_df['revenue'].idxmin()]

        stats = {
            "highest_revenue_day": {
                "date": str(highest_row['date']),
                "revenue": float(highest_row['revenue'])
            },
            "lowest_revenue_day": {
                "date": str(lowest_row['date']),
                "revenue": float(lowest_row['revenue'])
            }
        }

        return daily_df, stats
