"""Hotels API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def test_list_and_get_hotels(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    listing = client.get("/api/v1/hotels", params={"page_size": 20})
    assert listing.status_code == 200, listing.text
    payload = listing.json()["data"]
    assert payload["meta"]["total"] >= 3
    hotel = payload["items"][0]
    assert hotel["is_seed_data"] is True
    assert "starting_price_inr" in hotel

    detail = client.get(f"/api/v1/hotels/{hotel['id']}")
    assert detail.status_code == 200
    body = detail.json()["data"]
    assert body["id"] == hotel["id"]
    assert body["rooms"]
    assert "data_notice" in body

    by_slug = client.get(f"/api/v1/hotels/by-slug/{hotel['slug']}")
    assert by_slug.status_code == 200
    assert by_slug.json()["data"]["slug"] == hotel["slug"]


def test_hotel_filters_and_nearby(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    hyderabad = client.get("/api/v1/hotels", params={"city": "hyderabad"})
    assert hyderabad.status_code == 200
    assert hyderabad.json()["data"]["meta"]["total"] >= 1

    wifi = client.get("/api/v1/hotels", params={"wifi": True, "breakfast": True})
    assert wifi.status_code == 200
    assert all(item["has_wifi"] for item in wifi.json()["data"]["items"])

    nearby = client.get(
        "/api/v1/hotels/nearby",
        params={"lat": 17.385, "lng": 78.486, "radius_km": 80},
    )
    assert nearby.status_code == 200
    assert isinstance(nearby.json()["data"], list)
