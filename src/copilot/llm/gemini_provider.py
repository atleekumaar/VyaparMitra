"""
Google Gemini LLM provider for VyaparMitra Copilot.
Falls back to MockProvider when GEMINI_API_KEY is not configured or in offline mode.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from src.copilot.llm.base import LLMProvider
from src.copilot.llm.mock_provider import MockProvider
from src.copilot.schemas import BusinessContext

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """
    Google Gemini provider wrapper with automatic graceful fallback to MockProvider.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = model_name
        self.fallback = MockProvider()
        self._client = None

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model_name)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}. Falling back to MockProvider.")
                self._client = None

    def generate(
        self,
        prompt: str,
        context: BusinessContext,
        system_prompt: Optional[str] = None,
    ) -> str:
        if not self._client:
            return self.fallback.generate(prompt, context, system_prompt)

        try:
            full_prompt = f"{system_prompt}\n\nUser Question:\n{prompt}" if system_prompt else prompt
            response = self._client.generate_content(full_prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini API generation failed ({e}). Falling back to MockProvider.")

        return self.fallback.generate(prompt, context, system_prompt)
