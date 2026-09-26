"""
Product routes for VyaparMitra Phase 6 API.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from src.api.schemas import ProductDetailResponse, ProductListItem
from src.api.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])
service = ProductService()


@router.get("", response_model=List[ProductListItem])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search product ID or title"),
    limit: int = Query(100, ge=1, le=500, description="Max products to return"),
) -> List[ProductListItem]:
    """Returns catalog list with historical revenue and 7-day demand projections."""
    return service.list_products(category=category, search=search, limit=limit)


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product_detail(product_id: str) -> ProductDetailResponse:
    """Returns detailed product metrics, margin, forecast, cross-sell pairs, and actions."""
    product = service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID '{product_id}' was not found in catalog."
        )
    return product
