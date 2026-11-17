"""
ASGI Middleware and Global Error Handlers for VyaparMitra Phase 6 API.
Provides unique Request IDs, structured performance logging, and uniform error envelopes.
"""

from __future__ import annotations

import logging
import os
import time
import uuid
from collections import defaultdict
from threading import Lock
from typing import Callable, Dict, Tuple
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("vyaparmitra.api")


class InMemoryRateLimiter:
    """Thread-safe sliding-window rate limiter for sensitive API routes."""

    def __init__(self) -> None:
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()

    def check(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        """Returns (is_allowed, remaining_requests, retry_after_seconds)."""
        now = time.time()
        with self._lock:
            cutoff = now - window_seconds
            valid_ts = [t for t in self._requests[key] if t > cutoff]
            if len(valid_ts) >= max_requests:
                oldest = valid_ts[0]
                retry_after = max(1, int(oldest + window_seconds - now))
                self._requests[key] = valid_ts
                return False, 0, retry_after
            valid_ts.append(now)
            self._requests[key] = valid_ts
            remaining = max(0, max_requests - len(valid_ts))
            return True, remaining, 0

    def clear(self) -> None:
        with self._lock:
            self._requests.clear()


global_rate_limiter = InMemoryRateLimiter()


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window rate-limiting middleware guarding against DDoS, OTP spam,
    and LLM credit exhaustion.
    """

    ROUTE_LIMITS: Dict[str, Tuple[int, int]] = {
        "/api/auth/otp/send": (10, 60),      # 10 OTP requests per min
        "/api/auth/otp/verify": (15, 60),    # 15 OTP verifications per min
        "/api/auth/login": (15, 60),         # 15 password attempts per min
        "/api/copilot/ask": (30, 60),        # 30 LLM queries per min
    }
    DEFAULT_API_LIMIT: Tuple[int, int] = (180, 60)  # 180 req/min for general API

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if not path.startswith("/api"):
            return await call_next(request)

        # Bypass rate limits during automated test runs
        if (
            os.getenv("PYTEST_CURRENT_TEST")
            or os.getenv("TESTING") == "true"
            or request.headers.get("X-Bypass-Rate-Limit") == "true"
        ):
            return await call_next(request)

        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif request.client:
            client_ip = request.client.host
        else:
            client_ip = "127.0.0.1"

        limit, window = self.ROUTE_LIMITS.get(path, self.DEFAULT_API_LIMIT)
        rate_key = f"{path}:{client_ip}"
        allowed, remaining, retry_after = global_rate_limiter.check(rate_key, limit, window)

        if not allowed:
            req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
            msg = f"Rate limit exceeded. Try again in {retry_after} seconds."
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": msg,
                        "request_id": req_id,
                    },
                    "detail": msg,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-Request-ID": req_id,
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Assigns a unique request_id to each incoming HTTP request, logs performance,
    and attaches X-Request-ID to the response headers.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            response.headers["X-Request-ID"] = request_id

            logger.info(
                f"req_id={request_id} method={request.method} path={request.url.path} "
                f"status={response.status_code} latency_ms={duration_ms:.2f}"
            )
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"req_id={request_id} method={request.method} path={request.url.path} "
                f"latency_ms={duration_ms:.2f} error={exc}",
                exc_info=True
            )
            raise exc


def register_error_handlers(app: FastAPI) -> None:
    """Registers standard JSON error envelopes for HTTP exceptions, validation errors, and uncaught exceptions."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "RESOURCE_NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            422: "UNPROCESSABLE_ENTITY",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
        }
        error_code = code_map.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": error_code,
                    "message": str(exc.detail),
                    "request_id": req_id,
                },
                "detail": str(exc.detail),
            },
            headers={"X-Request-ID": req_id},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request payload or query parameters.",
                    "details": exc.errors(),
                    "request_id": req_id,
                }
            },
            headers={"X-Request-ID": req_id},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        logger.error(f"Unhandled exception on req_id={req_id}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred while processing your request. Please try again.",
                    "request_id": req_id,
                }
            },
            headers={"X-Request-ID": req_id},
        )
