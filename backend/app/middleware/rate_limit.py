"""Auth endpoint rate limiting middleware."""

from __future__ import annotations

from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.rate_limit import rate_limiter

AUTH_RATE_LIMITED_SUFFIXES = (
    "/auth/login",
    "/auth/register",
    "/auth/phone/request-otp",
    "/auth/phone/verify-otp",
    "/auth/forgot-password",
    "/auth/reset-password",
    "/auth/refresh",
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
        if not settings.rate_limit_enabled or request.method.upper() == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        if not any(path.endswith(suffix) for suffix in AUTH_RATE_LIMITED_SUFFIXES):
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        key = f"auth:{client}:{path}"
        allowed, remaining = rate_limiter.allow(
            key,
            limit=settings.rate_limit_auth_per_minute,
            window_seconds=60,
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "rate_limited",
                        "message": "Too many authentication attempts. Try again shortly.",
                        "details": None,
                    },
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(settings.rate_limit_auth_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_auth_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
