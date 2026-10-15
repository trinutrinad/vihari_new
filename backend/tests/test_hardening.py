"""Production hardening tests (Phase 25)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import DEFAULT_INSECURE_SECRET, Settings, get_settings
from app.core.rate_limit import rate_limiter
from app.main import app


@pytest.fixture(autouse=True)
def _reset_rate_limiter() -> None:
    rate_limiter.reset()
    yield
    rate_limiter.reset()


def test_security_headers_present() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert "no-store" in (response.headers.get("Cache-Control") or "")


def test_readiness_endpoint(client: TestClient, db_session: Session) -> None:
    _ = db_session
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "ready"
    assert payload["data"]["checks"]["database"] == "ok"
    assert "redis" in payload["data"]["checks"]


def test_auth_rate_limit_returns_429(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = db_session
    monkeypatch.setenv("RATE_LIMIT_AUTH_PER_MINUTE", "3")
    get_settings.cache_clear()
    assert get_settings().rate_limit_auth_per_minute == 3

    rate_limiter.reset()
    saw_429 = False
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrong-password"},
        )
        if response.status_code == 429:
            saw_429 = True
            assert response.json()["error"]["code"] == "rate_limited"
            assert response.headers.get("Retry-After") == "60"
            break
        # Wrong credentials should be 401 before hitting the limit.
        assert response.status_code in {401, 422}
    assert saw_429

    monkeypatch.delenv("RATE_LIMIT_AUTH_PER_MINUTE", raising=False)
    get_settings.cache_clear()


def test_production_secret_validation() -> None:
    insecure = Settings(
        APP_ENV="production",
        DEBUG="false",
        SECRET_KEY=DEFAULT_INSECURE_SECRET,
        OTP_DEBUG_EXPOSE_CODE="false",
    )
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        insecure.validate_for_runtime()

    secure = Settings(
        APP_ENV="production",
        DEBUG="false",
        SECRET_KEY="x" * 40,
        OTP_DEBUG_EXPOSE_CODE="false",
    )
    secure.validate_for_runtime()


def test_otp_debug_never_outside_debug() -> None:
    settings = Settings(DEBUG="false", OTP_DEBUG_EXPOSE_CODE="true")
    assert settings.expose_otp_debug_code is False
