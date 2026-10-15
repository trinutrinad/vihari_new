"""Activities API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def test_list_and_get_activities(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    listing = client.get("/api/v1/activities", params={"page_size": 20})
    assert listing.status_code == 200, listing.text
    payload = listing.json()["data"]
    assert payload["meta"]["total"] >= 4
    activity = payload["items"][0]
    assert activity["is_seed_data"] is True
    assert "category" in activity
    assert "price_inr" in activity

    detail = client.get(f"/api/v1/activities/{activity['id']}")
    assert detail.status_code == 200
    body = detail.json()["data"]
    assert body["id"] == activity["id"]
    assert "safety_information" in body
    assert "data_notice" in body

    by_slug = client.get(f"/api/v1/activities/by-slug/{activity['slug']}")
    assert by_slug.status_code == 200
    assert by_slug.json()["data"]["slug"] == activity["slug"]


def test_activity_filters_and_nearby(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    jaipur = client.get("/api/v1/activities", params={"city": "jaipur"})
    assert jaipur.status_code == 200
    assert jaipur.json()["data"]["meta"]["total"] >= 1

    adventure = client.get("/api/v1/activities", params={"category": "adventure"})
    assert adventure.status_code == 200
    assert adventure.json()["data"]["meta"]["total"] >= 1

    nearby = client.get(
        "/api/v1/activities/nearby",
        params={"lat": 26.9124, "lng": 75.7873, "radius_km": 100},
    )
    assert nearby.status_code == 200
    assert isinstance(nearby.json()["data"], list)
