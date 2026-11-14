"""
VyaparMitra Phase 6 — Production-Ready Merchant Command Center & API.
"""

from src.api.config import APIConfig, get_api_config


def __getattr__(name: str):
    if name in ("app", "create_app"):
        from src.api.main import app, create_app
        return app if name == "app" else create_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["app", "create_app", "APIConfig", "get_api_config"]

