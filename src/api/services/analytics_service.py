"""
Analytics Service for VyaparMitra Phase 6 API.
Interfaces with Phase 2 data marts for Sales, Customers, Products, Categories, Payments, Trends, and Anomalies.
"""

from __future__ import annotations

from typing import List
import pandas as pd
from src.api.db import fetch_table_df

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

        if True:
            df_sum = fetch_table_df("sales_summary")
            if not df_sum.empty:
                r = df_sum.iloc[0]
                tot_rev = float(r.get("total_revenue", 0.0))
                tot_orders = int(r.get("total_orders", 0))
                aov = float(r.get("average_order_value", 0.0))
                disc = float(r.get("discount_rate", 0.0))

        if True:
            df_d = fetch_table_df("sales_daily")
            for _, r in df_d.iterrows():
                daily_points.append(
                    DailySalesPoint(
                        date=str(r.get("period_key", r.get("period_start", r.get("date", r.get("period", ""))))),
                        revenue=round(float(r.get("revenue", 0.0)), 2),
                        orders=int(r.get("orders", 0)),
                        units=int(r.get("units", 0)) if "units" in r and pd.notna(r.get("units")) else None,
                        average_order_value=round(float(r.get("average_order_value", r.get("aov", 0.0))), 2) if ("average_order_value" in r or "aov" in r) else None,
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

        if True:
            df_s = fetch_table_df("customer_segments")
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

        if True:
            df_r = fetch_table_df("customer_risk_scores")
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

        if True:
            df_p = fetch_table_df("product_rankings")
            tot_count = len(df_p)
            for idx, r in df_p.head(15).iterrows():
                top_products.append(
                    ProductRankItem(
                        product_id=str(r.get("product_id", "")),
                        product_name=str(r.get("product_name", r.get("product_id", ""))),
                        category=str(r.get("product_category", "General")),
                        revenue=round(float(r.get("revenue", 0.0)), 2),
                        units=int(r.get("units", 0)),
                        rank=int(r.get("rank_by_revenue", r.get("revenue_rank", idx + 1))),
                    )
                )

        if True:
            df_par = fetch_table_df("pareto_analysis")
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

        if True:
            df_c = fetch_table_df("category_summary")
            for _, r in df_c.iterrows():
                categories.append(
                    CategoryShareItem(
                        category=str(r.get("product_category", r.get("category", "General"))),
                        revenue=round(float(r.get("category_revenue", r.get("revenue", 0.0))), 2),
                        orders=int(r.get("category_orders", r.get("orders", 0))),
                        revenue_share=round(float(r.get("revenue_share", 0.0)), 4),
                    )
                )

        return CategoryAnalyticsResponse(categories=categories)

    def get_payment_analytics(self) -> PaymentAnalyticsResponse:
        pay_path = self.analytics_dir / "payments" / "payment_summary.parquet"
        if not pay_path.exists():
            pay_path = self.analytics_dir / "payment_summary.parquet"

        methods: List[PaymentMethodItem] = []
        primary_method = "UPI"

        if pay_path.exists():
            try:
                df_pay = pd.read_parquet(pay_path)
            except Exception:
                df_pay = fetch_table_df("payment_summary")
        else:
            df_pay = fetch_table_df("payment_summary")

        if not df_pay.empty:
            sort_col = "revenue_share" if "revenue_share" in df_pay.columns else ("payment_method_revenue" if "payment_method_revenue" in df_pay.columns else "revenue")
            primary_method = str(df_pay.sort_values(by=sort_col, ascending=False).iloc[0].get("payment_method", "UPI"))
            for _, r in df_pay.iterrows():
                methods.append(
                    PaymentMethodItem(
                        payment_method=str(r.get("payment_method", "")),
                        transaction_count=int(r.get("payment_method_orders", r.get("orders", r.get("transaction_count", 0)))),
                        total_revenue=round(float(r.get("payment_method_revenue", r.get("revenue", r.get("total_revenue", 0.0)))), 2),
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

        if True:
            df_p = fetch_table_df("business_trend_predictions")
            if not df_p.empty:
                pred_trend = str(df_p["predicted_trend"].iloc[0]).upper()
                conf = round(float(df_p["confidence"].iloc[0]), 2)
                horizon = int(df_p["horizon_days"].iloc[0])

        if True:
            df_h = fetch_table_df("trend_analysis")
            rev_pts = df_h[df_h["metric"].isin(["revenue", "net_amount"])] if "metric" in df_h.columns else df_h
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
        if not anom_path.exists():
            anom_path = self.analytics_dir / "trends" / "anomaly_analysis.parquet"
        items: List[AnomalyItem] = []

        if True:
            df_a = fetch_table_df("anomalies")
            for _, r in df_a.iterrows():
                is_anom = r.get("is_anomaly")
                if is_anom is None:
                    is_anom = str(r.get("status", "")).lower() in ["unusually_high", "unusually_low", "anomaly"]
                if is_anom:
                    items.append(
                        AnomalyItem(
                            date=str(r.get("date", r.get("period", ""))),
                            metric=str(r.get("metric", "revenue")),
                            observed_value=round(float(r.get("observed_value", r.get("value", 0.0))), 2),
                            expected_value=round(float(r.get("expected_value", r.get("baseline", r.get("rolling_mean", 0.0)))), 2),
                            deviation_score=round(float(r.get("deviation_score", r.get("deviation", r.get("z_score", 0.0)))), 2),
                            is_anomaly=True,
                        )
                    )

        return AnomalyResponse(
            total_anomalies_detected=len(items),
            anomalies=items,
        )

    def record_cash_sale(self, req: Any) -> Any:
        import datetime
        from src.api.schemas import CashSaleResponse
        from src.api.db import save_table_df

        amount = float(req.amount)
        now = datetime.datetime.now()
        txn_id = f"CASH_{int(now.timestamp())}"
        
        updated_cash_rev = 0.0
        updated_cash_orders = 0

        # 1. Update payment_summary parquet tables & SQLite
        pay_paths = [
            self.analytics_dir / "payments" / "payment_summary.parquet",
            self.analytics_dir / "payment_summary.parquet",
        ]
        last_pay_df = None
        for p in pay_paths:
            if p.exists():
                try:
                    df = pd.read_parquet(p)
                    if "payment_method" in df.columns:
                        mask = df["payment_method"].str.upper() == "CASH"
                        if mask.any():
                            df.loc[mask, "payment_method_orders"] = df.loc[mask, "payment_method_orders"].astype(int) + 1
                            df.loc[mask, "payment_method_revenue"] = df.loc[mask, "payment_method_revenue"].astype(float) + amount
                            updated_cash_rev = float(df.loc[mask, "payment_method_revenue"].iloc[0])
                            updated_cash_orders = int(df.loc[mask, "payment_method_orders"].iloc[0])
                        else:
                            new_row = pd.DataFrame([{
                                "payment_method": "CASH",
                                "payment_method_orders": 1,
                                "payment_method_revenue": amount,
                                "orders_share": 0.05,
                                "revenue_share": 0.05,
                                "payment_method_aov": amount,
                            }])
                            df = pd.concat([df, new_row], ignore_index=True)
                            updated_cash_rev = amount
                            updated_cash_orders = 1

                        # Recalculate shares & AOV
                        tot_rev = df["payment_method_revenue"].sum()
                        tot_ord = df["payment_method_orders"].sum()
                        if tot_rev > 0:
                            df["revenue_share"] = (df["payment_method_revenue"] / tot_rev).round(4)
                        if tot_ord > 0:
                            df["orders_share"] = (df["payment_method_orders"] / tot_ord).round(4)
                        if "payment_method_aov" in df.columns:
                            df["payment_method_aov"] = (df["payment_method_revenue"] / df["payment_method_orders"]).round(2)

                        df.to_parquet(p, index=False)
                        last_pay_df = df
                except Exception as e:
                    pass

        # Sync to SQLite db
        if last_pay_df is not None:
            save_table_df("payment_summary", last_pay_df)

        # 2. Update daily sales and sales summary
        daily_paths = [
            self.analytics_dir / "sales" / "sales_daily.parquet",
            self.analytics_dir / "sales_daily.parquet",
        ]
        today_str = now.strftime("%Y-%m-%d")
        last_daily_df = None
        for dp in daily_paths:
            if dp.exists():
                try:
                    df_d = pd.read_parquet(dp)
                    date_col = "date" if "date" in df_d.columns else "period"
                    if date_col in df_d.columns:
                        mask_d = df_d[date_col].astype(str) == today_str
                        if mask_d.any():
                            df_d.loc[mask_d, "revenue"] = df_d.loc[mask_d, "revenue"].astype(float) + amount
                            df_d.loc[mask_d, "orders"] = df_d.loc[mask_d, "orders"].astype(int) + 1
                        else:
                            last_row = df_d.iloc[-1].to_dict() if not df_d.empty else {}
                            last_row[date_col] = today_str
                            last_row["revenue"] = amount
                            last_row["orders"] = 1
                            df_d = pd.concat([df_d, pd.DataFrame([last_row])], ignore_index=True)
                        df_d.to_parquet(dp, index=False)
                        last_daily_df = df_d
                except Exception:
                    pass

        if last_daily_df is not None:
            save_table_df("sales_daily", last_daily_df)

        return CashSaleResponse(
            status="SUCCESS",
            message=f"Cash sale of ₹{amount:,.2f} recorded successfully!",
            amount=amount,
            transaction_id=txn_id,
            updated_cash_total=round(updated_cash_rev, 2),
            updated_cash_orders=updated_cash_orders,
            timestamp=now.isoformat(),
        )

