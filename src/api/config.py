"""
Configuration module for VyaparMitra Phase 6 Backend API.
Loads environment variables and fallback YAML configurations safely.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


def _load_env_file():
    """Lightweight .env loader that populates os.environ without requiring external packages."""
    env_path = Path(".env")
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, val = line.partition("=")
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key and key not in os.environ:
                            os.environ[key] = val
        except Exception:
            pass


_load_env_file()


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
    db_path: Path = field(default_factory=lambda: Path(os.getenv("DB_PATH", "data/vyaparmitra.db")))
    config_path: Path = field(default_factory=lambda: Path(os.getenv("CONFIG_PATH", "configs/config.yaml")))
    copilot_config_path: Path = field(default_factory=lambda: Path(os.getenv("COPILOT_CONFIG_PATH", "configs/copilot.yaml")))
    demo_mode: bool = field(default_factory=lambda: os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes"))
    default_merchant_id: str = field(default_factory=lambda: os.getenv("DEFAULT_MERCHANT_ID", "M001"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Twilio Notification Configuration
    twilio_account_sid: str = field(default_factory=lambda: os.getenv("TWILIO_ACCOUNT_SID", ""))
    twilio_api_key_sid: str = field(default_factory=lambda: os.getenv("TWILIO_API_KEY_SID", ""))
    twilio_api_key_secret: str = field(default_factory=lambda: os.getenv("TWILIO_API_KEY_SECRET", ""))
    twilio_whatsapp_from: str = field(default_factory=lambda: os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"))
    twilio_sms_from: str = field(default_factory=lambda: os.getenv("TWILIO_SMS_FROM", "+14155238886"))


_config_instance: APIConfig | None = None


def get_api_config() -> APIConfig:
    """Singleton getter for API configuration."""
    global _config_instance
    if _config_instance is None:
        _config_instance = APIConfig()
    return _config_instance
