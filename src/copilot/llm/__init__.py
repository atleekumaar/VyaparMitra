"""
LLM Provider package and factory for VyaparMitra Copilot.
"""

from typing import Optional

from src.copilot.config import CopilotConfig, load_copilot_config
from src.copilot.llm.base import LLMProvider
from src.copilot.llm.gemini_provider import GeminiProvider
from src.copilot.llm.groq_provider import GroqProvider
from src.copilot.llm.mock_provider import MockProvider
from src.copilot.llm.openai_provider import OpenAIProvider
import os


def get_llm_provider(config: Optional[CopilotConfig] = None) -> LLMProvider:
    """
    Factory creating the configured LLMProvider instance.
    Supports Groq, Gemini, OpenAI, and falls back to MockProvider for offline mode.
    """
    cfg = config or load_copilot_config()
    provider_name = cfg.llm_provider.lower().strip()

    # If groq key is set in env or config
    groq_key = os.getenv("GROQ_API_KEY") or (cfg.llm_api_key if provider_name == "groq" else None)
    if provider_name == "groq" or (groq_key and provider_name in ("mock", "default", "groq")):
        return GroqProvider(api_key=groq_key, model_name=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"))

    if provider_name == "gemini":
        return GeminiProvider(api_key=cfg.llm_api_key, model_name=cfg.llm_model)
    elif provider_name == "openai":
        return OpenAIProvider(api_key=cfg.llm_api_key, model_name=cfg.llm_model)
    else:
        return MockProvider()


__all__ = [
    "LLMProvider",
    "MockProvider",
    "GeminiProvider",
    "GroqProvider",
    "OpenAIProvider",
    "get_llm_provider",
]
