"""
Copilot & MerchantOS Agent Routes for VyaparMitra API.
Combines Phase 5 multilingual Copilot endpoints with JWT-authenticated
Multi-Agent Execution and Persistent L3 Owner Approval workflows.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.api.auth import CurrentUser, enforce_branch_isolation, get_current_user, require_roles
from src.api.schemas import CopilotAskRequest, CopilotAskResponse, CopilotDailyBriefResponse
from src.api.services.copilot_service_adapter import CopilotServiceAdapter
from src.copilot.agents.inventory_tools import InventoryAgentTools
from src.copilot.agents.orchestrator import AgentState, MerchantOSAgentOrchestrator
from src.copilot.agents.security import TenantIsolationError, UnauthorizedAgentActionError

router = APIRouter(prefix="/copilot", tags=["Copilot & MerchantOS Agents"])
adapter = CopilotServiceAdapter()
orchestrator = MerchantOSAgentOrchestrator()


class AgentExecuteRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Merchant query or action request")
    branch_id: Optional[str] = Field(None, description="Optional branch scope")


class AgentExecuteResponse(BaseModel):
    tenant_id: str
    branch_id: Optional[str]
    user_id: str
    role: str
    intent: str
    response: str
    draft_actions: List[Dict[str, Any]] = []


class ApprovalReviewRequest(BaseModel):
    notes: Optional[str] = Field(default="Reviewed via MerchantOS Owner Portal")


@router.post("/ask", response_model=CopilotAskResponse)
def ask_copilot(payload: CopilotAskRequest) -> CopilotAskResponse:
    """Processes a natural language query in Hindi, Hinglish, or English via Phase 5 Copilot."""
    return adapter.ask(payload)


@router.get("/daily-brief", response_model=CopilotDailyBriefResponse)
def get_daily_brief(
    session_id: str = Query("default_session", description="Session identifier"),
    merchant_id: Optional[str] = Query(None, description="Target merchant ID"),
    language: Optional[str] = Query("hinglish", description="Target language (hindi, hinglish, english)"),
) -> CopilotDailyBriefResponse:
    """Generates the morning action briefing covering sales, forecasts, and actions."""
    return adapter.daily_brief(session_id=session_id, merchant_id=merchant_id, language=language)


@router.post("/agent/execute", response_model=AgentExecuteResponse)
def execute_merchant_agent(
    payload: AgentExecuteRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> AgentExecuteResponse:
    """
    Executes MerchantOS Multi-Agent Orchestrator bound to authenticated JWT user,
    enforcing business/branch isolation, RBAC permissions, and L3 approval drafting.
    """
    target_branch = enforce_branch_isolation(current_user, payload.branch_id)
    state: AgentState = {
        "tenant_id": current_user.business_id,
        "user_id": current_user.id,
        "role": current_user.role,
        "branch_id": target_branch,
        "query": payload.query,
        "intent": None,
        "messages": [],
        "draft_actions": [],
        "final_response": None,
    }
    result = orchestrator.route_and_execute(state)
    return AgentExecuteResponse(
        tenant_id=result["tenant_id"],
        branch_id=result["branch_id"],
        user_id=result["user_id"],
        role=result["role"],
        intent=result["intent"] or "UNKNOWN",
        response=result["final_response"] or "",
        draft_actions=result["draft_actions"],
    )


@router.get("/approvals")
def list_agent_approvals(
    status_filter: Optional[str] = Query(None, description="Filter by PENDING_APPROVAL, APPROVED, or REJECTED"),
    current_user: CurrentUser = Depends(require_roles(["owner", "admin", "manager"])),
) -> Dict[str, Any]:
    """Lists persisted L3 agent approval requests for the authenticated business."""
    ctx = {
        "tenant_id": current_user.business_id,
        "user_id": current_user.id,
        "role": current_user.role,
        "branch_id": current_user.branch_id,
    }
    items = InventoryAgentTools.list_approval_requests(status_filter=status_filter, context=ctx)
    return {"total": len(items), "approvals": items}


@router.post("/approvals/{approval_id}/approve")
def approve_agent_request(
    approval_id: str,
    payload: ApprovalReviewRequest = ApprovalReviewRequest(),
    current_user: CurrentUser = Depends(require_roles(["owner", "admin"])),
) -> Dict[str, Any]:
    """Owner-only endpoint: Approves purchase reorder draft, updates live inventory stock, and logs audit."""
    ctx = {
        "tenant_id": current_user.business_id,
        "user_id": current_user.id,
        "user_name": current_user.full_name,
        "role": current_user.role,
        "branch_id": current_user.branch_id,
    }
    try:
        return InventoryAgentTools.approve_reorder_request(
            approval_id=approval_id,
            review_notes=payload.notes or "Approved by Owner",
            context=ctx,
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except (UnauthorizedAgentActionError, TenantIsolationError) as sec_err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(sec_err))


@router.post("/approvals/{approval_id}/reject")
def reject_agent_request(
    approval_id: str,
    payload: ApprovalReviewRequest = ApprovalReviewRequest(),
    current_user: CurrentUser = Depends(require_roles(["owner", "admin"])),
) -> Dict[str, Any]:
    """Owner-only endpoint: Rejects a pending agent purchase reorder draft and logs audit."""
    ctx = {
        "tenant_id": current_user.business_id,
        "user_id": current_user.id,
        "user_name": current_user.full_name,
        "role": current_user.role,
        "branch_id": current_user.branch_id,
    }
    try:
        return InventoryAgentTools.reject_reorder_request(
            approval_id=approval_id,
            review_notes=payload.notes or "Rejected by Owner",
            context=ctx,
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except (UnauthorizedAgentActionError, TenantIsolationError) as sec_err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(sec_err))
