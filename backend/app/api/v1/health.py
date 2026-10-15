"""Health and readiness endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.api.deps import DbSession
from app.core.config import get_settings
from app.schemas.common import ApiResponse, HealthData

router = APIRouter()
APP_VERSION = "0.1.0"


@router.get("/health", response_model=ApiResponse[HealthData])
def health_check() -> ApiResponse[HealthData]:
    """Liveness probe — process is up."""
    settings = get_settings()
    return ApiResponse(
        success=True,
        message="OK",
        data=HealthData(
            status="healthy",
            service=settings.app_name,
            environment=settings.app_env,
            timestamp=datetime.now(UTC),
            version=APP_VERSION,
            checks={"api": "ok"},
        ),
    )


@router.get("/health/ready", response_model=ApiResponse[HealthData])
def readiness_check(db: DbSession, response: Response) -> ApiResponse[HealthData]:
    """Readiness probe — database required; Redis reported as soft dependency."""
    settings = get_settings()
    checks: dict[str, str] = {}

    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error:{exc.__class__.__name__}"

    try:
        import redis

        client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=0.5)
        client.ping()
        checks["redis"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["redis"] = f"degraded:{exc.__class__.__name__}"

    db_ok = checks.get("database") == "ok"
    status_label = "ready" if db_ok else "not_ready"
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ApiResponse(
        success=db_ok,
        message="OK" if db_ok else "Dependency check failed",
        data=HealthData(
            status=status_label,
            service=settings.app_name,
            environment=settings.app_env,
            timestamp=datetime.now(UTC),
            version=APP_VERSION,
            checks=checks,
        ),
    )
