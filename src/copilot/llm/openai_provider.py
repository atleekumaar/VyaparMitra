"""
OpenAI LLM provider for VyaparMitra Copilot.
Falls back to MockProvider when OPENAI_API_KEY is not configured or in offline mode.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from src.copilot.llm.base import LLMProvider
from src.copilot.llm.mock_provider import MockProvider
from src.copilot.schemas import BusinessContext

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    OpenAI provider wrapper with automatic graceful fallback to MockProvider.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name
        self.fallback = MockProvider()
        self._client = None

        if self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}. Falling back to MockProvider.")
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
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = self._client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1,
            )
            choice = resp.choices[0].message.content
            if choice:
                return choice.strip()
        except Exception as e:
            logger.warning(f"OpenAI API generation failed ({e}). Falling back to MockProvider.")

        return self.fallback.generate(prompt, context, system_prompt)
