"""
Controlled Business Query Layer for VyaparMitra Copilot.
Enforces strict multi-tenant isolation:
- Live registered businesses (e.g., BIZ_*) query tenant-scoped SQLite tables directly,
  never falling back to shared static demo Parquet artifacts.
- Legacy demo merchant IDs (M001 / M015 / None) continue to use Phase 1-4 artifacts.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml

from src.copilot.schemas import Fact, SourceReference

logger = logging.getLogger(__name__)

DEMO_MERCHANT_IDS = {"M001", "M015", "DEFAULT_MERCHANT"}


def _is_live_tenant(merchant_id: Optional[str]) -> bool:
    """Returns True when merchant_id belongs to a live tenant rather than static demo fixtures."""
    if not merchant_id:
        return False
    return str(merchant_id).strip().upper() not in DEMO_MERCHANT_IDS


def _get_sqlite_conn():
    """Lazily resolves SQLite DB connection from API layer."""
    from src.api.db import get_db_connection
    return get_db_connection()


class BusinessQueryEngine:
    """Retrieves verified business facts, metrics, and recommendations with tenant isolation."""

    def __init__(
        self,
        config_path: str = "configs/config.yaml",
        data_dir: Optional[str] = None,
    ) -> None:
        self.config_path = config_path
        self.data_dir = Path(data_dir) if data_dir else Path("data")

        self.features_dir = self.data_dir / "features"
        self.analytics_dir = self.data_dir / "analytics"
        self.ml_dir = self.data_dir / "ml"
        self.rec_dir = self.data_dir / "recommendations"

        cfg_file = Path(config_path)
        if cfg_file.exists():
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}
                paths = cfg.get("paths", {})
                if "features" in paths:
                    self.features_dir = Path(paths["features"])
                if "analytics" in paths:
                    self.analytics_dir = Path(paths["analytics"])
                if "ml" in paths:
                    self.ml_dir = Path(paths["ml"])
                if "recommendations" in paths:
                    self.rec_dir = Path(paths["recommendations"])
            except Exception as e:
                logger.warning(f"Error reading config {config_path}: {e}")

    # ------------------------------------------------------------------
    # Live Tenant SQLite Helpers
    # ------------------------------------------------------------------
    def _live_sales_summary(self, business_id: str, time_range: Optional[str] = None) -> Dict[str, Any]:
        metrics: Dict[str, Any] = {
            "total_revenue": 0.0,
            "total_orders": 0,
            "average_order_value": 0.0,
            "discount_rate": 0.0,
            "time_range": time_range or "overall",
            "tenant_id": business_id,
        }
        facts: List[Fact] = []
        sources: List[SourceReference] = [
            SourceReference(
                source="sqlite.sales",
                artifact=f"db://sales?business_id={business_id}",
                description="Tenant-isolated live sales records",
            )
        ]

        conn = _get_sqlite_conn()
        try:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS tot_orders,
                    COALESCE(SUM(total_amount), 0.0) AS tot_rev,
                    COALESCE(AVG(total_amount), 0.0) AS aov,
                    COALESCE(SUM(discount), 0.0) AS tot_disc
                FROM sales
                WHERE business_id = ? AND status != 'CANCELLED'
                """,
                (business_id,),
            ).fetchone()

            tot_orders = int(row["tot_orders"]) if row else 0
            tot_rev = round(float(row["tot_rev"]), 2) if row else 0.0
            aov = round(float(row["aov"]), 2) if (row and tot_orders > 0) else 0.0
            disc_rate = round(float(row["tot_disc"]) / tot_rev, 4) if tot_rev > 0 else 0.0

            metrics["total_revenue"] = tot_rev
            metrics["total_orders"] = tot_orders
            metrics["average_order_value"] = aov
            metrics["discount_rate"] = disc_rate
            if tot_orders == 0:
                metrics["store_status"] = "EMPTY_NO_SALES_YET"

            facts.append(Fact(key="total_revenue", value=tot_rev, source=f"db:sales:{business_id}", category="historical"))
            facts.append(Fact(key="total_orders", value=tot_orders, source=f"db:sales:{business_id}", category="historical"))
            facts.append(Fact(key="average_order_value", value=aov, source=f"db:sales:{business_id}", category="historical"))

            latest = conn.execute(
                """
                SELECT DATE(created_at) AS dt, COUNT(*) AS orders, COALESCE(SUM(total_amount), 0.0) AS rev
                FROM sales
                WHERE business_id = ? AND status != 'CANCELLED'
                GROUP BY DATE(created_at)
                ORDER BY dt DESC
                LIMIT 1
                """,
                (business_id,),
            ).fetchone()
            if latest:
                metrics["latest_date"] = str(latest["dt"])
                metrics["latest_daily_revenue"] = round(float(latest["rev"]), 2)
                metrics["latest_daily_orders"] = int(latest["orders"])
        finally:
            conn.close()

        res = {"metrics": metrics, "facts": facts, "sources": sources}
        res.update(metrics)
        return res

    # 1. Sales Summary
    def get_sales_summary(
        self,
        merchant_id: Optional[str] = None,
        time_range: Optional[str] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            return self._live_sales_summary(str(merchant_id), time_range=time_range)

        path = self.analytics_dir / "sales" / "sales_summary.parquet"
        daily_path = self.analytics_dir / "sales" / "sales_daily.parquet"

        metrics: Dict[str, Any] = {
            "total_revenue": 0.0,
            "total_orders": 0,
            "average_order_value": 0.0,
            "discount_rate": 0.0,
            "time_range": time_range or "overall",
        }
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if path.exists():
            df = pd.read_parquet(path)
            if not df.empty:
                row = df.iloc[0]
                metrics["total_revenue"] = float(row.get("total_revenue", 0.0))
                metrics["total_orders"] = int(row.get("total_orders", 0))
                metrics["average_order_value"] = float(row.get("average_order_value", 0.0))
                metrics["discount_rate"] = float(row.get("discount_rate", 0.0))

                facts.append(Fact(key="total_revenue", value=metrics["total_revenue"], source="analytics/sales_summary.parquet", category="historical"))
                facts.append(Fact(key="total_orders", value=metrics["total_orders"], source="analytics/sales_summary.parquet", category="historical"))
                facts.append(Fact(key="average_order_value", value=metrics["average_order_value"], source="analytics/sales_summary.parquet", category="historical"))
                sources.append(SourceReference(source="phase2.analytics", artifact=str(path), description="Historical sales and revenue metrics summary"))

        if daily_path.exists():
            df_daily = pd.read_parquet(daily_path)
            if not df_daily.empty:
                latest_row = df_daily.iloc[-1]
                metrics["latest_date"] = str(latest_row.get("period_end", latest_row.get("period", "")))
                metrics["latest_daily_revenue"] = float(latest_row.get("revenue", 0.0))
                metrics["latest_daily_orders"] = int(latest_row.get("orders", 0))

                if time_range and "march" in time_range.lower():
                    march_df = df_daily[df_daily["period"].str.startswith("2026-03")]
                    if not march_df.empty:
                        metrics["march_total_revenue"] = float(march_df["revenue"].sum())
                        metrics["march_total_orders"] = int(march_df["orders"].sum())
                        metrics["march_aov"] = round(metrics["march_total_revenue"] / max(1, metrics["march_total_orders"]), 2)

        res = {"metrics": metrics, "facts": facts, "sources": sources}
        res.update(metrics)
        return res

    # 2. Sales Trend & Momentum
    def get_sales_trend(
        self,
        merchant_id: Optional[str] = None,
        time_range: Optional[str] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            biz_id = str(merchant_id)
            conn = _get_sqlite_conn()
            try:
                rows = conn.execute(
                    """
                    SELECT DATE(created_at) AS dt, COUNT(*) AS orders, COALESCE(SUM(total_amount), 0.0) AS rev
                    FROM sales
                    WHERE business_id = ? AND status != 'CANCELLED'
                    GROUP BY DATE(created_at)
                    ORDER BY dt ASC
                    """,
                    (biz_id,),
                ).fetchall()
            finally:
                conn.close()

            tot_rev = round(sum(float(r["rev"]) for r in rows), 2)
            tot_orders = sum(int(r["orders"]) for r in rows)
            days_rec = len(rows)
            direction = "INSUFFICIENT_DATA" if days_rec < 2 else ("GROWING" if float(rows[-1]["rev"]) >= float(rows[0]["rev"]) else "DECLINING")
            metrics = {
                "trend_direction": direction,
                "confidence": 0.85 if days_rec >= 7 else 0.0,
                "total_revenue": tot_rev,
                "total_orders": tot_orders,
                "days_recorded": days_rec,
            }
            facts = [
                Fact(key="total_revenue", value=tot_rev, source=f"db:sales:{biz_id}", category="historical"),
                Fact(key="days_recorded", value=days_rec, source=f"db:sales:{biz_id}", category="historical"),
            ]
            sources = [SourceReference(source="sqlite.sales", artifact=f"db://sales?business_id={biz_id}", description="Tenant-isolated daily sales trend")]
            res = {"metrics": metrics, "facts": facts, "sources": sources}
            res.update(metrics)
            return res

        path = self.ml_dir / "trends" / "business_trend_predictions.parquet"
        hist_trend = self.analytics_dir / "trends" / "trend_analysis.parquet"
        daily_path = self.analytics_dir / "sales" / "sales_daily.parquet"

        metrics: Dict[str, Any] = {
            "trend_direction": "STABLE",
            "confidence": 0.50,
            "total_revenue": 0.0,
            "total_orders": 0,
            "days_recorded": 30,
        }
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if path.exists():
            df = pd.read_parquet(path)
            if not df.empty:
                metrics["trend_direction"] = str(df["predicted_trend"].iloc[0])
                metrics["confidence"] = float(df["confidence"].iloc[0])
                metrics["horizon_days"] = int(df["horizon_days"].iloc[0])
                facts.append(Fact(key="predicted_trend", value=metrics["trend_direction"], source="ml/business_trend_predictions.parquet", category="prediction"))
                sources.append(SourceReference(source="phase3.ml", artifact=str(path), description="ML business trend predictions"))

        if hist_trend.exists():
            ht = pd.read_parquet(hist_trend)
            rev_trends = ht[ht["metric"] == "revenue"]
            if not rev_trends.empty:
                last_pt = rev_trends.iloc[-1]
                metrics["historical_change_pct"] = float(last_pt.get("percentage_change", 0.0))
                facts.append(Fact(key="historical_change_pct", value=metrics["historical_change_pct"], source="analytics/trend_analysis.parquet", category="historical"))
                sources.append(SourceReference(source="phase2.analytics", artifact=str(hist_trend), description="Historical trend analysis"))

        if daily_path.exists():
            df_daily = pd.read_parquet(daily_path)
            if not df_daily.empty:
                metrics["total_revenue"] = float(df_daily["revenue"].sum())
                metrics["total_orders"] = int(df_daily["orders"].sum())
                metrics["days_recorded"] = len(df_daily)

        res = {"metrics": metrics, "facts": facts, "sources": sources}
        res.update(metrics)
        return res

    # 3. Sales Forecast
    def get_sales_forecast(
        self,
        merchant_id: Optional[str] = None,
        horizon: Optional[Any] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            biz_id = str(merchant_id)
            summary = self._live_sales_summary(biz_id)
            tot_orders = summary["total_orders"]
            tot_rev = summary["total_revenue"]
            avg_daily_rev = (tot_rev / 7.0) if tot_orders > 0 else 0.0
            metrics = {
                "forecast_total_revenue": round(avg_daily_rev * 7.0, 2),
                "forecast_total_orders": tot_orders if tot_orders > 0 else 0,
                "forecast_horizon": "7 days",
                "model_name": "TenantLiveRunRate" if tot_orders > 0 else "NoDataYet",
            }
            facts = [
                Fact(key="forecast_7d_total_revenue", value=metrics["forecast_total_revenue"], source=f"db:sales:{biz_id}", category="prediction"),
                Fact(key="forecast_7d_total_orders", value=metrics["forecast_total_orders"], source=f"db:sales:{biz_id}", category="prediction"),
            ]
            sources = [SourceReference(source="sqlite.sales", artifact=f"db://sales?business_id={biz_id}", description="Tenant-isolated 7-day forecast")]
            res = {"metrics": metrics, "facts": facts, "sources": sources}
            res.update(metrics)
            return res

        path = self.ml_dir / "forecasts" / "sales_forecast_7d.parquet"
        metrics: Dict[str, Any] = {
            "forecast_total_revenue": 0.0,
            "forecast_total_orders": 0,
            "forecast_horizon": "7 days",
            "model_name": "SalesForecaster",
        }
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if path.exists():
            df = pd.read_parquet(path)
            if not df.empty:
                rev_col = "predicted_revenue" if "predicted_revenue" in df.columns else "revenue"
                metrics["forecast_total_revenue"] = round(float(df[rev_col].sum()), 2)
                metrics["forecast_total_orders"] = int(df["predicted_orders"].sum()) if "predicted_orders" in df.columns else int(len(df) * 10)
                if "model_name" in df.columns:
                    metrics["model_name"] = str(df["model_name"].iloc[0])

                facts.append(Fact(key="forecast_7d_total_revenue", value=metrics["forecast_total_revenue"], source="ml/sales_forecast_7d.parquet", category="prediction"))
                facts.append(Fact(key="forecast_7d_total_orders", value=metrics["forecast_total_orders"], source="ml/sales_forecast_7d.parquet", category="prediction"))
                sources.append(SourceReference(source="phase3.ml", artifact=str(path), description="7-day sales and revenue forecast"))

        res = {"metrics": metrics, "facts": facts, "sources": sources}
        res.update(metrics)
        return res

    # 4. Product Performance
    def get_product_performance(
        self,
        merchant_id: Optional[str] = None,
        product_id: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            biz_id = str(merchant_id)
            conn = _get_sqlite_conn()
            try:
                rows = conn.execute(
                    """
                    SELECT
                        i.product_id,
                        i.product_name,
                        i.category,
                        i.current_stock,
                        COALESCE(SUM(si.quantity), 0) AS units_sold,
                        COALESCE(SUM(si.line_total), 0.0) AS revenue
                    FROM inventory i
                    LEFT JOIN sale_items si ON i.product_id = si.product_id
                    LEFT JOIN sales s ON si.sale_id = s.id AND s.business_id = ? AND s.status != 'CANCELLED'
                    WHERE i.business_id = ?
                    GROUP BY i.product_id, i.product_name, i.category, i.current_stock
                    ORDER BY revenue DESC, units_sold DESC
                    """,
                    (biz_id, biz_id),
                ).fetchall()
            finally:
                conn.close()

            metrics: Dict[str, Any] = {
                "product_id": product_id or "None",
                "product_name": "No products in inventory yet",
                "product_revenue": 0.0,
                "product_units_sold": 0,
                "total_skus": len(rows),
            }
            facts: List[Fact] = [
                Fact(key="total_skus", value=len(rows), source=f"db:inventory:{biz_id}", category="historical")
            ]
            sources = [SourceReference(source="sqlite.inventory", artifact=f"db://inventory?business_id={biz_id}", description="Tenant-isolated product performance")]

            if rows:
                selected = rows[0]
                if product_id:
                    for r in rows:
                        if product_id.lower() in str(r["product_id"]).lower() or product_id.lower() in str(r["product_name"]).lower():
                            selected = r
                            break
                metrics["product_id"] = str(selected["product_id"])
                metrics["product_name"] = str(selected["product_name"])
                metrics["product_revenue"] = round(float(selected["revenue"]), 2)
                metrics["product_units_sold"] = int(selected["units_sold"])
                facts.append(Fact(key=f"{metrics['product_id']}_revenue", value=metrics["product_revenue"], source=f"db:inventory:{biz_id}", category="historical"))
                facts.append(Fact(key=f"{metrics['product_id']}_units", value=metrics["product_units_sold"], source=f"db:inventory:{biz_id}", category="historical"))

            res = {"metrics": metrics, "facts": facts, "sources": sources}
            res.update(metrics)
            return res

        rank_path = self.analytics_dir / "products" / "product_rankings.parquet"
        metrics: Dict[str, Any] = {
            "product_id": product_id or "All Products",
            "product_revenue": 0.0,
            "product_units_sold": 0,
        }
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if rank_path.exists():
            df = pd.read_parquet(rank_path)
            if product_id and not df.empty:
                matched = df[df["product_id"].str.contains(product_id, case=False, na=False)]
                if not matched.empty:
                    p = matched.iloc[0]
                    metrics["product_id"] = str(p.get("product_id"))
                    metrics["product_name"] = str(p.get("product_name", p.get("product_id")))
                    metrics["product_revenue"] = float(p.get("revenue", 0.0))
                    metrics["product_units_sold"] = int(p.get("units", 0))
                    facts.append(Fact(key=f"{metrics['product_id']}_revenue", value=metrics["product_revenue"], source="analytics/product_rankings.parquet", category="historical"))
                    facts.append(Fact(key=f"{metrics['product_id']}_units", value=metrics["product_units_sold"], source="analytics/product_rankings.parquet", category="historical"))
            elif not df.empty:
                top = df.iloc[0]
                metrics["product_id"] = str(top.get("product_id"))
                metrics["product_name"] = str(top.get("product_name", top.get("product_id")))
                metrics["product_revenue"] = float(top.get("revenue", 0.0))
                metrics["product_units_sold"] = int(top.get("units", 0))

            sources.append(SourceReference(source="phase2.analytics", artifact=str(rank_path), description="Product ranking and revenue metrics"))

        res = {"metrics": metrics, "facts": facts, "sources": sources}
        res.update(metrics)
        return res

    # 5. Product Demand Forecast
    def get_product_demand_forecast(
        self,
        merchant_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            biz_id = str(merchant_id)
            perf = self.get_product_performance(merchant_id=biz_id, product_id=product_id)
            forecast_units = int(perf.get("product_units_sold", 0))
            metrics = {
                "product_id": perf.get("product_id", product_id or "None"),
                "forecast_units": forecast_units,
                "horizon": "7 days",
            }
            facts = [Fact(key=f"{metrics['product_id']}_demand_forecast_units", value=forecast_units, source=f"db:inventory:{biz_id}", category="prediction")]
            sources = [SourceReference(source="sqlite.inventory", artifact=f"db://inventory?business_id={biz_id}", description="Tenant-isolated SKU demand projection")]
            res = {"metrics": metrics, "facts": facts, "sources": sources}
            res.update(metrics)
            return res

        path = self.ml_dir / "forecasts" / "product_demand_forecast_7d.parquet"
        metrics: Dict[str, Any] = {
            "product_id": product_id or "SKU",
            "forecast_units": 0,
            "horizon": "7 days",
        }
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if path.exists():
            df = pd.read_parquet(path)
            if not df.empty:
                if product_id:
                    matched = df[df["product_id"].str.contains(product_id, case=False, na=False)]
                    if not matched.empty:
                        metrics["forecast_units"] = int(matched["predicted_units"].sum())
                        metrics["product_id"] = str(matched["product_id"].iloc[0])
                    else:
                        metrics["forecast_units"] = int(df["predicted_units"].head(7).sum())
                else:
                    metrics["forecast_units"] = int(df["predicted_units"].sum())

                facts.append(Fact(key=f"{metrics['product_id']}_demand_forecast_units", value=metrics["forecast_units"], source="ml/product_demand_forecast_7d.parquet", category="prediction"))
                sources.append(SourceReference(source="phase3.ml", artifact=str(path), description="SKU-level 7-day demand projections"))

        res = {"metrics": metrics, "facts": facts, "sources": sources}
        res.update(metrics)
        return res

    # 6. Customer Risk
    def get_customer_risk(
        self,
        merchant_id: Optional[str] = None,
        customer_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            biz_id = str(merchant_id)
            conn = _get_sqlite_conn()
            try:
                rows = conn.execute(
                    "SELECT id, name, current_balance, credit_limit FROM customers WHERE business_id = ?",
                    (biz_id,),
                ).fetchall()
            finally:
                conn.close()

            high_risk = sum(
                1 for r in rows
                if float(r["credit_limit"] or 0) > 0 and float(r["current_balance"] or 0) >= 0.8 * float(r["credit_limit"])
            )
            metrics = {
                "total_customers_evaluated": len(rows),
                "high_risk_customers_count": high_risk,
                "customer_id": customer_id,
                "churn_tier": "High" if high_risk > 0 else "None",
                "churn_probability": 0.0,
            }
            facts = [
                Fact(key="total_customers", value=len(rows), source=f"db:customers:{biz_id}", category="historical"),
                Fact(key="high_risk_customer_count", value=high_risk, source=f"db:customers:{biz_id}", category="prediction"),
            ]
            sources = [SourceReference(source="sqlite.customers", artifact=f"db://customers?business_id={biz_id}", description="Tenant-isolated customer ledger risk")]
            res = {"metrics": metrics, "facts": facts, "sources": sources}
            res.update(metrics)
            return res

        path = self.ml_dir / "customer_risk" / "customer_risk_scores.parquet"
        metrics: Dict[str, Any] = {
            "total_customers_evaluated": 0,
            "high_risk_customers_count": 0,
            "customer_id": customer_id,
            "churn_tier": "Low",
            "churn_probability": 0.15,
        }
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if path.exists():
            df = pd.read_parquet(path)
            metrics["total_customers_evaluated"] = len(df)
            risk_col = "risk_band" if "risk_band" in df.columns else "churn_tier"
            if risk_col in df.columns:
                metrics["high_risk_customers_count"] = int((df[risk_col].astype(str).str.lower() == "high").sum())

            if customer_id and not df.empty:
                matched = df[df["customer_id"].str.contains(customer_id, case=False, na=False)]
                if not matched.empty:
                    c_row = matched.iloc[0]
                    metrics["customer_id"] = str(c_row.get("customer_id"))
                    metrics["churn_tier"] = str(c_row.get(risk_col, "Medium"))
                    score_col = "risk_probability" if "risk_probability" in df.columns else "churn_probability"
                    metrics["churn_probability"] = float(c_row.get(score_col, 0.5))

            facts.append(Fact(key="high_risk_customer_count", value=metrics["high_risk_customers_count"], source="ml/customer_risk_scores.parquet", category="prediction"))
            sources.append(SourceReference(source="phase3.ml", artifact=str(path), description="Customer churn risk evaluation"))

        res = {"metrics": metrics, "facts": facts, "sources": sources}
        res.update(metrics)
        return res

    # 7. Inventory Recommendations
    def get_inventory_recommendations(
        self,
        merchant_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            biz_id = str(merchant_id)
            conn = _get_sqlite_conn()
            try:
                low_rows = conn.execute(
                    """
                    SELECT product_id, product_name, current_stock, min_stock_threshold, selling_price
                    FROM inventory
                    WHERE business_id = ? AND current_stock <= min_stock_threshold
                    ORDER BY current_stock ASC
                    LIMIT 10
                    """,
                    (biz_id,),
                ).fetchall()
            finally:
                conn.close()

            recommendations: List[Dict[str, Any]] = []
            facts: List[Fact] = []
            for idx, r in enumerate(low_rows, 1):
                deficit = max(10, int(r["min_stock_threshold"] or 10) * 2 - int(r["current_stock"] or 0))
                rec = {
                    "recommendation_id": f"REC_LIVE_{idx:03d}",
                    "type": "INVENTORY",
                    "action": "RESTOCK",
                    "sku": str(r["product_id"]),
                    "product_name": str(r["product_name"]),
                    "suggested_quantity": deficit,
                    "estimated_revenue_impact": round(deficit * float(r["selling_price"] or 0.0), 2),
                }
                recommendations.append(rec)
                facts.append(Fact(key=f"restock_{rec['sku']}", value=deficit, source=f"db:inventory:{biz_id}", category="recommendation"))

            sources = [SourceReference(source="sqlite.inventory", artifact=f"db://inventory?business_id={biz_id}", description="Tenant-isolated live low-stock alerts")]
            return {
                "recommendations": recommendations,
                "evidence": [],
                "facts": facts,
                "sources": sources,
                "metrics": {"total_inventory_recs": len(recommendations)},
            }

        path = self.rec_dir / "inventory_recommendations.parquet"
        ev_path = self.rec_dir / "recommendation_evidence.parquet"

        recommendations: List[Dict[str, Any]] = []
        evidence: List[Dict[str, Any]] = []
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if path.exists():
            df = pd.read_parquet(path)
            if product_id and not df.empty:
                matched = df[df["entity_id"].str.contains(product_id, case=False, na=False)]
                subset = matched if not matched.empty else df.head(3)
            else:
                subset = df.head(3)

            for _, row in subset.iterrows():
                rec_dict = {
                    "recommendation_id": str(row.get("recommendation_id", "")),
                    "type": "INVENTORY",
                    "action": str(row.get("action_type", row.get("action", "RESTOCK"))),
                    "sku": str(row.get("entity_id", "")),
                    "suggested_quantity": int(row.get("suggested_quantity", 10)),
                    "estimated_revenue_impact": float(row.get("expected_impact", row.get("impact_score", 1500.0))),
                }
                recommendations.append(rec_dict)
                facts.append(Fact(key=f"restock_{rec_dict['sku']}", value=rec_dict["suggested_quantity"], source="recommendations/inventory_recommendations.parquet", category="recommendation"))

            sources.append(SourceReference(source="phase4.recommendations", artifact=str(path), description="Inventory restock suggestions"))

        if ev_path.exists():
            df_ev = pd.read_parquet(ev_path)
            if not df_ev.empty:
                evidence = df_ev.head(3).to_dict(orient="records")

        return {
            "recommendations": recommendations,
            "evidence": evidence,
            "facts": facts,
            "sources": sources,
            "metrics": {"total_inventory_recs": len(recommendations)},
        }

    # 8. Cross-Sell Recommendations
    def get_cross_sell_recommendations(
        self,
        merchant_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            return {
                "recommendations": [],
                "facts": [],
                "sources": [SourceReference(source="sqlite.sales", artifact=f"db://sales?business_id={merchant_id}", description="Tenant-isolated affinity analysis")],
                "metrics": {"total_cross_sell_recs": 0},
            }

        path = self.rec_dir / "cross_sell_recommendations.parquet"
        recommendations: List[Dict[str, Any]] = []
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if path.exists():
            df = pd.read_parquet(path)
            if not df.empty:
                subset = df.head(3)
                for _, row in subset.iterrows():
                    rec_dict = {
                        "recommendation_id": str(row.get("recommendation_id", "")),
                        "type": "CROSS_SELL",
                        "target_sku": str(row.get("entity_id", row.get("base_product", "PRD_001"))),
                        "recommended_sku": str(row.get("recommended_entity_id", row.get("cross_product", "PRD_002"))),
                        "confidence": float(row.get("confidence", 0.75)),
                    }
                    recommendations.append(rec_dict)
                    facts.append(Fact(key=f"bundle_{rec_dict['target_sku']}", value=rec_dict["recommended_sku"], source="recommendations/cross_sell_recommendations.parquet", category="recommendation"))

            sources.append(SourceReference(source="phase4.recommendations", artifact=str(path), description="Product bundling and affinity"))

        return {
            "recommendations": recommendations,
            "facts": facts,
            "sources": sources,
            "metrics": {"total_cross_sell_recs": len(recommendations)},
        }

    # 9. Pricing Recommendations
    def get_pricing_recommendations(
        self,
        merchant_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            return {
                "recommendations": [],
                "evidence": [],
                "facts": [],
                "sources": [SourceReference(source="sqlite.inventory", artifact=f"db://inventory?business_id={merchant_id}", description="Tenant-isolated pricing analysis")],
                "metrics": {"total_pricing_recs": 0},
            }

        path = self.rec_dir / "pricing_recommendations.parquet"
        recommendations: List[Dict[str, Any]] = []
        evidence: List[Dict[str, Any]] = []
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if path.exists():
            df = pd.read_parquet(path)
            if not df.empty:
                subset = df.head(3)
                for _, row in subset.iterrows():
                    rec_dict = {
                        "recommendation_id": str(row.get("recommendation_id", "")),
                        "type": "PRICING",
                        "sku": str(row.get("entity_id", "")),
                        "action": str(row.get("action_type", "ADJUST_PRICE")),
                        "current_price": float(row.get("current_price", 100.0)),
                        "recommended_price": float(row.get("recommended_price", 110.0)),
                    }
                    recommendations.append(rec_dict)
                    facts.append(Fact(key=f"price_{rec_dict['sku']}", value=rec_dict["recommended_price"], source="recommendations/pricing_recommendations.parquet", category="recommendation"))

            sources.append(SourceReference(source="phase4.recommendations", artifact=str(path), description="Price elasticity adjustments"))

        return {
            "recommendations": recommendations,
            "evidence": evidence,
            "facts": facts,
            "sources": sources,
            "metrics": {"total_pricing_recs": len(recommendations)},
        }

    # 10. Daily Action Plan
    def get_daily_action_plan(
        self,
        merchant_id: Optional[str] = None,
        limit: int = 5,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            inv = self.get_inventory_recommendations(merchant_id=merchant_id)
            recs = inv["recommendations"][:limit]
            return {
                "recommendations": recs,
                "facts": [Fact(key="daily_actions_count", value=len(recs), source=f"db:inventory:{merchant_id}", category="recommendation")],
                "sources": inv["sources"],
                "metrics": {"pending_action_count": len(recs)},
            }

        path = self.rec_dir / "merchant_action_plan.parquet"
        recommendations: List[Dict[str, Any]] = []
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if path.exists():
            df = pd.read_parquet(path)
            if not df.empty:
                subset = df.head(limit)
                for _, row in subset.iterrows():
                    rec_dict = {
                        "recommendation_id": str(row.get("recommendation_id", "")),
                        "type": str(row.get("type", "ACTION")),
                        "sku": str(row.get("entity_id", "")),
                        "action": str(row.get("title", row.get("action_type", "URGENT ACTION"))),
                        "estimated_revenue_impact": float(row.get("impact_score", 1200.0)),
                    }
                    recommendations.append(rec_dict)

            facts.append(Fact(key="daily_actions_count", value=len(recommendations), source="recommendations/merchant_action_plan.parquet", category="recommendation"))
            sources.append(SourceReference(source="phase4.recommendations", artifact=str(path), description="Top prioritized daily merchant action items"))

        return {
            "recommendations": recommendations,
            "facts": facts,
            "sources": sources,
            "metrics": {"pending_action_count": len(recommendations)},
        }

    # 11. Recommendation Explanation
    def get_recommendation_explanation(
        self,
        merchant_id: Optional[str] = None,
        recommendation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            return {
                "evidence": [],
                "facts": [],
                "sources": [SourceReference(source="sqlite.inventory", artifact=f"db://inventory?business_id={merchant_id}", description="Tenant-isolated recommendation evidence")],
                "metrics": {"evidence_records": 0},
            }

        ev_path = self.rec_dir / "recommendation_evidence.parquet"
        evidence: List[Dict[str, Any]] = []
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        if ev_path.exists():
            df_ev = pd.read_parquet(ev_path)
            if not df_ev.empty:
                if recommendation_id:
                    matched = df_ev[df_ev["recommendation_id"] == recommendation_id]
                    subset = matched if not matched.empty else df_ev.head(2)
                else:
                    subset = df_ev.head(2)

                for _, row in subset.iterrows():
                    ev_dict = {
                        "recommendation_id": str(row.get("recommendation_id", "")),
                        "reasoning": str(row.get("reasoning", row.get("evidence_description", "Data-driven recommendation."))),
                    }
                    evidence.append(ev_dict)

            sources.append(SourceReference(source="phase4.evidence", artifact=str(ev_path), description="Auditable reasoning behind merchant recommendations"))

        return {
            "evidence": evidence,
            "facts": facts,
            "sources": sources,
            "metrics": {"evidence_records": len(evidence)},
        }

    # 12. General Business Summary
    def get_general_business_summary(
        self,
        merchant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        sales = self.get_sales_summary(merchant_id=merchant_id)
        forecast = self.get_sales_forecast(merchant_id=merchant_id)
        plan = self.get_daily_action_plan(merchant_id=merchant_id, limit=3)

        combined_metrics = {}
        combined_metrics.update(sales.get("metrics", {}))
        combined_metrics.update(forecast.get("metrics", {}))

        combined_facts = []
        combined_facts.extend(sales.get("facts", []))
        combined_facts.extend(forecast.get("facts", []))

        combined_sources = []
        combined_sources.extend(sales.get("sources", []))
        combined_sources.extend(forecast.get("sources", []))
        combined_sources.extend(plan.get("sources", []))

        return {
            "metrics": combined_metrics,
            "facts": combined_facts,
            "sources": combined_sources,
            "recommendations": plan.get("recommendations", []),
        }

    # 13. Peer Benchmarks
    def get_benchmark(
        self,
        merchant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if _is_live_tenant(merchant_id):
            return {
                "metrics": {"status": "NOT_ENOUGH_STORE_HISTORY"},
                "facts": [],
                "sources": [SourceReference(source="sqlite.sales", artifact=f"db://sales?business_id={merchant_id}", description="Tenant-isolated store status")],
                "recommendations": [],
            }

        m_id = str(merchant_id or "M001").upper()
        from src.analytics.benchmark import get_benchmark_engine
        engine = get_benchmark_engine()
        b_data = engine.get_benchmark(m_id)
        if not b_data:
            return {"metrics": {}, "facts": [], "sources": []}

        metrics = {
            "rank": b_data["rank"],
            "peer_count": b_data["peer_count"],
            "peer_group": b_data["peer_group"],
            "overall_score": b_data["overall_score"],
        }
        for m in b_data.get("metrics", []):
            metrics[f"{m['name']}_you"] = m["you"]
            metrics[f"{m['name']}_median"] = m["peer_median"]
            metrics[f"{m['name']}_status"] = m["status"]
            metrics[f"{m['name']}_percentile"] = m["percentile"]

        facts = [
            Fact(key="rank", value=b_data["rank"], source="benchmarks.json", category="historical"),
            Fact(key="overall_score", value=b_data["overall_score"], source="benchmarks.json", category="historical"),
            Fact(key="peer_count", value=b_data["peer_count"], source="benchmarks.json", category="historical"),
            Fact(key="peer_group", value=b_data["peer_group"], source="benchmarks.json", category="historical"),
        ]
        for m in b_data.get("metrics", []):
            facts.append(Fact(key=m["name"], value=m["you"], source="benchmarks.json", category="historical"))

        sources = [
            SourceReference(
                source="benchmarks.json",
                artifact="data/analytics/merchants/benchmarks.json",
                description=f"Peer benchmark scorecard for {b_data['peer_group']}",
            )
        ]

        recommendations = [
            {
                "recommendation_id": f"REC_BENCHMARK_{idx}",
                "title": m["label"],
                "action": m["action"],
                "status": m["status"],
            }
            for idx, m in enumerate(b_data.get("metrics", []))
            if m.get("status") in ("red", "yellow")
        ]

        return {
            "metrics": metrics,
            "facts": facts,
            "sources": sources,
            "recommendations": recommendations,
        }
