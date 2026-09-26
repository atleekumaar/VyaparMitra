"""
LLM Provider package and factory for VyaparMitra Copilot.
"""

from typing import Optional

from src.copilot.config import CopilotConfig, load_copilot_config
from src.copilot.llm.base import LLMProvider
from src.copilot.llm.gemini_provider import GeminiProvider
from src.copilot.llm.mock_provider import MockProvider
from src.copilot.llm.openai_provider import OpenAIProvider


def get_llm_provider(config: Optional[CopilotConfig] = None) -> LLMProvider:
    """
    Factory creating the configured LLMProvider instance.
    Defaults to MockProvider for offline, deterministic, zero-key environments.
    """
    cfg = config or load_copilot_config()
    provider_name = cfg.llm_provider.lower().strip()

    if provider_name == "gemini":
        return GeminiProvider(api_key=cfg.llm_api_key, model_name=cfg.llm_model)
    elif provider_name == "openai":
        return OpenAIProvider(api_key=cfg.llm_api_key, model_name=cfg.llm_model)
    else:
        return MockProvider()


__all__ = ["LLMProvider", "MockProvider", "GeminiProvider", "OpenAIProvider", "get_llm_provider"]
