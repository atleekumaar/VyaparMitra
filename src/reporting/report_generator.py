"""
Markdown report generator for VyaparMitra Phase 2 Business Intelligence Engine.
Formats core KPIs, category performance, temporal peaks, and factual observations into an executive report.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict
import pandas as pd

from src.schemas.analytics_schema import BusinessSummary

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates formatted business_summary.md."""

    def __init__(self) -> None:
        pass

    def generate_markdown_report(
        self,
        summary: BusinessSummary,
        category_df: pd.DataFrame,
        product_rankings_df: pd.DataFrame,
        payment_df: pd.DataFrame,
        trend_df: pd.DataFrame,
    ) -> str:
        """Constructs human-readable markdown business intelligence report."""
        top_cats = category_df.head(5)
        top_prods = product_rankings_df.head(5)

        insights_md = "\n".join(f"* {insight}" for insight in summary.key_insights)

        cat_rows = "\n".join(
            f"| {row['product_category']} | ₹{row['category_revenue']:,.2f} | {row['category_orders']:,} | {row['revenue_share']*100:.1f}% | ₹{row['average_order_value']:,.2f} |"
            for _, row in top_cats.iterrows()
        )

        prod_rows = "\n".join(
            f"| {row['product_name']} | {row['product_category']} | ₹{row['revenue']:,.2f} | {row['units']:,} | {row['orders']:,} |"
            for _, row in top_prods.iterrows()
        )

        pay_rows = "\n".join(
            f"| {row['payment_method']} | {row['payment_method_orders']:,} | {row['orders_share']*100:.1f}% | ₹{row['payment_method_revenue']:,.2f} | {row['revenue_share']*100:.1f}% | ₹{row['payment_method_aov']:,.2f} |"
            for _, row in payment_df.iterrows()
        )

        md = f"""# VyaparMitra — Business Intelligence & Analytics Report (Phase 2)

**Report Scope:** {summary.period}  
**Generated Mode:** Descriptive & Diagnostic Analytics  

---

## 1. Executive Performance Scorecard

| Core Metric | Observed Value | Description |
| :--- | :--- | :--- |
| **Total Net Revenue** | **₹{summary.total_revenue:,.2f}** | Cumulative realized sales revenue |
| **Total Orders** | **{summary.total_orders:,}** | Completed transaction volume |
| **Total Units Sold** | **{summary.total_units:,}** | Total physical quantity of items |
| **Average Order Value (AOV)** | **₹{summary.average_order_value:,.2f}** | Mean revenue generated per transaction |
| **Active Customer Reach** | **{summary.active_customers:,}** | Distinct purchasing customers |
| **Peak Operating Weekday** | **{summary.peak_weekday}** | Day with highest observed revenue |
| **Peak Operational Hour** | **{summary.peak_hour:02d}:00 – {summary.peak_hour+1:02d}:00** | Time window with highest order volume |
| **Dominant Payment Channel** | **{summary.dominant_payment_method}** | Leading settlement method |

---

## 2. Key Factual Observations (Diagnostic Insights)

{insights_md}

---

## 3. Category Contribution (Top 5)

| Category | Net Revenue | Orders | Revenue Share | Average Order Value |
| :--- | :--- | :--- | :--- | :--- |
{cat_rows}

---

## 4. Leading Products by Net Sales (Top 5)

| Product Title | Category | Net Revenue | Units Sold | Orders Count |
| :--- | :--- | :--- | :--- | :--- |
{prod_rows}

---

## 5. Payment Channel Breakdown

| Payment Channel | Orders | Orders Share | Net Revenue | Revenue Share | Ticket Size (AOV) |
| :--- | :--- | :--- | :--- | :--- | :--- |
{pay_rows}

---

## 6. Phase 3 Machine Learning Consumption Notice

> [!NOTE]
> All analytical metrics above represent verified historical observations. Phase 3 (Predictive AI) will consume these structured datasets directly from `data/analytics/` to build demand forecasts, customer lifetime value estimates, and inventory alerts.
"""
        return md
