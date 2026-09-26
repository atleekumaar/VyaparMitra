"""
Recommendation and Action Center routes for VyaparMitra Phase 6 API.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from src.api.schemas import (
    ActionStatusUpdateRequest,
    ActionStatusUpdateResponse,
    RecommendationDetailResponse,
    RecommendationListResponse,
)
from src.api.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])
service = RecommendationService()


@router.get("", response_model=RecommendationListResponse)
def list_recommendations(
    type: Optional[str] = Query(None, description="Filter by subsystem type (e.g. INVENTORY, RETENTION, CROSS_SELL, PRICING)"),
    priority: Optional[str] = Query(None, description="Filter by priority band (CRITICAL, HIGH, MEDIUM, LOW)"),
    status: Optional[str] = Query(None, description="Filter by status (GENERATED, VIEWED, ACCEPTED, REJECTED, EXECUTED)"),
    limit: int = Query(100, ge=1, le=500, description="Max recommendations to return"),
) -> RecommendationListResponse:
    """Returns filtered list of prioritized merchant recommendations."""
    return service.list_recommendations(rec_type=type, priority=priority, status=status, limit=limit)


@router.get("/{recommendation_id}", response_model=RecommendationDetailResponse)
def get_recommendation_detail(recommendation_id: str) -> RecommendationDetailResponse:
    """Returns recommendation details and full 6-part evidence rationale."""
    rec = service.get_recommendation(recommendation_id)
    if not rec:
        raise HTTPException(
            status_code=404,
            detail=f"Recommendation with ID '{recommendation_id}' not found."
        )
    return rec


@router.post("/{recommendation_id}/status", response_model=ActionStatusUpdateResponse)
def update_action_status(
    recommendation_id: str,
    payload: ActionStatusUpdateRequest,
) -> ActionStatusUpdateResponse:
    """Updates the action status (ACCEPTED, REJECTED, EXECUTED, VIEWED)."""
    return service.update_status(recommendation_id=recommendation_id, new_status=payload.status)
