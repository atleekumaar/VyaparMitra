"""
Configuration module for VyaparMitra Phase 6 Backend API.
Loads environment variables and fallback YAML configurations safely.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class APIConfig:
    """Production-ready API settings loaded from environment or defaults."""
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    cors_origins: List[str] = field(default_factory=lambda: [
        origin.strip() for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,*"
        ).split(",") if origin.strip()
    ])
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("DATA_DIR", "data")))
    config_path: Path = field(default_factory=lambda: Path(os.getenv("CONFIG_PATH", "configs/config.yaml")))
    copilot_config_path: Path = field(default_factory=lambda: Path(os.getenv("COPILOT_CONFIG_PATH", "configs/copilot.yaml")))
    demo_mode: bool = field(default_factory=lambda: os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes"))
    default_merchant_id: str = field(default_factory=lambda: os.getenv("DEFAULT_MERCHANT_ID", "M001"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


_config_instance: APIConfig | None = None


def get_api_config() -> APIConfig:
    """Singleton getter for API configuration."""
    global _config_instance
    if _config_instance is None:
        _config_instance = APIConfig()
    return _config_instance
