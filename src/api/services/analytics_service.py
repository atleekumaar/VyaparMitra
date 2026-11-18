"""
Analytics Service for VyaparMitra Phase 6 API.
Interfaces with Phase 2 data marts for Sales, Customers, Products, Categories, Payments, Trends, and Anomalies,
or dynamic operational tables for non-demo merchants.
"""

from __future__ import annotations

import datetime
import uuid
from pathlib import Path
from typing import Any, List
import pandas as pd
from src.api.db import fetch_table_df, get_db_connection, save_table_df

from src.api.config import APIConfig, get_api_config
from src.api.schemas import (
    AnomalyItem,
    AnomalyResponse,
    CashSaleResponse,
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

    def get_sales_analytics(self, merchant_id: str | None = None) -> SalesAnalyticsResponse:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")

        if is_explicit_non_demo:
            conn = get_db_connection()
            try:
                sales_summary = conn.execute(
                    """
                    SELECT COUNT(*) as tot_orders, COALESCE(SUM(total_amount), 0.0) as tot_rev,
                           COALESCE(AVG(total_amount), 0.0) as aov, COALESCE(SUM(discount), 0.0) as tot_disc
                    FROM sales
                    WHERE business_id = ? AND status != 'CANCELLED'
                    """,
                    (merchant_id,)
                ).fetchone()

                tot_orders = int(sales_summary["tot_orders"]) if sales_summary else 0
                tot_rev = float(sales_summary["tot_rev"]) if sales_summary else 0.0
                aov = round(float(sales_summary["aov"]), 2) if (sales_summary and tot_orders > 0) else 0.0
                disc = round(float(sales_summary["tot_disc"]) / tot_rev, 4) if tot_rev > 0 else 0.0

                daily_rows = conn.execute(
                    """
                    SELECT DATE(created_at) as sale_date, COUNT(*) as orders, COALESCE(SUM(total_amount), 0.0) as revenue
                    FROM sales
                    WHERE business_id = ? AND status != 'CANCELLED'
                    GROUP BY DATE(created_at)
                    ORDER BY DATE(created_at) ASC
                    """,
                    (merchant_id,)
                ).fetchall()

                daily_points = [
                    DailySalesPoint(
                        date=r["sale_date"],
                        revenue=round(float(r["revenue"]), 2),
                        orders=int(r["orders"]),
                        units=None,
                        average_order_value=round(float(r["revenue"]) / int(r["orders"]), 2) if int(r["orders"]) > 0 else None,
                    )
                    for r in daily_rows
                ]
                return SalesAnalyticsResponse(
                    total_revenue=tot_rev,
                    total_orders=tot_orders,
                    average_order_value=aov,
                    discount_rate=disc,
                    daily_series=daily_points,
                )
            finally:
                conn.close()

        # Fallback to pre-computed synthetic data marts for demo mode M001 / M015
        tot_rev = 0.0
        tot_orders = 0
        aov = 0.0
        disc = 0.0
        daily_points: List[DailySalesPoint] = []

        df_sum = fetch_table_df("sales_summary")
        if not df_sum.empty:
            r = df_sum.iloc[0]
            tot_rev = float(r.get("total_revenue", 0.0))
            tot_orders = int(r.get("total_orders", 0))
            aov = float(r.get("average_order_value", 0.0))
            disc = float(r.get("discount_rate", 0.0))

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

    def get_customer_analytics(self, merchant_id: str | None = None) -> CustomerAnalyticsResponse:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")

        if is_explicit_non_demo:
            conn = get_db_connection()
            try:
                cust_rows = conn.execute(
                    "SELECT id, name, current_balance, credit_limit FROM customers WHERE business_id = ?",
                    (merchant_id,)
                ).fetchall()
                tot_cust = len(cust_rows)
                spend_row = conn.execute(
                    "SELECT COALESCE(SUM(total_amount), 0.0) as tot_spend FROM sales WHERE business_id = ? AND status != 'CANCELLED'",
                    (merchant_id,)
                ).fetchone()
                tot_spend = round(float(spend_row["tot_spend"]), 2) if spend_row else 0.0
                segments = [
                    CustomerSegmentSummary(
                        segment_name="Active Customers",
                        customer_count=tot_cust,
                        total_revenue=tot_spend,
                        revenue_share=1.0 if tot_cust > 0 else 0.0,
                    )
                ] if tot_cust > 0 else []
                return CustomerAnalyticsResponse(
                    total_customers=tot_cust,
                    high_risk_count=0,
                    medium_risk_count=0,
                    low_risk_count=tot_cust,
                    segments=segments,
                )
            finally:
                conn.close()

        tot_cust = 0
        high_r = 0
        med_r = 0
        low_r = 0
        segments: List[CustomerSegmentSummary] = []

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

    def get_product_analytics(self, merchant_id: str | None = None) -> ProductAnalyticsResponse:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")

        if is_explicit_non_demo:
            conn = get_db_connection()
            try:
                inv_rows = conn.execute(
                    """
                    SELECT i.product_id, i.product_name, i.category, i.current_stock,
                           COALESCE(SUM(si.total_price), 0.0) as rev,
                           COALESCE(SUM(si.quantity), 0) as units
                    FROM inventory i
                    LEFT JOIN sale_items si ON si.product_id = i.product_id
                    LEFT JOIN sales s ON si.sale_id = s.id AND s.business_id = ? AND s.status != 'CANCELLED'
                    WHERE i.business_id = ?
                    GROUP BY i.product_id
                    ORDER BY rev DESC, i.updated_at DESC
                    LIMIT 20
                    """,
                    (merchant_id, merchant_id)
                ).fetchall()

                top_products = [
                    ProductRankItem(
                        product_id=str(r["product_id"]),
                        product_name=str(r["product_name"]),
                        category=str(r["category"] or "General"),
                        revenue=round(float(r["rev"]), 2),
                        units=int(r["units"]),
                        rank=idx + 1,
                        current_stock=int(r["current_stock"] if r["current_stock"] is not None else 0),
                    )
                    for idx, r in enumerate(inv_rows)
                ]
                return ProductAnalyticsResponse(
                    total_products_tracked=len(inv_rows),
                    top_performers=top_products,
                    pareto_80_20_ratio=0.80 if len(inv_rows) > 0 else None,
                )
            finally:
                conn.close()

        top_products: List[ProductRankItem] = []
        tot_count = 0
        pareto_ratio = 0.80

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

        df_par = fetch_table_df("pareto_analysis")
        if not df_par.empty and "pareto_share" in df_par.columns:
            pareto_ratio = float(df_par["pareto_share"].iloc[0])

        return ProductAnalyticsResponse(
            total_products_tracked=tot_count,
            top_performers=top_products,
            pareto_80_20_ratio=pareto_ratio,
        )

    def get_category_analytics(self, merchant_id: str | None = None) -> CategoryAnalyticsResponse:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")

        if is_explicit_non_demo:
            conn = get_db_connection()
            try:
                cat_rows = conn.execute(
                    """
                    SELECT i.category,
                           COALESCE(SUM(si.total_price), 0.0) as rev,
                           COUNT(DISTINCT s.id) as orders
                    FROM inventory i
                    JOIN sale_items si ON si.product_id = i.product_id
                    JOIN sales s ON si.sale_id = s.id AND s.business_id = ? AND s.status != 'CANCELLED'
                    WHERE i.business_id = ?
                    GROUP BY i.category
                    ORDER BY rev DESC
                    """,
                    (merchant_id, merchant_id)
                ).fetchall()

                tot_cat_rev = sum(float(r["rev"]) for r in cat_rows)
                categories = [
                    CategoryShareItem(
                        category=str(r["category"] or "General"),
                        revenue=round(float(r["rev"]), 2),
                        orders=int(r["orders"]),
                        revenue_share=round(float(r["rev"]) / tot_cat_rev, 4) if tot_cat_rev > 0 else 0.0,
                    )
                    for r in cat_rows
                ]
                return CategoryAnalyticsResponse(categories=categories)
            finally:
                conn.close()

        categories: List[CategoryShareItem] = []
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

    def get_payment_analytics(self, merchant_id: str | None = None) -> PaymentAnalyticsResponse:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")

        if is_explicit_non_demo:
            conn = get_db_connection()
            try:
                pay_rows = conn.execute(
                    """
                    SELECT payment_method, COUNT(*) as tx_count, COALESCE(SUM(total_amount), 0.0) as rev
                    FROM sales
                    WHERE business_id = ? AND status != 'CANCELLED'
                    GROUP BY payment_method
                    """,
                    (merchant_id,)
                ).fetchall()

                tot_pay_rev = sum(float(r["rev"]) for r in pay_rows)
                tot_pay_tx = sum(int(r["tx_count"]) for r in pay_rows)
                methods = [
                    PaymentMethodItem(
                        payment_method=str(r["payment_method"]).upper(),
                        transaction_count=int(r["tx_count"]),
                        total_revenue=round(float(r["rev"]), 2),
                        revenue_share=round(float(r["rev"]) / tot_pay_rev, 4) if tot_pay_rev > 0 else 0.0,
                        transaction_share=round(float(r["tx_count"]) / tot_pay_tx, 4) if tot_pay_tx > 0 else 0.0,
                    )
                    for r in pay_rows
                ]
                primary_method = methods[0].payment_method if methods else "CASH"
                return PaymentAnalyticsResponse(
                    payment_methods=methods,
                    primary_payment_method=primary_method,
                )
            finally:
                conn.close()

        methods: List[PaymentMethodItem] = []
        df_p = fetch_table_df("payment_summary")
        tot_rev = df_p["payment_method_revenue"].sum() if ("payment_method_revenue" in df_p.columns and not df_p.empty) else 1.0
        primary_method = "UPI"

        for _, r in df_p.iterrows():
            pm = str(r.get("payment_method", "OTHER")).upper()
            rev = float(r.get("payment_method_revenue", r.get("revenue", 0.0)))
            tx_cnt = int(r.get("payment_method_orders", r.get("transaction_count", r.get("orders", 0))))
            share = round(rev / tot_rev, 4) if tot_rev > 0 else 0.0
            methods.append(
                PaymentMethodItem(
                    payment_method=pm,
                    transaction_count=tx_cnt,
                    total_revenue=round(rev, 2),
                    revenue_share=share,
                    transaction_share=round(float(r.get("orders_share", share)), 4),
                )
            )

        if methods:
            primary_method = max(methods, key=lambda m: m.total_revenue).payment_method

        return PaymentAnalyticsResponse(
            payment_methods=methods,
            primary_payment_method=primary_method,
        )

    def get_trend_analytics(self, merchant_id: str | None = None) -> TrendAnalyticsResponse:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")
        if is_explicit_non_demo:
            return TrendAnalyticsResponse(
                predicted_trend="STABLE",
                confidence=0.50,
                horizon_days=7,
                historical_revenue_change_pct=0.0,
            )

        pred_trend = "STABLE"
        conf = 0.50
        horizon = 7
        hist_change = 0.0

        df_p = fetch_table_df("business_trend_predictions")
        if not df_p.empty:
            pred_trend = str(df_p["predicted_trend"].iloc[0]).upper()
            conf = round(float(df_p["confidence"].iloc[0]), 2)
            horizon = int(df_p["horizon_days"].iloc[0])

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

    def get_anomaly_analytics(self, merchant_id: str | None = None) -> AnomalyResponse:
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")
        if is_explicit_non_demo:
            return AnomalyResponse(
                total_anomalies_detected=0,
                anomalies=[],
            )

        items: List[AnomalyItem] = []
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

    def record_cash_sale(self, req: Any, merchant_id: str | None = None) -> Any:
        amount = float(req.amount)
        now = datetime.datetime.now()
        txn_id = f"CASH_{int(now.timestamp())}_{uuid.uuid4().hex[:6]}"
        is_explicit_non_demo = merchant_id is not None and merchant_id not in ("M001", "M015")

        if is_explicit_non_demo:
            conn = get_db_connection()
            try:
                b_row = conn.execute(
                    "SELECT id FROM branches WHERE business_id = ? ORDER BY is_main DESC LIMIT 1",
                    (merchant_id,)
                ).fetchone()
                branch_id = b_row["id"] if b_row else f"BR_{merchant_id}_MAIN"

                conn.execute(
                    """
                    INSERT INTO sales (
                        id, invoice_number, business_id, branch_id, subtotal, discount,
                        tax, total_amount, payment_method, status, created_by, created_at
                    ) VALUES (?, ?, ?, ?, ?, 0.0, 0.0, ?, 'CASH', 'COMPLETED', 'POS', ?)
                    """,
                    (txn_id, f"INV_{txn_id}", merchant_id, branch_id, amount, amount, now.isoformat())
                )
                conn.commit()

                c_row = conn.execute(
                    """
                    SELECT COUNT(*) as cnt, COALESCE(SUM(total_amount), 0.0) as tot
                    FROM sales
                    WHERE business_id = ? AND payment_method = 'CASH' AND status != 'CANCELLED'
                    """,
                    (merchant_id,)
                ).fetchone()
                updated_cash_rev = float(c_row["tot"]) if c_row else amount
                updated_cash_orders = int(c_row["cnt"]) if c_row else 1
            finally:
                conn.close()

            return CashSaleResponse(
                status="SUCCESS",
                message=f"Cash sale of ₹{amount:,.2f} recorded successfully!",
                amount=amount,
                transaction_id=txn_id,
                updated_cash_total=round(updated_cash_rev, 2),
                updated_cash_orders=updated_cash_orders,
                timestamp=now.isoformat(),
            )

        # Demo mode updates
        updated_cash_rev = 0.0
        updated_cash_orders = 0

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
                except Exception:
                    pass

        if last_pay_df is not None:
            save_table_df("payment_summary", last_pay_df)

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
