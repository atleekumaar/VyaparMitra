"""
Groq LLM provider for VyaparMitra Copilot.
Ultra-fast inference using LLaMA-3.3 models on Groq LPUs.
Falls back to MockProvider when GROQ_API_KEY is missing or in offline mode.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from src.copilot.llm.base import LLMProvider
from src.copilot.llm.mock_provider import MockProvider
from src.copilot.schemas import BusinessContext

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """
    Groq provider with automatic fallback to MockProvider.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "qwen/qwen3.8-27b",
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model_name = model_name or os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        self.fallback = MockProvider()
        self._client = None

        if self.api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
                logger.info(f"Initialized GroqProvider with model={self.model_name}")
            except Exception as e:
                logger.warning(
                    f"Could not initialize Groq client: {e}. Falling back to MockProvider."
                )
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
                max_tokens=800,
            )
            choice = resp.choices[0].message.content
            if choice:
                return choice.strip()
            return self.fallback.generate(prompt, context, system_prompt)
        except Exception as e:
            logger.warning(
                f"Groq generation failed ({e}). Falling back to MockProvider."
            )
            return self.fallback.generate(prompt, context, system_prompt)
