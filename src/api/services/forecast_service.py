"""
Forecast Service for VyaparMitra Phase 6 API.
Serves 7-day predictive sales and SKU demand forecasts from Phase 3 ML artifacts,
with graceful empty state handling for new merchants.
"""

from __future__ import annotations

from typing import List, Optional
import pandas as pd
from src.api.db import fetch_table_df

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
            return SalesForecastResponse(
                forecast_7d_total_revenue=0.0,
                forecast_horizon_days=7,
                model_name="SalesForecaster_Ridge",
                daily_forecasts=[],
                trend_direction="STABLE",
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
            return DemandForecastResponse(
                horizon_days=7,
                top_demand_skus=[],
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
