"""
Customer routes for VyaparMitra Phase 6 API.
Supports multi-tenant merchant context via query params, X-Merchant-Id, or JWT Bearer.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.auth import get_request_merchant_id
from src.api.schemas import CustomerDetailResponse, CustomerListItem
from src.api.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])
service = CustomerService()


@router.get("", response_model=List[CustomerListItem])
def list_customers(
    segment: Optional[str] = Query(None, description="Filter by customer segment"),
    risk_tier: Optional[str] = Query(None, description="Filter by churn risk tier"),
    limit: int = Query(100, ge=1, le=500, description="Max customers to return"),
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> List[CustomerListItem]:
    """Returns customer list with spend, recency, and churn risk classification."""
    return service.list_customers(segment=segment, risk_tier=risk_tier, limit=limit, merchant_id=merchant_id)


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer_detail(
    customer_id: str,
    merchant_id: Optional[str] = Depends(get_request_merchant_id),
) -> CustomerDetailResponse:
    """Returns detailed customer profile, churn probability, and recommended retention action."""
    customer = service.get_customer(customer_id, merchant_id=merchant_id)
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with ID '{customer_id}' was not found in records."
        )
    return customer
