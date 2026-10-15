"""Trip management API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def _auth_headers(client: TestClient, email: str = "tripper@example.com") -> dict[str, str]:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Trip Planner",
            "email": email,
            "password": "SecurePass1",
        },
    )
    assert register.status_code in {200, 201}, register.text
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_trip_crud_and_itinerary(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    headers = _auth_headers(client)

    places = client.get("/api/v1/places", params={"page_size": 5}).json()["data"]["items"]
    assert len(places) >= 2
    place_a = places[0]
    place_b = places[1]

    created = client.post(
        "/api/v1/trips",
        headers=headers,
        json={
            "title": "Hyderabad weekend",
            "origin_city": "Hyderabad",
            "destination_summary": "City highlights",
            "budget_inr": 8000,
            "status": "draft",
            "days": [
                {
                    "day_number": 1,
                    "title": "Arrival",
                    "places": [
                        {
                            "place_id": place_a["id"],
                            "time_slot": "Morning",
                            "sort_order": 0,
                        },
                    ],
                },
            ],
        },
    )
    assert created.status_code == 201, created.text
    trip = created.json()["data"]
    trip_id = trip["id"]
    assert trip["day_count"] == 1
    assert trip["stop_count"] == 1
    assert len(trip["days"][0]["places"]) == 1

    listed = client.get("/api/v1/trips", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == trip_id for item in listed.json()["data"])

    day_id = trip["days"][0]["id"]
    added = client.post(
        f"/api/v1/trips/{trip_id}/days/{day_id}/places",
        headers=headers,
        json={"place_id": place_b["id"], "time_slot": "Evening"},
    )
    assert added.status_code == 201, added.text
    assert added.json()["data"]["stop_count"] == 2
    assert len(added.json()["data"]["map_points"]) >= 1

    updated = client.patch(
        f"/api/v1/trips/{trip_id}",
        headers=headers,
        json={"status": "upcoming", "title": "Hyderabad long weekend"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["status"] == "upcoming"
    assert updated.json()["data"]["title"] == "Hyderabad long weekend"

    share = client.post(f"/api/v1/trips/{trip_id}/share", headers=headers)
    assert share.status_code == 200
    code = share.json()["data"]["share_code"]
    shared = client.get(f"/api/v1/trips/shared/{code}")
    assert shared.status_code == 200
    assert shared.json()["data"]["id"] == trip_id

    deleted = client.delete(f"/api/v1/trips/{trip_id}", headers=headers)
    assert deleted.status_code == 200
    missing = client.get(f"/api/v1/trips/{trip_id}", headers=headers)
    assert missing.status_code == 404


def test_trips_require_auth(client: TestClient) -> None:
    response = client.get("/api/v1/trips")
    assert response.status_code == 401
