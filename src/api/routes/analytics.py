"""
Analytics routes for VyaparMitra Phase 6 API.
Supports multi-tenant merchant context via query params, X-Merchant-Id, or JWT Bearer.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends
from src.api.auth import get_request_merchant_id
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
def get_sales_analytics(
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> SalesAnalyticsResponse:
    """Returns historical sales metrics, total orders, AOV, and daily time series."""
    return service.get_sales_analytics(merchant_id=merchant_id)


@router.get("/customers", response_model=CustomerAnalyticsResponse)
def get_customer_analytics(
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> CustomerAnalyticsResponse:
    """Returns customer segment breakdown and churn risk counts."""
    return service.get_customer_analytics(merchant_id=merchant_id)


@router.get("/products", response_model=ProductAnalyticsResponse)
def get_product_analytics(
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> ProductAnalyticsResponse:
    """Returns top performing SKUs and Pareto concentration ratio."""
    return service.get_product_analytics(merchant_id=merchant_id)


@router.get("/categories", response_model=CategoryAnalyticsResponse)
def get_category_analytics(
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> CategoryAnalyticsResponse:
    """Returns category-level revenue and order share breakdown."""
    return service.get_category_analytics(merchant_id=merchant_id)


@router.get("/payments", response_model=PaymentAnalyticsResponse)
def get_payment_analytics(
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> PaymentAnalyticsResponse:
    """Returns payment methods breakdown (UPI vs Cash vs Card) with revenue shares."""
    return service.get_payment_analytics(merchant_id=merchant_id)


@router.get("/trends", response_model=TrendAnalyticsResponse)
def get_trend_analytics(
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> TrendAnalyticsResponse:
    """Returns business momentum trend prediction and historical velocity."""
    return service.get_trend_analytics(merchant_id=merchant_id)


@router.get("/anomalies", response_model=AnomalyResponse)
def get_anomaly_analytics(
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> AnomalyResponse:
    """Returns statistical revenue anomalies detected using IQR/z-score."""
    return service.get_anomaly_analytics(merchant_id=merchant_id)


@router.post("/cash-sale", response_model=CashSaleResponse)
def record_cash_sale(
    payload: CashSaleRequest,
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> CashSaleResponse:
    """Records a manual/cash sale transaction and updates payment & sales analytics."""
    return service.record_cash_sale(payload, merchant_id=merchant_id)
