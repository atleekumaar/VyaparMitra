"""
Service layer for VyaparMitra Copilot.
Manages multi-session copilot instances and provides clean entry points for Phase 6 API or UI integration.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.copilot.config import CopilotConfig, load_copilot_config
from src.copilot.copilot import VyaparMitraCopilot
from src.copilot.schemas import Language


class CopilotService:
    """
    Stateful service coordinator managing active merchant sessions and queries.
    """

    def __init__(self, config: Optional[CopilotConfig] = None):
        self.config = config or load_copilot_config()
        self._sessions: Dict[str, VyaparMitraCopilot] = {}

    def get_or_create_copilot(
        self,
        session_id: str = "default_session",
        merchant_id: Optional[str] = None,
    ) -> VyaparMitraCopilot:
        """Retrieves or instantiates a copilot session for a given session ID."""
        if session_id not in self._sessions:
            copilot = VyaparMitraCopilot(
                config=self.config,
                session_id=session_id,
                merchant_id=merchant_id or self.config.default_merchant_id,
            )
            self._sessions[session_id] = copilot
        return self._sessions[session_id]

    def query(
        self,
        session_id: str,
        query: str,
        merchant_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Processes a merchant query within a session."""
        copilot = self.get_or_create_copilot(session_id=session_id, merchant_id=merchant_id)
        lang_enum = Language(language.lower()) if language else None
        response = copilot.ask(query=query, merchant_id=merchant_id, language_override=lang_enum)
        return response.model_dump()

    def daily_brief(
        self,
        session_id: str,
        merchant_id: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generates a daily brief for the merchant session."""
        copilot = self.get_or_create_copilot(session_id=session_id, merchant_id=merchant_id)
        lang_enum = Language(language.lower()) if language else None
        response = copilot.generate_daily_brief(merchant_id=merchant_id, language=lang_enum)
        return response.model_dump()

    def clear_session(self, session_id: str) -> bool:
        """Clears memory for a session."""
        if session_id in self._sessions:
            self._sessions[session_id].state.clear()
            del self._sessions[session_id]
            return True
        return False

    def health_check(self) -> Dict[str, Any]:
        """Returns copilot engine health status and active sessions."""
        return {
            "status": "healthy",
            "provider": self.config.llm_provider,
            "default_language": self.config.default_language,
            "active_sessions": len(self._sessions),
        }
