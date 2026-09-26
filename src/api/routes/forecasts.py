"""
Forecast routes for VyaparMitra Phase 6 API.
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from src.api.schemas import DemandForecastResponse, SalesForecastResponse
from src.api.services.forecast_service import ForecastService

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])
service = ForecastService()


@router.get("/sales", response_model=SalesForecastResponse)
def get_sales_forecast() -> SalesForecastResponse:
    """Returns 7-day predicted store sales revenue with daily forecast series."""
    return service.get_sales_forecast()


@router.get("/demand", response_model=DemandForecastResponse)
def get_demand_forecast(
    limit: int = Query(30, ge=1, le=200, description="Max SKUs to return")
) -> DemandForecastResponse:
    """Returns SKU-level 7-day projected demand units."""
    return service.get_demand_forecast(limit=limit)
