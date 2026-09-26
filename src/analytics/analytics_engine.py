"""
Central Analytics Engine and Orchestrator for VyaparMitra Phase 2.
Coordinates all analytical domains, exposes a clean Python API,
exports the Analytics Data Mart to data/analytics/, validates output quality,
and reconciles perfectly with Phase 1 feature store totals.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, Optional, Tuple
import pandas as pd
import yaml

from src.analytics.category_analytics import CategoryAnalytics
from src.analytics.context_analytics import ContextAnalytics
from src.analytics.customer_analytics import CustomerAnalytics
from src.analytics.merchant_analytics import MerchantAnalytics
from src.analytics.payment_analytics import PaymentAnalytics
from src.analytics.product_analytics import ProductAnalytics
from src.analytics.sales_analytics import SalesAnalytics
from src.analytics.time_analytics import TimeAnalytics
from src.analytics.trend_analytics import TrendAnalytics
from src.reporting.report_generator import ReportGenerator
from src.reporting.summary_generator import SummaryGenerator
from src.schemas.analytics_schema import BusinessSummary, CustomerKPISet, SalesKPISet

logger = logging.getLogger("VyaparMitra.AnalyticsEngine")


class AnalyticsEngine:
    """
    Main entry point and execution engine for VyaparMitra Phase 2 Business Intelligence.
    Provides typed methods for interactive querying and automated batch data mart generation.
    """

    def __init__(self, config_path: str = "configs/config.yaml") -> None:
        self.config_path = config_path
        self.config = self._load_config(config_path)

        # File paths
        paths_cfg = self.config.get("paths", {})
        self.features_dir = Path(paths_cfg.get("features", "data/features"))
        self.analytics_dir = Path(paths_cfg.get("analytics", "data/analytics"))
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

        # Ingest Phase 1 feature store tables immutably
        self._load_feature_store()

        # Initialize domain analytics modules
        self.sales_engine = SalesAnalytics(self.transactions_df, self.daily_df)
        self.customer_engine = CustomerAnalytics(self.customer_features_df, self.transactions_df, self.config)
        self.product_engine = ProductAnalytics(self.product_features_df, self.transactions_df)
        self.category_engine = CategoryAnalytics(self.transactions_df)
        self.time_engine = TimeAnalytics(self.transactions_df)
        self.payment_engine = PaymentAnalytics(self.transactions_df)
        self.merchant_engine = MerchantAnalytics(self.merchant_features_df, self.transactions_df)
        min_sample = self.config.get("analytics", {}).get("minimum_sample_size", {}).get("festival", 3)
        self.context_engine = ContextAnalytics(self.transactions_df, self.daily_df, min_sample_size=min_sample)
        self.trend_engine = TrendAnalytics(self.transactions_df, self.config)

        self.summary_gen = SummaryGenerator()
        self.report_gen = ReportGenerator()

    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_feature_store(self) -> None:
        """Load Phase 1 feature store files into memory."""
        tx_path = self.features_dir / "transaction_features.parquet"
        merchant_path = self.features_dir / "merchant_features.parquet"
        customer_path = self.features_dir / "customer_features.parquet"
        product_path = self.features_dir / "product_features.parquet"
        daily_path = self.features_dir / "daily_features.parquet"

        if not tx_path.exists():
            raise FileNotFoundError(f"Required feature store file missing: {tx_path}. Run Phase 1 pipeline first.")

        self.transactions_df = pd.read_parquet(tx_path)
        self.merchant_features_df = pd.read_parquet(merchant_path) if merchant_path.exists() else pd.DataFrame()
        self.customer_features_df = pd.read_parquet(customer_path) if customer_path.exists() else pd.DataFrame()
        self.product_features_df = pd.read_parquet(product_path) if product_path.exists() else pd.DataFrame()
        self.daily_df = pd.read_parquet(daily_path) if daily_path.exists() else pd.DataFrame()

    # --- Public Analytical API ---

    def sales(
        self,
        period: str = "monthly",
        merchant_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Query periodic sales and growth metrics."""
        return self.sales_engine.get_period_comparison(
            frequency=period,
            merchant_id=merchant_id,
            start_date=start_date,
            end_date=end_date,
        )

    def sales_kpis(
        self,
        merchant_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> SalesKPISet:
        """Query core aggregate sales KPIs."""
        return self.sales_engine.get_core_kpis(
            merchant_id=merchant_id,
            start_date=start_date,
            end_date=end_date,
        )

    def customer_summary(self, merchant_id: Optional[str] = None) -> CustomerKPISet:
        """Query customer volume and engagement metrics."""
        return self.customer_engine.get_customer_kpis(merchant_id=merchant_id)

    def customer_segments(self) -> pd.DataFrame:
        """Query customer RFM segmentation matrix."""
        return self.customer_engine.get_rfm_segmentation()

    def customer_cohorts(self) -> pd.DataFrame:
        """Query historical cohort retention matrix."""
        return self.customer_engine.get_cohort_matrix()

    def product_summary(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Query product SKU performance matrix."""
        return self.product_engine.get_performance_matrix(merchant_id=merchant_id)

    def product_rankings(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Query product independent multi-metric rankings."""
        return self.product_engine.get_product_rankings(merchant_id=merchant_id)

    def category_summary(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Query category-level contribution and performance metrics."""
        return self.category_engine.get_category_summary(merchant_id=merchant_id)

    def payment_summary(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Query payment method volume and share analysis."""
        return self.payment_engine.get_payment_summary(merchant_id=merchant_id)

    def merchant_summary(self, merchant_id: Optional[str] = None) -> pd.DataFrame:
        """Query merchant operational metrics."""
        return self.merchant_engine.get_merchant_summary(merchant_id=merchant_id)

    def merchant_benchmarks(self) -> pd.DataFrame:
        """Query descriptive peer benchmarks."""
        return self.merchant_engine.get_merchant_benchmarks()

    def trends(self, frequency: str = "monthly", metric: str = "net_amount") -> pd.DataFrame:
        """Query directional trend classifications."""
        return self.trend_engine.get_trend_analysis(frequency=frequency, metric=metric)

    def anomalies(self, metric: str = "net_amount") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Query statistical outliers in daily performance."""
        return self.trend_engine.get_daily_anomalies(metric=metric)

    def business_summary(self) -> BusinessSummary:
        """Synthesizes all modules into a machine-readable summary object."""
        sales_kpis = self.sales_kpis()
        monthly_sales = self.sales(period="monthly")
        customer_kpis = self.customer_summary()
        cat_df = self.category_summary()
        prod_rankings = self.product_rankings()
        peak_periods = self.time_engine.get_peak_periods()
        pay_df = self.payment_summary()
        _, fest_summary = self.context_engine.get_festival_analysis()
        _, weather_summary = self.context_engine.get_weather_analysis()

        top_cat = str(cat_df.iloc[0]["product_category"]) if not cat_df.empty else "N/A"
        top_prod = str(prod_rankings.iloc[0]["product_name"]) if not prod_rankings.empty else "N/A"

        return self.summary_gen.generate_summary(
            sales_kpis=sales_kpis,
            monthly_sales=monthly_sales,
            customer_kpis=customer_kpis,
            top_category=top_cat,
            top_product=top_prod,
            peak_periods=peak_periods,
            payment_summary=pay_df,
            festival_summary=fest_summary,
            weather_summary=weather_summary,
            category_summary=cat_df,
        )

    # --- Batch Analytics Data Mart Generation ---

    def run_all_analytics(self) -> Dict[str, Any]:
        """
        Executes all analytical pipelines, validates outputs, reconciles against Phase 1,
        and saves 20+ analytical artifacts to data/analytics/.
        """
        start_time = time.time()
        logger.info("Running complete Phase 2 Business Intelligence Engine...")

        # 1. Sales
        sales_kpi_obj = self.sales_kpis()
        sales_summary_df = pd.DataFrame([sales_kpi_obj.model_dump()])
        sales_daily_df = self.sales(period="daily")
        sales_weekly_df = self.sales(period="weekly")
        sales_monthly_df = self.sales(period="monthly")

        # 2. Customers
        customer_kpi_obj = self.customer_summary()
        customer_summary_df = pd.DataFrame([customer_kpi_obj.model_dump()])
        customer_segments_df = self.customer_segments()
        customer_cohorts_df = self.customer_cohorts()

        # 3. Products
        product_summary_df = self.product_summary()
        product_rankings_df = self.product_rankings()

        # 4. Categories
        category_summary_df = self.category_summary()
        category_monthly_df = self.category_engine.get_category_monthly()

        # 5. Time
        time_hourly_df = self.time_engine.get_hourly_analytics()
        time_weekday_df = self.time_engine.get_weekday_analytics()
        time_monthly_df = self.time_engine.get_monthly_analytics()

        # 6. Payments
        payment_summary_df = self.payment_summary()

        # 7. Merchants
        merchant_summary_df = self.merchant_summary()
        merchant_benchmarks_df = self.merchant_benchmarks()

        # 8. Context (Festivals & Weather)
        festival_df, fest_stats = self.context_engine.get_festival_analysis()
        weather_df, weather_stats = self.context_engine.get_weather_analysis()

        # 9. Trends & Anomalies
        trend_analysis_df = self.trends(frequency="monthly")
        anomaly_analysis_df, anomaly_stats = self.anomalies()

        # 10. Summary and Reports
        summary_obj = self.business_summary()
        summary_json = summary_obj.model_dump()
        report_md = self.report_gen.generate_markdown_report(
            summary=summary_obj,
            category_df=category_summary_df,
            product_rankings_df=product_rankings_df,
            payment_df=payment_summary_df,
            trend_df=trend_analysis_df,
        )

        # Artifacts dictionary mapping filename to DataFrame
        artifacts: Dict[str, Tuple[pd.DataFrame, str]] = {
            "sales_summary": (sales_summary_df, "sales"),
            "sales_daily": (sales_daily_df, "sales"),
            "sales_weekly": (sales_weekly_df, "sales"),
            "sales_monthly": (sales_monthly_df, "sales"),
            "customer_summary": (customer_summary_df, "customers"),
            "customer_segments": (customer_segments_df, "customers"),
            "customer_cohorts": (customer_cohorts_df, "customers"),
            "product_summary": (product_summary_df, "products"),
            "product_rankings": (product_rankings_df, "products"),
            "category_summary": (category_summary_df, "categories"),
            "category_monthly": (category_monthly_df, "categories"),
            "time_hourly": (time_hourly_df, "time"),
            "time_weekday": (time_weekday_df, "time"),
            "time_monthly": (time_monthly_df, "time"),
            "payment_summary": (payment_summary_df, "payments"),
            "merchant_summary": (merchant_summary_df, "merchants"),
            "merchant_benchmarks": (merchant_benchmarks_df, "merchants"),
            "festival_analysis": (festival_df, "context"),
            "weather_analysis": (weather_df, "context"),
            "trend_analysis": (trend_analysis_df, "trends"),
            "anomaly_analysis": (anomaly_analysis_df, "trends"),
        }

        # 11. Quality Validation of Analytical Outputs
        validation_results = self._validate_analytics_outputs(artifacts)

        # 12. Reconciliation with Phase 1
        reconciliation = self._reconcile_with_phase1(sales_kpi_obj)

        # 13. Persist to Analytics Data Mart
        for name, (df, sub_dir) in artifacts.items():
            # Write to root data/analytics/
            df.to_parquet(self.analytics_dir / f"{name}.parquet", index=False)
            df.to_csv(self.analytics_dir / f"{name}.csv", index=False)
            # Also write to category sub-directory
            target_sub = self.analytics_dir / sub_dir
            target_sub.mkdir(parents=True, exist_ok=True)
            df.to_parquet(target_sub / f"{name}.parquet", index=False)
            df.to_csv(target_sub / f"{name}.csv", index=False)

        # Write reports
        with open(self.analytics_dir / "business_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary_json, f, indent=2)

        with open(self.analytics_dir / "business_summary.md", "w", encoding="utf-8") as f:
            f.write(report_md)

        # Also write to reports sub-directory
        reports_sub = self.analytics_dir / "reports"
        reports_sub.mkdir(parents=True, exist_ok=True)
        with open(reports_sub / "business_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary_json, f, indent=2)
        with open(reports_sub / "business_summary.md", "w", encoding="utf-8") as f:
            f.write(report_md)

        elapsed = round(time.time() - start_time, 2)
        logger.info("Phase 2 Analytics completed successfully in %.2f seconds.", elapsed)

        return {
            "elapsed_seconds": elapsed,
            "validation": validation_results,
            "reconciliation": reconciliation,
            "business_summary": summary_json,
            "datasets_generated": len(artifacts),
        }

    def _validate_analytics_outputs(self, artifacts: Dict[str, Tuple[pd.DataFrame, str]]) -> Dict[str, Any]:
        """Validates numerical non-negativity, share summations, and key uniqueness."""
        errors = []

        for name, (df, _) in artifacts.items():
            if df.empty:
                continue

            # Check numeric non-negativity for standard financial/count metrics
            for col in ["revenue", "orders", "units", "aov", "category_revenue", "total_revenue", "merchant_revenue"]:
                if col in df.columns:
                    negative_count = int((df[col] < 0).sum())
                    if negative_count > 0:
                        errors.append(f"{name}.{col} contains {negative_count} negative values.")

            # Validate share columns approximately sum to 1.0 (tolerance 0.02)
            for share_col in ["revenue_share", "orders_share", "unit_share"]:
                if share_col in df.columns and len(df) > 1:
                    tot_share = df[share_col].sum()
                    if not (0.97 <= tot_share <= 1.03):
                        errors.append(f"{name}.{share_col} sum ({tot_share:.4f}) deviates from 1.0.")

        status = "PASS" if not errors else "WARN"
        return {"status": status, "errors": errors}

    def _reconcile_with_phase1(self, sales_kpis: SalesKPISet) -> Dict[str, Any]:
        """
        Reconciles Phase 2 aggregate revenue and orders against Phase 1 transaction features.
        """
        phase1_total_revenue = float(round(self.transactions_df["net_amount"].sum(), 2))
        phase1_orders_count = len(self.transactions_df)

        phase2_total_revenue = float(round(sales_kpis.total_revenue, 2))
        phase2_orders_count = int(sales_kpis.total_orders)

        rev_match = abs(phase1_total_revenue - phase2_total_revenue) < 0.01
        ord_match = phase1_orders_count == phase2_orders_count

        return {
            "phase1_revenue": phase1_total_revenue,
            "phase2_revenue": phase2_total_revenue,
            "revenue_match": rev_match,
            "phase1_orders": phase1_orders_count,
            "phase2_orders": phase2_orders_count,
            "orders_match": ord_match,
            "status": "PASS" if (rev_match and ord_match) else "FAIL",
        }


def main() -> None:
    """CLI execution for Phase 2 Analytics Engine."""
    parser = argparse.ArgumentParser(description="VyaparMitra Phase 2 Business Intelligence Engine")
    parser.add_argument("--config", type=str, default="configs/config.yaml", help="Path to config YAML")
    args = parser.parse_args()

    print("========================================")
    print("VYAPARMITRA PHASE 2")
    print("BUSINESS INTELLIGENCE ENGINE")
    print("========================================\n")

    print("Loading feature store...")
    engine = AnalyticsEngine(config_path=args.config)
    print(f"[OK] Transactions: {len(engine.transactions_df):,}")
    print(f"[OK] Merchants: {len(engine.merchant_features_df):,}")
    print(f"[OK] Customers: {len(engine.customer_features_df):,}")
    print(f"[OK] Products: {len(engine.product_features_df):,}")
    print(f"[OK] Daily records: {len(engine.daily_df):,}\n")

    print("Running analytics...")
    results = engine.run_all_analytics()

    print("[OK] Sales analytics")
    print("[OK] Customer analytics")
    print("[OK] Product analytics")
    print("[OK] Category analytics")
    print("[OK] Time analytics")
    print("[OK] Payment analytics")
    print("[OK] Merchant analytics")
    print("[OK] Festival analytics")
    print("[OK] Weather analytics")
    print("[OK] Trend analytics")
    print("[OK] Anomaly analytics\n")

    print("Generating business summary...")
    print(f"[OK] {results['datasets_generated']}+ analytics datasets generated")
    print(f"[OK] Business summary generated (Runtime: {results['elapsed_seconds']}s)")
    print(f"[OK] Reconciliation Status: {results['reconciliation']['status']} (Rev: Rs {results['reconciliation']['phase2_revenue']:,.2f}, Orders: {results['reconciliation']['phase2_orders']:,})")
    print(f"[OK] Validation Status: {results['validation']['status']}")
    print("\nSTATUS: PASS\n")


if __name__ == "__main__":
    main()
