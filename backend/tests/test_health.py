"""Health endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "healthy"
    assert payload["data"]["service"] == "Bharat Yatra"
    assert "X-Request-ID" in response.headers


def test_health_preserves_incoming_request_id() -> None:
    response = client.get("/api/v1/health", headers={"X-Request-ID": "test-req-123"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-req-123"


def test_openapi_available_in_debug() -> None:
    response = client.get("/docs")
    assert response.status_code == 200
