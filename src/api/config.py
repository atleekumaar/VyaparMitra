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


def _resolve_db_path() -> Path:
    explicit = os.getenv("DB_PATH")
    if explicit:
        return Path(explicit)
    if os.getenv("VERCEL"):
        import shutil
        tmp_db = Path("/tmp/vyaparmitra.db")
        if not tmp_db.exists():
            orig_db = Path("data/vyaparmitra.db")
            if orig_db.exists():
                try:
                    shutil.copy(orig_db, tmp_db)
                except Exception:
                    pass
        return tmp_db
    return Path("data/vyaparmitra.db")


def _resolve_cors_origins() -> List[str]:
    explicit = os.getenv("CORS_ORIGINS")
    if explicit:
        origins = [o.strip() for o in explicit.split(",") if o.strip()]
        # Wildcard * cannot be used with credentials in standard browser CORS
        return [o for o in origins if o != "*"]
    return [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://vyaparmitra.onrender.com",
        "https://atleekumaar.github.io",
    ]


def _resolve_demo_mode() -> bool:
    env_val = os.getenv("DEMO_MODE")
    if env_val is not None:
        return env_val.lower() in ("true", "1", "yes")
    app_env = os.getenv("APP_ENV", "development").lower()
    return app_env != "production"


def _resolve_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY")
    if secret:
        return secret
    app_env = os.getenv("APP_ENV", "development").lower()
    if app_env == "production":
        import secrets
        return secrets.token_hex(32)
    return "vyaparmitra-production-jwt-secret-key-32bytes-secure-2026"


@dataclass
class APIConfig:
    """Production-ready API settings loaded from environment or defaults."""
    app_env: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: int(os.getenv("PORT", os.getenv("API_PORT", "8000"))))
    cors_origins: List[str] = field(default_factory=_resolve_cors_origins)
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("DATA_DIR", "data")))
    db_path: Path = field(default_factory=_resolve_db_path)
    config_path: Path = field(default_factory=lambda: Path(os.getenv("CONFIG_PATH", "configs/config.yaml")))
    copilot_config_path: Path = field(default_factory=lambda: Path(os.getenv("COPILOT_CONFIG_PATH", "configs/copilot.yaml")))
    demo_mode: bool = field(default_factory=_resolve_demo_mode)
    default_merchant_id: str = field(default_factory=lambda: os.getenv("DEFAULT_MERCHANT_ID", "M001"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # Twilio Notification Configuration
    twilio_account_sid: str = field(default_factory=lambda: os.getenv("TWILIO_ACCOUNT_SID", ""))
    twilio_api_key_sid: str = field(default_factory=lambda: os.getenv("TWILIO_API_KEY_SID", ""))
    twilio_api_key_secret: str = field(default_factory=lambda: os.getenv("TWILIO_API_KEY_SECRET", ""))
    twilio_whatsapp_from: str = field(default_factory=lambda: os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"))
    twilio_sms_from: str = field(default_factory=lambda: os.getenv("TWILIO_SMS_FROM", "+14155238886"))

    # Authentication & Security
    jwt_secret_key: str = field(default_factory=_resolve_jwt_secret)
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_expire_minutes: int = field(default_factory=lambda: int(os.getenv("JWT_EXPIRE_MINUTES", "1440")))


_config_instance: APIConfig | None = None


def get_api_config() -> APIConfig:
    """Singleton getter for API configuration."""
    global _config_instance
    if _config_instance is None:
        _config_instance = APIConfig()
    return _config_instance
