"""
Business summary and factual rule-based insight generation module.
Generates structured machine-readable JSON summaries and strictly factual,
observational statements without prescriptive recommendation language.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
import pandas as pd

from src.schemas.analytics_schema import BusinessSummary

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Produces verified machine-readable business summaries and factual observations."""

    def __init__(self) -> None:
        pass

    def generate_summary(
        self,
        sales_kpis: Any,
        monthly_sales: pd.DataFrame,
        customer_kpis: Any,
        top_category: str,
        top_product: str,
        peak_periods: Dict[str, Any],
        payment_summary: pd.DataFrame,
        festival_summary: Dict[str, Any],
        weather_summary: Dict[str, Any],
        category_summary: pd.DataFrame,
    ) -> BusinessSummary:
        """
        Synthesizes core analytical outputs into a canonical BusinessSummary object.
        """
        # Determine latest month period and growth
        period_str = "Full History"
        rev_growth = None
        if not monthly_sales.empty:
            latest_row = monthly_sales.iloc[-1]
            period_str = str(latest_row["period_key"])
            if len(monthly_sales) > 1 and "revenue_growth_pct" in latest_row:
                rev_growth = float(latest_row["revenue_growth_pct"])

        peak_wkday = peak_periods.get("highest_revenue_weekday", {}).get("day_name", "N/A")
        peak_hr = peak_periods.get("highest_revenue_hour", {}).get("hour", 0)

        # Dominant payment method
        dom_pm = "UPI"
        if not payment_summary.empty:
            dom_pm = str(payment_summary.iloc[0]["payment_method"])
            dom_pm_share = float(payment_summary.iloc[0]["orders_share"]) * 100.0

        # Generate rule-based factual insight statements (strictly descriptive, no prescriptive advice)
        insights: List[str] = []

        if rev_growth is not None:
            direction = "increased" if rev_growth >= 0 else "decreased"
            insights.append(f"Revenue {direction} by {abs(rev_growth):.1f}% in {period_str} compared with the previous month.")

        insights.append(f"{peak_wkday} generated the highest observed sales volume among all weekdays.")
        insights.append(f"Peak transactional activity occurred between {peak_hr:02d}:00 and {peak_hr+1:02d}:00.")
        insights.append(f"{dom_pm} was the dominant payment channel, representing {dom_pm_share:.1f}% of recorded orders.")

        if not category_summary.empty:
            top_cat_share = float(category_summary.iloc[0]["revenue_share"]) * 100.0
            insights.append(f"{top_category} was the highest-performing category, contributing {top_cat_share:.1f}% of total product revenue.")

        if festival_summary and "festival_revenue_difference_pct" in festival_summary:
            f_diff = festival_summary["festival_revenue_difference_pct"]
            f_dir = "higher" if f_diff >= 0 else "lower"
            insights.append(f"Observed daily revenue on festival dates was {abs(f_diff):.1f}% {f_dir} than on non-festival dates.")

        if weather_summary and "rainy_revenue_difference_pct" in weather_summary:
            w_diff = weather_summary["rainy_revenue_difference_pct"]
            w_dir = "higher" if w_diff >= 0 else "lower"
            insights.append(f"Rainy days were associated with {abs(w_diff):.1f}% {w_dir} observed revenue compared to dry days.")

        fest_uplift = festival_summary.get("festival_revenue_difference_pct") if festival_summary else None
        rain_uplift = weather_summary.get("rainy_revenue_difference_pct") if weather_summary else None

        return BusinessSummary(
            period=period_str,
            total_revenue=float(sales_kpis.total_revenue),
            total_orders=int(sales_kpis.total_orders),
            total_units=int(sales_kpis.total_units),
            average_order_value=float(sales_kpis.average_order_value),
            revenue_growth_pct=rev_growth,
            active_customers=int(customer_kpis.active_customers),
            top_revenue_category=top_category,
            top_revenue_product=top_product,
            peak_weekday=peak_wkday,
            peak_hour=peak_hr,
            dominant_payment_method=dom_pm,
            festival_day_revenue_uplift_pct=fest_uplift,
            rainy_day_revenue_uplift_pct=rain_uplift,
            key_insights=insights,
        )
