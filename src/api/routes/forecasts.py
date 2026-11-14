"""
Forecast routes for VyaparMitra Phase 6 API.
Supports multi-tenant merchant context via query params, X-Merchant-Id, or JWT Bearer.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.api.auth import get_request_merchant_id
from src.api.schemas import DemandForecastResponse, SalesForecastResponse
from src.api.services.forecast_service import ForecastService

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])
service = ForecastService()


@router.get("/sales", response_model=SalesForecastResponse)
def get_sales_forecast(
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> SalesForecastResponse:
    """Returns 7-day predicted store sales revenue with daily forecast series."""
    return service.get_sales_forecast(merchant_id=merchant_id)


@router.get("/demand", response_model=DemandForecastResponse)
def get_demand_forecast(
    limit: int = Query(30, ge=1, le=200, description="Max SKUs to return"),
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> DemandForecastResponse:
    """Returns SKU-level 7-day projected demand units."""
    return service.get_demand_forecast(limit=limit, merchant_id=merchant_id)
