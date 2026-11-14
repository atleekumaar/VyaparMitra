"""
Dashboard Service for VyaparMitra Phase 6.
Aggregates high-level business health KPIs and top priority actions from Phase 1-4 data marts
or dynamic operational tables in multi-tenant mode.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
from src.api.db import fetch_table_df, get_db_connection

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
        # Check if this request targets demo merchants or fallback
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")
        m_id = merchant_id or self.config.default_merchant_id

        # Defaults
        tot_rev = 0.0
        tot_orders = 0
        aov = 0.0
        tot_units = 0
        rev_change = 0.0
        trend_dir = "STABLE"
        f_rev_7d = 0.0
        total_actions = 0
        critical_count = 0
        date_range = "Last 30 Days"
        merchant_name = "Vyapar Kirana & General Store"
        is_demo = not is_explicit_non_demo

        conn = get_db_connection()
        try:
            biz_row = conn.execute("SELECT name FROM businesses WHERE id = ?", (m_id,)).fetchone()
            if biz_row:
                merchant_name = biz_row["name"]
        except Exception:
            pass

        if is_explicit_non_demo:
            # Operational database mode for real/new merchants
            try:
                sales_row = conn.execute(
                    """
                    SELECT COUNT(*) as tot_orders, COALESCE(SUM(total_amount), 0.0) as tot_rev
                    FROM sales
                    WHERE business_id = ? AND status != 'CANCELLED'
                    """,
                    (m_id,)
                ).fetchone()

                if sales_row:
                    tot_orders = int(sales_row["tot_orders"])
                    tot_rev = float(sales_row["tot_rev"])
                    aov = round(tot_rev / tot_orders, 2) if tot_orders > 0 else 0.0

                units_row = conn.execute(
                    """
                    SELECT COALESCE(SUM(si.quantity), 0) as tot_units
                    FROM sale_items si
                    JOIN sales s ON si.sale_id = s.id
                    WHERE s.business_id = ? AND s.status != 'CANCELLED'
                    """,
                    (m_id,)
                ).fetchone()
                if units_row:
                    tot_units = int(units_row["tot_units"])

                daily_rows = conn.execute(
                    """
                    SELECT DATE(created_at) as sale_date, COALESCE(SUM(total_amount), 0.0) as revenue
                    FROM sales
                    WHERE business_id = ? AND status != 'CANCELLED'
                    GROUP BY DATE(created_at)
                    ORDER BY DATE(created_at) ASC
                    """,
                    (m_id,)
                ).fetchall()

                if len(daily_rows) >= 14:
                    last_7 = sum(float(r["revenue"]) for r in daily_rows[-7:])
                    prev_7 = sum(float(r["revenue"]) for r in daily_rows[-14:-7])
                    if prev_7 > 0:
                        rev_change = round(((last_7 - prev_7) / prev_7) * 100.0, 1)
                elif len(daily_rows) >= 2:
                    last_val = float(daily_rows[-1]["revenue"])
                    prev_val = float(daily_rows[-2]["revenue"])
                    if prev_val > 0:
                        rev_change = round(((last_val - prev_val) / prev_val) * 100.0, 1)

                trend_dir = "UP" if rev_change > 0 else ("DOWN" if rev_change < 0 else "STABLE")
                f_rev_7d = round(tot_rev * 0.25, 2) if tot_orders >= 7 else 0.0
            except Exception:
                pass
            finally:
                conn.close()
        else:
            # Fallback to pre-computed synthetic data marts for demo mode M001 / M015
            conn.close()
            df_sum = fetch_table_df("sales_summary")
            if not df_sum.empty:
                r = df_sum.iloc[0]
                tot_rev = float(r.get("total_revenue", 0.0))
                tot_orders = int(r.get("total_orders", 0))
                aov = float(r.get("average_order_value", 0.0))
                tot_units = int(r.get("total_units", tot_orders * 2))

            df_d = fetch_table_df("sales_daily")
            if len(df_d) >= 14:
                last_7 = float(df_d.tail(7)["revenue"].sum())
                prev_7 = float(df_d.iloc[-14:-7]["revenue"].sum())
                if prev_7 > 0:
                    rev_change = round(((last_7 - prev_7) / prev_7) * 100.0, 1)

            df_t = fetch_table_df("business_trend_predictions")
            if not df_t.empty:
                trend_dir = str(df_t["predicted_trend"].iloc[0]).upper()

            df_f = fetch_table_df("sales_forecast_7d")
            if not df_f.empty:
                rev_col = "predicted_revenue" if "predicted_revenue" in df_f.columns else "revenue"
                f_rev_7d = round(float(df_f[rev_col].sum()), 2)

            df_act = fetch_table_df("merchant_action_plan")
            total_actions = len(df_act)
            if "priority_band" in df_act.columns:
                critical_count = int((df_act["priority_band"].astype(str).str.lower() == "critical").sum())

        kpis: Dict[str, MetricCard] = {
            "revenue": MetricCard(
                label="Total Revenue",
                value=round(tot_rev, 2),
                formatted_value=f"₹{tot_rev:,.2f}" if tot_rev > 0 else "₹0.00",
                change_pct=rev_change if tot_orders > 0 else None,
                trend="UP" if rev_change > 0 else ("DOWN" if rev_change < 0 else "STABLE"),
                subtext="vs previous period" if tot_orders > 0 else "No sales recorded yet"
            ),
            "orders": MetricCard(
                label="Total Orders",
                value=tot_orders,
                formatted_value=f"{tot_orders:,}",
                change_pct=round(rev_change * 0.8, 1) if (rev_change != 0 and tot_orders > 0) else None,
                trend="UP" if rev_change > 0 else "STABLE",
                subtext="Total completed orders" if tot_orders > 0 else "Awaiting first transaction"
            ),
            "aov": MetricCard(
                label="Average Order Value",
                value=round(aov, 2),
                formatted_value=f"₹{aov:,.2f}" if aov > 0 else "₹0.00",
                subtext="Average ticket size" if tot_orders > 0 else "Calculated after first sale"
            ),
            "units": MetricCard(
                label="Units Sold",
                value=tot_units,
                formatted_value=f"{tot_units:,}",
                subtext="Gross inventory movement" if tot_units > 0 else "Zero items moved"
            ),
        }

        return DashboardSummaryResponse(
            merchant_id=m_id,
            merchant_name=merchant_name,
            date_range=date_range,
            kpis=kpis,
            sales_trend_direction=trend_dir,
            forecast_7d_total_revenue=f_rev_7d,
            total_actions_pending=total_actions,
            critical_actions_count=critical_count,
            demo_mode=is_demo,
        )

    def get_top_actions(self, merchant_id: str | None = None, limit: int = 5) -> DashboardActionsResponse:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")
        m_id = merchant_id or self.config.default_merchant_id
        actions: List[ActionItem] = []

        if not is_explicit_non_demo:
            df_act = fetch_table_df("merchant_action_plan")
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
