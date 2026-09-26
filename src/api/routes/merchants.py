"""
Merchant & Benchmark API Routes for VyaparMitra.
Provides peer benchmarking scorecards, peer groups, rankings, and merchant directory.
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, Path

from src.analytics.benchmark import get_benchmark_engine
from src.api.schemas import BenchmarkResponse, MerchantListResponse

logger = logging.getLogger("vyaparmitra.api.merchants")
router = APIRouter(tags=["Merchants & Benchmarking"])


@router.get(
    "/merchants",
    response_model=MerchantListResponse,
    summary="List all available merchants for dashboard demo switching",
)
def list_merchants() -> MerchantListResponse:
    """Returns directory of all available merchants with location & category info."""
    engine = get_benchmark_engine()
    merchants = engine.list_merchants()
    return MerchantListResponse(total=len(merchants), merchants=merchants)


@router.get(
    "/merchants/{merchant_id}/benchmark",
    response_model=BenchmarkResponse,
    summary="Get peer benchmark scorecard for a merchant",
)
def get_merchant_benchmark(
    merchant_id: str = Path(..., description="Target merchant ID (e.g., M015, M001)")
) -> BenchmarkResponse:
    """
    Computes/serves peer benchmarks across 6 core operational metrics:
    Repeat Rate, Ticket Size, Payment Failure Rate, Refund Rate, UPI Share, and MoM Growth.
    """
    engine = get_benchmark_engine()
    benchmark = engine.get_benchmark(merchant_id)
    if not benchmark:
        raise HTTPException(
            status_code=404,
            detail=f"Benchmark data for merchant '{merchant_id}' not found.",
        )
    return BenchmarkResponse(**benchmark)


@router.get(
    "/benchmark/{merchant_id}",
    response_model=BenchmarkResponse,
    include_in_schema=False,
)
def get_benchmark_alias(merchant_id: str) -> BenchmarkResponse:
    """Convenience alias for /merchants/{merchant_id}/benchmark."""
    return get_merchant_benchmark(merchant_id)
