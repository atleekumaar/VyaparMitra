"""
Base abstract interface for VyaparMitra Copilot LLM providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.copilot.schemas import BusinessContext


class LLMProvider(ABC):
    """Abstract LLM Provider interface."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        context: BusinessContext,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generates a natural language response grounded in BusinessContext.
        """
        raise NotImplementedError
