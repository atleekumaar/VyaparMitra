"""
VyaparMitra Phase 2: Business Intelligence & Analytics Engine package.
"""

from src.analytics.sales_analytics import SalesAnalytics
from src.analytics.customer_analytics import CustomerAnalytics
from src.analytics.product_analytics import ProductAnalytics
from src.analytics.category_analytics import CategoryAnalytics
from src.analytics.time_analytics import TimeAnalytics
from src.analytics.payment_analytics import PaymentAnalytics
from src.analytics.merchant_analytics import MerchantAnalytics
from src.analytics.context_analytics import ContextAnalytics
from src.analytics.trend_analytics import TrendAnalytics


def __getattr__(name: str):
    if name == "AnalyticsEngine":
        from src.analytics.analytics_engine import AnalyticsEngine
        return AnalyticsEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AnalyticsEngine",
    "SalesAnalytics",
    "CustomerAnalytics",
    "ProductAnalytics",
    "CategoryAnalytics",
    "TimeAnalytics",
    "PaymentAnalytics",
    "MerchantAnalytics",
    "ContextAnalytics",
    "TrendAnalytics",
]
