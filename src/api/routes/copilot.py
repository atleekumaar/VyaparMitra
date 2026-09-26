"""
Copilot routes for VyaparMitra Phase 6 API.
Interfaces with Phase 5 CopilotService for multilingual question answering and morning briefs.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Query
from src.api.schemas import CopilotAskRequest, CopilotAskResponse, CopilotDailyBriefResponse
from src.api.services.copilot_service_adapter import CopilotServiceAdapter

router = APIRouter(prefix="/copilot", tags=["Copilot"])
adapter = CopilotServiceAdapter()


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
