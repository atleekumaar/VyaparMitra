"""
Main application factory for VyaparMitra Phase 6 REST API and Command Center.
"""

from __future__ import annotations

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.config import get_api_config
from src.api.middleware import RequestLoggingMiddleware, register_error_handlers
from src.api.routes import api_router

logger = logging.getLogger("vyaparmitra.api")


def create_app() -> FastAPI:
    """Creates and configures the production-ready FastAPI application."""
    config = get_api_config()

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    )

    app = FastAPI(
        title="VyaparMitra — AI Business Command Center API",
        description="Production-ready REST API connecting Phase 1 Data, Phase 2 Analytics, Phase 3 ML, Phase 4 Decisions, and Phase 5 Hindi Copilot.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 1. CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Performance & Request ID Middleware
    app.add_middleware(RequestLoggingMiddleware)

    # 3. Global Error Handlers (Envelope formatting)
    register_error_handlers(app)

    # 4. Register API Routes
    app.include_router(api_router)

    # 5. Static Frontend Serving (if built in frontend/dist)
    dist_dir = Path("frontend/dist")
    if dist_dir.exists() and (dist_dir / "index.html").exists():
        app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            if full_path.startswith("api/") or full_path == "api":
                raise HTTPException(status_code=404, detail="API endpoint not found")
            file_candidate = dist_dir / full_path
            if file_candidate.is_file():
                return FileResponse(file_candidate)
            return FileResponse(dist_dir / "index.html")
    else:
        @app.get("/", include_in_schema=False)
        def root():
            return {
                "product": "VyaparMitra",
                "descriptor": "AI Business Command Center",
                "status": "online",
                "version": "1.0.0",
                "api_docs": "/docs",
                "health": "/api/health",
                "demo_mode": config.demo_mode,
            }

    return app


app = create_app()
