"""AI planner API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def _auth_headers(client: TestClient) -> dict[str, str]:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "AI Planner",
            "email": "ai.planner@example.com",
            "password": "SecurePass1",
        },
    )
    assert register.status_code in {200, 201}, register.text
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_plan_trip_preview_and_save(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    preview = client.post(
        "/api/v1/ai/plan-trip",
        json={
            "origin_city": "Hyderabad",
            "days": 3,
            "budget_inr": 10000,
            "interests": ["nature", "food"],
            "destination_hint": "Goa",
            "prompt": "peaceful nature and good food",
            "save": True,
        },
    )
    assert preview.status_code == 200, preview.text
    data = preview.json()["data"]
    assert data["provider"] == "mock"
    assert data["days"]
    assert data["trip"] is None
    assert "sign in" in data["notice"].lower() or "Sign in" in preview.json()["message"]

    headers = _auth_headers(client)
    saved = client.post(
        "/api/v1/ai/plan-trip",
        headers=headers,
        json={
            "origin_city": "Hyderabad",
            "days": 3,
            "budget_inr": 10000,
            "interests": ["beach", "food"],
            "destination_hint": "Goa",
            "save": True,
        },
    )
    assert saved.status_code == 200, saved.text
    body = saved.json()["data"]
    assert body["trip"] is not None
    assert body["trip"]["is_ai_generated"] is True
    assert body["trip"]["day_count"] == 3
    assert body["conversation_id"]


def test_ai_chat(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Help me plan a weekend trip"},
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["reply"]
    assert data["provider"] == "mock"
    assert data["conversation_id"]


def test_ai_agents_catalog_and_trace(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    catalog = client.get("/api/v1/ai/agents")
    assert catalog.status_code == 200
    agents = catalog.json()["data"]
    names = {item["name"] for item in agents}
    assert {"destination", "hotel", "food", "guide", "budget", "planner"} <= names

    planned = client.post(
        "/api/v1/ai/plan-trip",
        json={
            "origin_city": "Hyderabad",
            "days": 2,
            "interests": ["heritage"],
            "destination_hint": "Jaipur",
            "save": False,
        },
    )
    assert planned.status_code == 200, planned.text
    data = planned.json()["data"]
    trace_names = [item["agent"] for item in data["agent_trace"]]
    assert "destination" in trace_names
    assert "planner" in trace_names
    assert data.get("weather") is not None
    assert data.get("safety") is not None
    assert data.get("booking") is not None
    assert data["booking"]["available"] is True
