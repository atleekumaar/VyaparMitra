"""
Analytics routes for VyaparMitra Phase 6 API.
"""

from __future__ import annotations

from fastapi import APIRouter
from src.api.schemas import (
    AnomalyResponse,
    CashSaleRequest,
    CashSaleResponse,
    CategoryAnalyticsResponse,
    CustomerAnalyticsResponse,
    PaymentAnalyticsResponse,
    ProductAnalyticsResponse,
    SalesAnalyticsResponse,
    TrendAnalyticsResponse,
)
from src.api.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])
service = AnalyticsService()


@router.get("/sales", response_model=SalesAnalyticsResponse)
def get_sales_analytics() -> SalesAnalyticsResponse:
    """Returns historical sales metrics, total orders, AOV, and daily time series."""
    return service.get_sales_analytics()


@router.get("/customers", response_model=CustomerAnalyticsResponse)
def get_customer_analytics() -> CustomerAnalyticsResponse:
    """Returns customer segment breakdown and churn risk counts."""
    return service.get_customer_analytics()


@router.get("/products", response_model=ProductAnalyticsResponse)
def get_product_analytics() -> ProductAnalyticsResponse:
    """Returns top performing SKUs and Pareto concentration ratio."""
    return service.get_product_analytics()


@router.get("/categories", response_model=CategoryAnalyticsResponse)
def get_category_analytics() -> CategoryAnalyticsResponse:
    """Returns category-level revenue and order share breakdown."""
    return service.get_category_analytics()


@router.get("/payments", response_model=PaymentAnalyticsResponse)
def get_payment_analytics() -> PaymentAnalyticsResponse:
    """Returns payment methods breakdown (UPI vs Cash vs Card) with revenue shares."""
    return service.get_payment_analytics()


@router.get("/trends", response_model=TrendAnalyticsResponse)
def get_trend_analytics() -> TrendAnalyticsResponse:
    """Returns business momentum trend prediction and historical velocity."""
    return service.get_trend_analytics()


@router.get("/anomalies", response_model=AnomalyResponse)
def get_anomaly_analytics() -> AnomalyResponse:
    """Returns statistical revenue anomalies detected using IQR/z-score."""
    return service.get_anomaly_analytics()


@router.post("/cash-sale", response_model=CashSaleResponse)
def record_cash_sale(payload: CashSaleRequest) -> CashSaleResponse:
    """Records a manual/cash sale transaction and updates payment & sales analytics."""
    return service.record_cash_sale(payload)

