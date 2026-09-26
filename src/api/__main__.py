"""
CLI Runner to start VyaparMitra Phase 6 API Server.

Usage:
  python -m src.api
  python -m src.api --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import argparse
import uvicorn
from src.api.config import get_api_config


def main():
    config = get_api_config()
    parser = argparse.ArgumentParser(description="VyaparMitra Command Center API Server")
    parser.add_argument("--host", type=str, default=config.api_host, help="Host to bind")
    parser.add_argument("--port", type=int, default=config.api_port, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()
    print(f"Starting VyaparMitra API Server on http://{args.host}:{args.port}")
    uvicorn.run("src.api.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
