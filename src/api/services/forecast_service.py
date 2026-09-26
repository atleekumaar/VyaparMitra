"""
Forecast Service for VyaparMitra Phase 6 API.
Serves 7-day predictive sales and SKU demand forecasts from Phase 3 ML artifacts.
"""

from __future__ import annotations

from typing import List
import pandas as pd

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

    def get_sales_forecast(self) -> SalesForecastResponse:
        f_path = self.ml_dir / "forecasts" / "sales_forecast_7d.parquet"
        trend_path = self.ml_dir / "trends" / "business_trend_predictions.parquet"

        tot_rev = 0.0
        model_name = "SalesForecaster_Ridge"
        daily_items: List[DailySalesForecastItem] = []
        trend_dir = "STABLE"

        if f_path.exists():
            df_f = pd.read_parquet(f_path)
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

        if trend_path.exists():
            df_t = pd.read_parquet(trend_path)
            if not df_t.empty:
                trend_dir = str(df_t["predicted_trend"].iloc[0]).upper()

        return SalesForecastResponse(
            forecast_7d_total_revenue=tot_rev,
            forecast_horizon_days=len(daily_items) or 7,
            model_name=model_name,
            daily_forecasts=daily_items,
            trend_direction=trend_dir,
        )

    def get_demand_forecast(self, limit: int = 30) -> DemandForecastResponse:
        d_path = self.ml_dir / "forecasts" / "product_demand_forecast_7d.parquet"
        sku_items: List[SKUForecastItem] = []

        if d_path.exists():
            df_d = pd.read_parquet(d_path)
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
                            product_name=str(r.get("product_name", pid)),
                            category=str(r["product_category"]),
                            predicted_7d_units=int(round(float(r["units"]))),
                        )
                    )

        return DemandForecastResponse(
            horizon_days=7,
            top_demand_skus=sku_items,
        )
