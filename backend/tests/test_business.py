"""Business dashboard API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import DEMO_OWNER_EMAIL, DEMO_OWNER_PASSWORD, seed_all


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


def _owner_headers(client: TestClient) -> dict[str, str]:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": DEMO_OWNER_EMAIL, "password": DEMO_OWNER_PASSWORD},
    )
    assert login.status_code == 200, login.text
    token = login.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_business_access_and_summary(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    unauth = client.get("/api/v1/business/access")
    assert unauth.status_code == 401

    traveller = _auth_headers(client, "biz-traveller@example.com")
    access = client.get("/api/v1/business/access", headers=traveller)
    assert access.status_code == 200
    assert access.json()["data"]["has_access"] is False

    forbidden = client.get("/api/v1/business/summary", headers=traveller)
    assert forbidden.status_code == 403

    owner = _owner_headers(client)
    owner_access = client.get("/api/v1/business/access", headers=owner)
    assert owner_access.status_code == 200
    body = owner_access.json()["data"]
    assert body["has_access"] is True
    assert body["hotels_count"] >= 1
    assert body["restaurants_count"] >= 1
    assert body["guides_count"] >= 1

    summary = client.get("/api/v1/business/summary", headers=owner)
    assert summary.status_code == 200
    data = summary.json()["data"]
    assert data["hotels_count"] >= 1
    assert "revenue_captured_inr" in data

    properties = client.get("/api/v1/business/properties", headers=owner)
    assert properties.status_code == 200
    items = properties.json()["data"]
    assert any(item["resource_type"] == "hotel" for item in items)
    assert any(item["resource_type"] == "restaurant" for item in items)
    assert any(item["resource_type"] == "guide" for item in items)


def test_business_bookings_for_owned_resources(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_all(db_session, force=True)
    owner = _owner_headers(client)
    props = client.get("/api/v1/business/properties", headers=owner).json()["data"]
    hotel = next(item for item in props if item["resource_type"] == "hotel")

    traveller = _auth_headers(client, "biz-booker@example.com")
    booked = client.post(
        "/api/v1/bookings",
        headers=traveller,
        json={"resource_type": "hotel", "resource_id": hotel["id"], "nights": 1},
    )
    assert booked.status_code == 201, booked.text
    booking_number = booked.json()["data"]["booking_number"]

    owned = client.get("/api/v1/business/bookings", headers=owner)
    assert owned.status_code == 200
    numbers = {item["booking_number"] for item in owned.json()["data"]}
    assert booking_number in numbers

    summary = client.get("/api/v1/business/summary", headers=owner)
    assert summary.json()["data"]["bookings_total"] >= 1
