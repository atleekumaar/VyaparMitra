"""
Dashboard routes for VyaparMitra Phase 6 API.
Supports multi-tenant merchant context via query params, X-Merchant-Id, or JWT Bearer.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.api.auth import get_request_merchant_id
from src.api.schemas import DashboardActionsResponse, DashboardSummaryResponse
from src.api.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
service = DashboardService()


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> DashboardSummaryResponse:
    """Returns top business health KPIs, 7-day forecast total, and trend indicator."""
    return service.get_summary(merchant_id=merchant_id)


@router.get("/actions", response_model=DashboardActionsResponse)
def get_dashboard_actions(
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
    limit: int = Query(5, ge=1, le=20, description="Max actions to return"),
) -> DashboardActionsResponse:
    """Returns top prioritized commercial and inventory actions."""
    return service.get_top_actions(merchant_id=merchant_id, limit=limit)
