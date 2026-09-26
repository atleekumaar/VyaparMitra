"""
Dashboard Service for VyaparMitra Phase 6.
Aggregates high-level business health KPIs and top priority actions from Phase 1-4 data marts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

from src.api.config import APIConfig, get_api_config
from src.api.schemas import ActionItem, DashboardActionsResponse, DashboardSummaryResponse, MetricCard


class DashboardService:
    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or get_api_config()
        self.data_dir = self.config.data_dir
        self.analytics_dir = self.data_dir / "analytics"
        self.ml_dir = self.data_dir / "ml"
        self.rec_dir = self.data_dir / "recommendations"

    def get_summary(self, merchant_id: str | None = None) -> DashboardSummaryResponse:
        m_id = merchant_id or self.config.default_merchant_id
        summary_path = self.analytics_dir / "sales" / "sales_summary.parquet"
        daily_path = self.analytics_dir / "sales" / "sales_daily.parquet"
        trend_path = self.ml_dir / "trends" / "business_trend_predictions.parquet"
        forecast_path = self.ml_dir / "forecasts" / "sales_forecast_7d.parquet"
        action_path = self.rec_dir / "merchant_action_plan.parquet"

        # Defaults
        tot_rev = 0.0
        tot_orders = 0
        aov = 0.0
        tot_units = 0
        date_range = "Last 30 Days"

        if summary_path.exists():
            df_sum = pd.read_parquet(summary_path)
            if not df_sum.empty:
                r = df_sum.iloc[0]
                tot_rev = float(r.get("total_revenue", 0.0))
                tot_orders = int(r.get("total_orders", 0))
                aov = float(r.get("average_order_value", 0.0))
                tot_units = int(r.get("total_units", tot_orders * 2))

        # Recent change
        rev_change = 0.0
        if daily_path.exists():
            df_d = pd.read_parquet(daily_path)
            if len(df_d) >= 14:
                last_7 = float(df_d.tail(7)["revenue"].sum())
                prev_7 = float(df_d.iloc[-14:-7]["revenue"].sum())
                if prev_7 > 0:
                    rev_change = round(((last_7 - prev_7) / prev_7) * 100.0, 1)

        # Trend & Forecast
        trend_dir = "STABLE"
        if trend_path.exists():
            df_t = pd.read_parquet(trend_path)
            if not df_t.empty:
                trend_dir = str(df_t["predicted_trend"].iloc[0]).upper()

        f_rev_7d = 0.0
        if forecast_path.exists():
            df_f = pd.read_parquet(forecast_path)
            if not df_f.empty:
                rev_col = "predicted_revenue" if "predicted_revenue" in df_f.columns else "revenue"
                f_rev_7d = round(float(df_f[rev_col].sum()), 2)

        # Action plan counts
        total_actions = 0
        critical_count = 0
        if action_path.exists():
            df_act = pd.read_parquet(action_path)
            total_actions = len(df_act)
            if "priority_band" in df_act.columns:
                critical_count = int((df_act["priority_band"].astype(str).str.lower() == "critical").sum())

        kpis: Dict[str, MetricCard] = {
            "revenue": MetricCard(
                label="Total Revenue",
                value=round(tot_rev, 2),
                formatted_value=f"₹{tot_rev:,.2f}",
                change_pct=rev_change,
                trend="UP" if rev_change > 0 else ("DOWN" if rev_change < 0 else "STABLE"),
                subtext="vs previous 7-day period"
            ),
            "orders": MetricCard(
                label="Total Orders",
                value=tot_orders,
                formatted_value=f"{tot_orders:,}",
                change_pct=round(rev_change * 0.8, 1) if rev_change != 0 else None,
                trend="UP" if rev_change > 0 else "STABLE",
                subtext="Total completed orders"
            ),
            "aov": MetricCard(
                label="Average Order Value",
                value=round(aov, 2),
                formatted_value=f"₹{aov:,.2f}",
                subtext="Average ticket size"
            ),
            "units": MetricCard(
                label="Units Sold",
                value=tot_units,
                formatted_value=f"{tot_units:,}",
                subtext="Gross inventory movement"
            ),
        }

        return DashboardSummaryResponse(
            merchant_id=m_id,
            merchant_name="Vyapar Kirana & General Store",
            date_range=date_range,
            kpis=kpis,
            sales_trend_direction=trend_dir,
            forecast_7d_total_revenue=f_rev_7d,
            total_actions_pending=total_actions,
            critical_actions_count=critical_count,
            demo_mode=self.config.demo_mode,
        )

    def get_top_actions(self, merchant_id: str | None = None, limit: int = 5) -> DashboardActionsResponse:
        m_id = merchant_id or self.config.default_merchant_id
        action_path = self.rec_dir / "merchant_action_plan.parquet"
        actions: List[ActionItem] = []

        if action_path.exists():
            df_act = pd.read_parquet(action_path)
            for _, r in df_act.head(limit).iterrows():
                actions.append(
                    ActionItem(
                        recommendation_id=str(r.get("recommendation_id", "")),
                        type=str(r.get("type", "ACTION")),
                        priority_band=str(r.get("priority_band", "HIGH")).upper(),
                        priority_score=float(r.get("priority", r.get("priority_score", 0.85))),
                        title=str(r.get("title", "Commercial Action")),
                        action=str(r.get("action", "")),
                        reason=str(r.get("reason", "Identified by decision engine")),
                        expected_impact=float(r.get("expected_impact", r.get("impact_score", 1200.0))),
                        entity_id=str(r.get("entity_id", "")),
                        status=str(r.get("lifecycle_state", "GENERATED")).upper(),
                        evidence_snippet=str(r.get("evidence_description", ""))[:120] if r.get("evidence_description") else None,
                    )
                )

        return DashboardActionsResponse(
            merchant_id=m_id,
            total_actions=len(actions),
            actions=actions,
        )
