"""
Forecast Service for VyaparMitra Phase 6 API.
Serves 7-day predictive sales and SKU demand forecasts from Phase 3 ML artifacts,
with graceful empty state handling for new merchants.
"""

from __future__ import annotations

import datetime
from typing import List, Optional
import pandas as pd
from src.api.db import fetch_table_df, get_db_connection

from src.api.config import APIConfig, get_api_config
from src.api.schemas import (
    DailySalesForecastItem,
    DemandForecastResponse,
    SKUForecastItem,
    SalesForecastResponse,
)


class ForecastService:
    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or get_api_config()
        self.ml_dir = self.config.data_dir / "ml"

    def get_sales_forecast(self, merchant_id: Optional[str] = None) -> SalesForecastResponse:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")
        if is_explicit_non_demo:
            conn = get_db_connection()
            try:
                recent_sales = conn.execute(
                    """
                    SELECT DATE(created_at) as sale_date, COUNT(*) as orders, COALESCE(SUM(total_amount), 0.0) as revenue
                    FROM sales
                    WHERE business_id = ? AND status != 'CANCELLED'
                    GROUP BY DATE(created_at)
                    ORDER BY DATE(created_at) DESC
                    LIMIT 30
                    """,
                    (merchant_id,)
                ).fetchall()
            finally:
                conn.close()

            if not recent_sales:
                return SalesForecastResponse(
                    forecast_7d_total_revenue=0.0,
                    forecast_horizon_days=7,
                    model_name="SalesForecaster_Ridge",
                    daily_forecasts=[],
                    trend_direction="STABLE",
                )

            total_hist_rev = sum(float(r["revenue"]) for r in recent_sales)
            avg_daily_rev = total_hist_rev / max(1, len(recent_sales))

            # Trend direction: compare recent half vs older half
            if len(recent_sales) >= 4:
                half = len(recent_sales) // 2
                recent_half_avg = sum(float(r["revenue"]) for r in recent_sales[:half]) / half
                older_half_avg = sum(float(r["revenue"]) for r in recent_sales[half:]) / (len(recent_sales) - half)
                if recent_half_avg > older_half_avg * 1.05:
                    trend_dir = "UP"
                    trend_mult = 1.05
                elif recent_half_avg < older_half_avg * 0.95:
                    trend_dir = "DOWN"
                    trend_mult = 0.95
                else:
                    trend_dir = "STABLE"
                    trend_mult = 1.0
            else:
                trend_dir = "STABLE"
                trend_mult = 1.0

            today = datetime.date.today()
            daily_forecasts = []
            proj_total = 0.0
            for i in range(1, 8):
                f_date = (today + datetime.timedelta(days=i)).isoformat()
                pred_rev = round(avg_daily_rev * trend_mult, 2)
                proj_total += pred_rev
                daily_forecasts.append(
                    DailySalesForecastItem(
                        forecast_date=f_date,
                        predicted_revenue=pred_rev,
                    )
                )

            return SalesForecastResponse(
                forecast_7d_total_revenue=round(proj_total, 2),
                forecast_horizon_days=7,
                model_name="ColdStart_MovingAverage_Heuristic",
                daily_forecasts=daily_forecasts,
                trend_direction=trend_dir,
            )

        tot_rev = 0.0
        model_name = "SalesForecaster_Ridge"
        daily_items: List[DailySalesForecastItem] = []
        trend_dir = "STABLE"

        df_f = fetch_table_df("sales_forecast_7d")
        if not df_f.empty:
            rev_col = "predicted_revenue" if "predicted_revenue" in df_f.columns else "revenue"
            tot_rev = round(float(df_f[rev_col].sum()), 2)
            if "model_name" in df_f.columns:
                model_name = str(df_f["model_name"].iloc[0])

            for _, r in df_f.iterrows():
                daily_items.append(
                    DailySalesForecastItem(
                        forecast_date=str(r.get("forecast_date", r.get("date", ""))),
                        predicted_revenue=round(float(r[rev_col]), 2),
                    )
                )

        df_t = fetch_table_df("business_trend_predictions")
        if not df_t.empty:
            trend_dir = str(df_t["predicted_trend"].iloc[0]).upper()

        return SalesForecastResponse(
            forecast_7d_total_revenue=tot_rev,
            forecast_horizon_days=len(daily_items) or 7,
            model_name=model_name,
            daily_forecasts=daily_items,
            trend_direction=trend_dir,
        )

    def get_demand_forecast(self, limit: int = 30, merchant_id: Optional[str] = None) -> DemandForecastResponse:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")
        if is_explicit_non_demo:
            conn = get_db_connection()
            try:
                demand_rows = conn.execute(
                    """
                    SELECT i.product_id, i.product_name, i.category,
                           COALESCE(SUM(si.quantity), 0) as total_units_sold,
                           COUNT(DISTINCT DATE(s.created_at)) as active_days
                    FROM inventory i
                    LEFT JOIN sale_items si ON si.product_id = i.product_id
                    LEFT JOIN sales s ON si.sale_id = s.id AND s.business_id = ? AND s.status != 'CANCELLED'
                    WHERE i.business_id = ?
                    GROUP BY i.product_id
                    HAVING total_units_sold > 0
                    ORDER BY total_units_sold DESC
                    LIMIT ?
                    """,
                    (merchant_id, merchant_id, limit)
                ).fetchall()
            finally:
                conn.close()

            if not demand_rows:
                return DemandForecastResponse(
                    horizon_days=7,
                    top_demand_skus=[],
                )

            sku_items = []
            for r in demand_rows:
                tot_u = int(r["total_units_sold"])
                active_d = max(1, int(r["active_days"]))
                daily_velocity = tot_u / active_d
                pred_7d_units = max(1, int(round(daily_velocity * 7)))
                sku_items.append(
                    SKUForecastItem(
                        product_id=str(r["product_id"]),
                        product_name=str(r["product_name"]),
                        category=str(r["category"] or "General"),
                        predicted_7d_units=pred_7d_units,
                    )
                )

            return DemandForecastResponse(
                horizon_days=7,
                top_demand_skus=sku_items,
            )

        sku_items: List[SKUForecastItem] = []

        df_d = fetch_table_df("product_demand_forecast_7d")
        if not df_d.empty:
            grouped = df_d.groupby(["product_id", "product_category"]).agg(
                units=("predicted_units", "sum")
            ).reset_index()

            grouped = grouped.sort_values(by="units", ascending=False)
            for _, r in grouped.head(limit).iterrows():
                pid = str(r["product_id"])
                sku_items.append(
                    SKUForecastItem(
                        product_id=pid,
                        product_name=pid,
                        category=str(r["product_category"]),
                        predicted_7d_units=int(round(float(r["units"]))),
                    )
                )

        return DemandForecastResponse(
            horizon_days=7,
            top_demand_skus=sku_items,
        )
