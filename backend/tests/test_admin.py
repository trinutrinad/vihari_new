"""Admin dashboard API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD, seed_all


def _auth_headers(client: TestClient, email: str, password: str = "SecurePass1") -> dict[str, str]:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Regular Traveller",
            "email": email,
            "password": password,
        },
    )
    assert register.status_code in {200, 201}, register.text
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _admin_headers(client: TestClient) -> dict[str, str]:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": DEMO_ADMIN_EMAIL, "password": DEMO_ADMIN_PASSWORD},
    )
    assert login.status_code == 200, login.text
    token = login.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_access_summary_and_lists(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    unauth = client.get("/api/v1/admin/access")
    assert unauth.status_code == 401

    traveller = _auth_headers(client, "admin-traveller@example.com")
    access = client.get("/api/v1/admin/access", headers=traveller)
    assert access.status_code == 200
    assert access.json()["data"]["has_access"] is False

    forbidden = client.get("/api/v1/admin/summary", headers=traveller)
    assert forbidden.status_code == 403

    admin = _admin_headers(client)
    admin_access = client.get("/api/v1/admin/access", headers=admin)
    assert admin_access.status_code == 200
    assert admin_access.json()["data"]["has_access"] is True
    assert "ADMIN" in admin_access.json()["data"]["roles"]

    summary = client.get("/api/v1/admin/summary", headers=admin)
    assert summary.status_code == 200
    data = summary.json()["data"]
    assert data["users_total"] >= 3
    assert data["places_total"] >= 1
    assert data["hotels_total"] >= 1
    assert "revenue_captured_inr" in data

    users = client.get("/api/v1/admin/users", headers=admin)
    assert users.status_code == 200
    assert any(item["email"] == DEMO_ADMIN_EMAIL for item in users.json()["data"])

    bookings = client.get("/api/v1/admin/bookings", headers=admin)
    assert bookings.status_code == 200

    payments = client.get("/api/v1/admin/payments", headers=admin)
    assert payments.status_code == 200

    tickets = client.get("/api/v1/admin/tickets", headers=admin)
    assert tickets.status_code == 200


def test_admin_sees_platform_booking(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    traveller = _auth_headers(client, "admin-booker@example.com")
    hotels = client.get("/api/v1/hotels", params={"page_size": 1}).json()["data"]["items"]
    assert hotels

    booked = client.post(
        "/api/v1/bookings",
        headers=traveller,
        json={"resource_type": "hotel", "resource_id": hotels[0]["id"], "nights": 1},
    )
    assert booked.status_code == 201, booked.text
    booking_number = booked.json()["data"]["booking_number"]

    admin = _admin_headers(client)
    listed = client.get("/api/v1/admin/bookings", headers=admin)
    assert listed.status_code == 200
    numbers = {item["booking_number"] for item in listed.json()["data"]}
    assert booking_number in numbers

    summary = client.get("/api/v1/admin/summary", headers=admin)
    assert summary.json()["data"]["bookings_total"] >= 1
