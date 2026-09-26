"""
Copilot Service Adapter for VyaparMitra Phase 6 API.
Integrates directly with the verified Phase 5 CopilotService without reimplementing any copilot logic.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from src.api.config import APIConfig, get_api_config
from src.api.schemas import CopilotAskRequest, CopilotAskResponse, CopilotDailyBriefResponse
from src.copilot.service import CopilotService


class CopilotServiceAdapter:
    """
    Adapter bridging Phase 6 FastAPI endpoints to the verified Phase 5 CopilotService.
    """

    _copilot_service_instance: Optional[CopilotService] = None

    def __init__(self, config: APIConfig | None = None) -> None:
        self.config = config or get_api_config()
        if CopilotServiceAdapter._copilot_service_instance is None:
            CopilotServiceAdapter._copilot_service_instance = CopilotService()
        self.service = CopilotServiceAdapter._copilot_service_instance

    def ask(self, request: CopilotAskRequest) -> CopilotAskResponse:
        """Invokes Phase 5 Copilot query pipeline and maps to typed response."""
        result_dict = self.service.query(
            session_id=request.session_id or "default_session",
            query=request.query,
            merchant_id=request.merchant_id or self.config.default_merchant_id,
            language=request.language,
        )

        validation_dict = result_dict.get("validation", {})
        val_status = "PASSED" if validation_dict.get("valid", True) else "FLAGGED"

        return CopilotAskResponse(
            answer=result_dict.get("answer", ""),
            intent=result_dict.get("intent", "UNKNOWN"),
            language=result_dict.get("language", "hinglish"),
            sources=result_dict.get("sources", []),
            evidence=result_dict.get("evidence", []),
            recommendations=result_dict.get("recommendations", []),
            confidence=result_dict.get("confidence", 0.95),
            validation_status=val_status,
            generated_at=result_dict.get("generated_at", ""),
        )

    def daily_brief(
        self,
        session_id: str = "default_session",
        merchant_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> CopilotDailyBriefResponse:
        """Invokes Phase 5 morning briefing generation."""
        result_dict = self.service.daily_brief(
            session_id=session_id,
            merchant_id=merchant_id or self.config.default_merchant_id,
            language=language,
        )

        validation_dict = result_dict.get("validation", {})
        val_status = "PASSED" if validation_dict.get("valid", True) else "FLAGGED"

        ask_resp = CopilotAskResponse(
            answer=result_dict.get("answer", ""),
            intent=result_dict.get("intent", "DAILY_ACTION_PLAN"),
            language=result_dict.get("language", "hinglish"),
            sources=result_dict.get("sources", []),
            evidence=result_dict.get("evidence", []),
            recommendations=result_dict.get("recommendations", []),
            confidence=result_dict.get("confidence", 0.95),
            validation_status=val_status,
            generated_at=result_dict.get("generated_at", ""),
        )

        return CopilotDailyBriefResponse(brief=ask_resp)

    def get_health(self) -> Dict[str, Any]:
        """Queries Copilot engine health."""
        return self.service.health_check()
