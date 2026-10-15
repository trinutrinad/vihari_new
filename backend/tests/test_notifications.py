"""Notifications API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def _auth_headers(client: TestClient, email: str) -> dict[str, str]:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Notify User",
            "email": email,
            "password": "SecurePass1",
        },
    )
    assert register.status_code in {200, 201}, register.text
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_notifications_demo_list_read(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    headers = _auth_headers(client, "notify1@example.com")

    unauth = client.get("/api/v1/notifications")
    assert unauth.status_code == 401

    created = client.post(
        "/api/v1/notifications/demo",
        headers=headers,
        json={"title": "Hello", "body": "Demo body", "category": "system"},
    )
    assert created.status_code == 201, created.text
    note = created.json()["data"]
    assert note["is_read"] is False

    listed = client.get("/api/v1/notifications", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == note["id"] for item in listed.json()["data"])

    count = client.get("/api/v1/notifications/unread-count", headers=headers)
    assert count.status_code == 200
    assert count.json()["data"]["unread_count"] >= 1

    marked = client.post(
        f"/api/v1/notifications/{note['id']}/read",
        headers=headers,
    )
    assert marked.status_code == 200
    assert marked.json()["data"]["is_read"] is True

    client.post(
        "/api/v1/notifications/demo",
        headers=headers,
        json={"title": "Second", "body": "Another"},
    )
    all_read = client.post("/api/v1/notifications/read-all", headers=headers)
    assert all_read.status_code == 200
    assert all_read.json()["data"]["unread_count"] == 0


def test_booking_emits_notification(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    headers = _auth_headers(client, "notify2@example.com")
    hotels = client.get("/api/v1/hotels", params={"page_size": 1}).json()["data"]["items"]
    assert hotels

    booked = client.post(
        "/api/v1/bookings",
        headers=headers,
        json={"resource_type": "hotel", "resource_id": hotels[0]["id"], "nights": 1},
    )
    assert booked.status_code == 201, booked.text

    notes = client.get("/api/v1/notifications", headers=headers)
    assert notes.status_code == 200
    assert any(item["category"] == "booking" for item in notes.json()["data"])
