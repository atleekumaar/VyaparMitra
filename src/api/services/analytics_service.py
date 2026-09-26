"""
Analytics Service for VyaparMitra Phase 6 API.
Interfaces with Phase 2 data marts for Sales, Customers, Products, Categories, Payments, Trends, and Anomalies.
"""

from __future__ import annotations

from typing import List
import pandas as pd

from src.api.config import APIConfig, get_api_config
from src.api.schemas import (
    AnomalyItem,
    AnomalyResponse,
    CategoryAnalyticsResponse,
    CategoryShareItem,
    CustomerAnalyticsResponse,
    CustomerSegmentSummary,
    DailySalesPoint,
    PaymentAnalyticsResponse,
    PaymentMethodItem,
    ProductAnalyticsResponse,
    ProductRankItem,
    SalesAnalyticsResponse,
    TrendAnalyticsResponse,
)


class AnalyticsService:
    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or get_api_config()
        self.analytics_dir = self.config.data_dir / "analytics"
        self.ml_dir = self.config.data_dir / "ml"

    def get_sales_analytics(self) -> SalesAnalyticsResponse:
        summary_path = self.analytics_dir / "sales" / "sales_summary.parquet"
        daily_path = self.analytics_dir / "sales" / "sales_daily.parquet"

        tot_rev = 0.0
        tot_orders = 0
        aov = 0.0
        disc = 0.0
        daily_points: List[DailySalesPoint] = []

        if summary_path.exists():
            df_sum = pd.read_parquet(summary_path)
            if not df_sum.empty:
                r = df_sum.iloc[0]
                tot_rev = float(r.get("total_revenue", 0.0))
                tot_orders = int(r.get("total_orders", 0))
                aov = float(r.get("average_order_value", 0.0))
                disc = float(r.get("discount_rate", 0.0))

        if daily_path.exists():
            df_d = pd.read_parquet(daily_path)
            for _, r in df_d.iterrows():
                daily_points.append(
                    DailySalesPoint(
                        date=str(r.get("period_key", r.get("date", ""))),
                        revenue=round(float(r.get("revenue", 0.0)), 2),
                        orders=int(r.get("orders", 0)),
                        units=int(r.get("units", 0)) if "units" in r else None,
                        average_order_value=round(float(r.get("average_order_value", 0.0)), 2) if "average_order_value" in r else None,
                    )
                )

        return SalesAnalyticsResponse(
            total_revenue=tot_rev,
            total_orders=tot_orders,
            average_order_value=aov,
            discount_rate=disc,
            daily_series=daily_points,
        )

    def get_customer_analytics(self) -> CustomerAnalyticsResponse:
        seg_path = self.analytics_dir / "customers" / "customer_segments.parquet"
        risk_path = self.ml_dir / "customer_risk" / "customer_risk_scores.parquet"

        tot_cust = 0
        high_r = 0
        med_r = 0
        low_r = 0
        segments: List[CustomerSegmentSummary] = []

        if seg_path.exists():
            df_s = pd.read_parquet(seg_path)
            tot_cust = len(df_s)
            seg_col = "rfm_segment" if "rfm_segment" in df_s.columns else ("segment" if "segment" in df_s.columns else "customer_type")
            if seg_col in df_s.columns:
                grouped = df_s.groupby(seg_col).agg(
                    count=("customer_id", "count"),
                    revenue=("customer_total_spend", "sum") if "customer_total_spend" in df_s.columns else ("customer_id", "count")
                ).reset_index()
                tot_spend = grouped["revenue"].sum() if grouped["revenue"].sum() > 0 else 1.0
                for _, r in grouped.iterrows():
                    segments.append(
                        CustomerSegmentSummary(
                            segment_name=str(r[seg_col]),
                            customer_count=int(r["count"]),
                            total_revenue=round(float(r["revenue"]), 2),
                            revenue_share=round(float(r["revenue"]) / tot_spend, 4),
                        )
                    )

        if risk_path.exists():
            df_r = pd.read_parquet(risk_path)
            risk_col = "risk_band" if "risk_band" in df_r.columns else "churn_tier"
            if risk_col in df_r.columns:
                bands = df_r[risk_col].astype(str).str.lower()
                high_r = int((bands == "high").sum())
                med_r = int((bands == "medium").sum())
                low_r = int((bands == "low").sum())

        return CustomerAnalyticsResponse(
            total_customers=tot_cust,
            high_risk_count=high_r,
            medium_risk_count=med_r,
            low_risk_count=low_r,
            segments=segments,
        )

    def get_product_analytics(self) -> ProductAnalyticsResponse:
        rank_path = self.analytics_dir / "products" / "product_rankings.parquet"
        pareto_path = self.analytics_dir / "products" / "pareto_analysis.parquet"

        top_products: List[ProductRankItem] = []
        tot_count = 0
        pareto_ratio = 0.80

        if rank_path.exists():
            df_p = pd.read_parquet(rank_path)
            tot_count = len(df_p)
            for idx, r in df_p.head(15).iterrows():
                top_products.append(
                    ProductRankItem(
                        product_id=str(r.get("product_id", "")),
                        product_name=str(r.get("product_name", r.get("product_id", ""))),
                        category=str(r.get("product_category", "General")),
                        revenue=round(float(r.get("revenue", 0.0)), 2),
                        units=int(r.get("units", 0)),
                        rank=int(r.get("revenue_rank", idx + 1)),
                    )
                )

        if pareto_path.exists():
            df_par = pd.read_parquet(pareto_path)
            if not df_par.empty and "pareto_share" in df_par.columns:
                pareto_ratio = float(df_par["pareto_share"].iloc[0])

        return ProductAnalyticsResponse(
            total_products_tracked=tot_count,
            top_performers=top_products,
            pareto_80_20_ratio=pareto_ratio,
        )

    def get_category_analytics(self) -> CategoryAnalyticsResponse:
        cat_path = self.analytics_dir / "categories" / "category_summary.parquet"
        categories: List[CategoryShareItem] = []

        if cat_path.exists():
            df_c = pd.read_parquet(cat_path)
            for _, r in df_c.iterrows():
                categories.append(
                    CategoryShareItem(
                        category=str(r.get("product_category", r.get("category", "General"))),
                        revenue=round(float(r.get("revenue", 0.0)), 2),
                        orders=int(r.get("orders", 0)),
                        revenue_share=round(float(r.get("revenue_share", 0.0)), 4),
                    )
                )

        return CategoryAnalyticsResponse(categories=categories)

    def get_payment_analytics(self) -> PaymentAnalyticsResponse:
        pay_path = self.analytics_dir / "payments" / "payment_summary.parquet"
        methods: List[PaymentMethodItem] = []
        primary_method = "UPI"

        if pay_path.exists():
            df_pay = pd.read_parquet(pay_path)
            if not df_pay.empty:
                primary_method = str(df_pay.sort_values(by="revenue_share", ascending=False).iloc[0].get("payment_method", "UPI"))
                for _, r in df_pay.iterrows():
                    methods.append(
                        PaymentMethodItem(
                            payment_method=str(r.get("payment_method", "")),
                            transaction_count=int(r.get("orders", r.get("transaction_count", 0))),
                            total_revenue=round(float(r.get("revenue", 0.0)), 2),
                            revenue_share=round(float(r.get("revenue_share", 0.0)), 4),
                        )
                    )

        return PaymentAnalyticsResponse(
            payment_methods=methods,
            primary_payment_method=primary_method,
        )

    def get_trend_analytics(self) -> TrendAnalyticsResponse:
        pred_path = self.ml_dir / "trends" / "business_trend_predictions.parquet"
        hist_path = self.analytics_dir / "trends" / "trend_analysis.parquet"

        pred_trend = "STABLE"
        conf = 0.50
        horizon = 7
        hist_change = 0.0

        if pred_path.exists():
            df_p = pd.read_parquet(pred_path)
            if not df_p.empty:
                pred_trend = str(df_p["predicted_trend"].iloc[0]).upper()
                conf = round(float(df_p["confidence"].iloc[0]), 2)
                horizon = int(df_p["horizon_days"].iloc[0])

        if hist_path.exists():
            df_h = pd.read_parquet(hist_path)
            rev_pts = df_h[df_h["metric"] == "revenue"] if "metric" in df_h.columns else df_h
            if not rev_pts.empty:
                hist_change = round(float(rev_pts.iloc[-1].get("percentage_change", 0.0)), 2)

        return TrendAnalyticsResponse(
            predicted_trend=pred_trend,
            confidence=conf,
            horizon_days=horizon,
            historical_revenue_change_pct=hist_change,
        )

    def get_anomaly_analytics(self) -> AnomalyResponse:
        anom_path = self.analytics_dir / "trends" / "anomalies.parquet"
        items: List[AnomalyItem] = []

        if anom_path.exists():
            df_a = pd.read_parquet(anom_path)
            for _, r in df_a.iterrows():
                items.append(
                    AnomalyItem(
                        date=str(r.get("date", r.get("period", ""))),
                        metric=str(r.get("metric", "revenue")),
                        observed_value=round(float(r.get("observed_value", r.get("value", 0.0))), 2),
                        expected_value=round(float(r.get("expected_value", r.get("rolling_mean", 0.0))), 2),
                        deviation_score=round(float(r.get("deviation_score", r.get("z_score", 0.0))), 2),
                        is_anomaly=bool(r.get("is_anomaly", True)),
                    )
                )

        return AnomalyResponse(
            total_anomalies_detected=len(items),
            anomalies=items,
        )
