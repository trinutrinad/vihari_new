"""Bookings API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def _auth_headers(client: TestClient, email: str = "booker@example.com") -> dict[str, str]:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Demo Booker",
            "email": email,
            "password": "SecurePass1",
        },
    )
    assert register.status_code in {200, 201}, register.text
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_booking_create_list_cancel(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    headers = _auth_headers(client)

    hotels = client.get("/api/v1/hotels", params={"page_size": 5}).json()["data"]["items"]
    assert hotels
    hotel = hotels[0]

    created = client.post(
        "/api/v1/bookings",
        headers=headers,
        json={
            "resource_type": "hotel",
            "resource_id": hotel["id"],
            "nights": 2,
        },
    )
    assert created.status_code == 201, created.text
    booking = created.json()["data"]
    assert booking["status"] == "confirmed"
    assert booking["is_mock"] is True
    assert booking["amount_inr"] > 0
    assert booking["resource_title"]

    listed = client.get("/api/v1/bookings", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == booking["id"] for item in listed.json()["data"])

    detail = client.get(f"/api/v1/bookings/{booking['id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["booking_number"] == booking["booking_number"]

    cancelled = client.post(
        f"/api/v1/bookings/{booking['id']}/cancel",
        headers=headers,
        json={"reason": "Changed plans"},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["data"]["status"] == "cancelled"


def test_booking_requires_auth_and_supports_types(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_all(db_session, force=True)

    unauth = client.get("/api/v1/bookings")
    assert unauth.status_code == 401

    headers = _auth_headers(client, email="booker2@example.com")
    guides = client.get("/api/v1/guides", params={"page_size": 1}).json()["data"]["items"]
    activities = client.get("/api/v1/activities", params={"page_size": 1}).json()["data"][
        "items"
    ]
    transport = client.get("/api/v1/transport", params={"page_size": 1}).json()["data"][
        "items"
    ]
    restaurants = client.get("/api/v1/restaurants", params={"page_size": 1}).json()[
        "data"
    ]["items"]

    for resource_type, resource_id, extra in [
        ("guide", guides[0]["id"], {"duration_days": 1}),
        ("activity", activities[0]["id"], {"participants": 2}),
        ("transport", transport[0]["id"], {"distance_km": 8}),
        ("restaurant", restaurants[0]["id"], {}),
    ]:
        response = client.post(
            "/api/v1/bookings",
            headers=headers,
            json={"resource_type": resource_type, "resource_id": resource_id, **extra},
        )
        assert response.status_code == 201, response.text
        assert response.json()["data"]["resource_type"] == resource_type
