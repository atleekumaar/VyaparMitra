"""
Configuration loader and schema for VyaparMitra Phase 5 Hindi AI Business Copilot.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
import yaml

logger = logging.getLogger(__name__)

DEFAULT_COPILOT_CONFIG: Dict[str, Any] = {
    "copilot": {
        "default_language": "hinglish",
        "max_context_items": 20,
        "max_history_turns": 5,
        "default_merchant_id": "M001",
    },
    "llm": {
        "provider": "mock",
        "model": "gemini-1.5-flash",
        "temperature": 0.1,
        "max_tokens": 800,
        "api_key": None,
    },
    "retrieval": {
        "top_k": 5,
        "knowledge_dir": "data/knowledge",
        "data_dir": "data",
    },
    "validation": {
        "enabled": True,
        "strict_numeric_validation": True,
        "strict_entity_validation": True,
    },
    "fallback": {
        "enabled": True,
    },
}


@dataclass
class CopilotConfig:
    raw: Dict[str, Any] = field(default_factory=lambda: DEFAULT_COPILOT_CONFIG.copy())

    @property
    def default_language(self) -> str:
        return self.raw.get("copilot", {}).get("default_language", "hinglish")

    @property
    def default_merchant_id(self) -> Optional[str]:
        return self.raw.get("copilot", {}).get("default_merchant_id", "M001")

    @property
    def max_history_turns(self) -> int:
        return self.raw.get("copilot", {}).get("max_history_turns", 5)

    @property
    def llm_provider(self) -> str:
        return self.raw.get("llm", {}).get("provider", "mock")

    @property
    def llm_model(self) -> str:
        return self.raw.get("llm", {}).get("model", "gemini-1.5-flash")

    @property
    def llm_temperature(self) -> float:
        return float(self.raw.get("llm", {}).get("temperature", 0.1))

    @property
    def llm_api_key(self) -> Optional[str]:
        return self.raw.get("llm", {}).get("api_key")

    @property
    def knowledge_path(self) -> str:
        return self.raw.get("retrieval", {}).get("knowledge_dir", "data/knowledge")

    @property
    def data_dir(self) -> str:
        return self.raw.get("retrieval", {}).get("data_dir", "data")

    @property
    def validation_enforce_grounding(self) -> bool:
        return bool(self.raw.get("validation", {}).get("strict_numeric_validation", True))


def load_copilot_config(config_path: str = "configs/copilot.yaml") -> CopilotConfig:
    """Loads YAML configuration with fallback searching across paths, returning CopilotConfig."""
    candidates = [
        Path(config_path),
        Path("configs/copilot.yaml"),
        Path("config/copilot.yaml"),
    ]
    raw_dict = DEFAULT_COPILOT_CONFIG.copy()

    for p in candidates:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}
                merged = {**DEFAULT_COPILOT_CONFIG, **cfg}
                for section in ["copilot", "llm", "retrieval", "validation", "fallback"]:
                    if section in cfg and isinstance(cfg[section], dict):
                        merged[section] = {**DEFAULT_COPILOT_CONFIG.get(section, {}), **cfg[section]}
                raw_dict = merged
                break
            except Exception as e:
                logger.warning("Failed to parse %s: %s. Using default copilot config.", p, e)

    return CopilotConfig(raw=raw_dict)
