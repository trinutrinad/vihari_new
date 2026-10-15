"""Restaurants API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def test_list_and_get_restaurants(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    listing = client.get("/api/v1/restaurants", params={"page_size": 20})
    assert listing.status_code == 200, listing.text
    payload = listing.json()["data"]
    assert payload["meta"]["total"] >= 3
    restaurant = payload["items"][0]
    assert restaurant["is_seed_data"] is True
    assert "cuisine_tags" in restaurant

    detail = client.get(f"/api/v1/restaurants/{restaurant['id']}")
    assert detail.status_code == 200
    body = detail.json()["data"]
    assert body["id"] == restaurant["id"]
    assert body["menu_items"]
    assert "data_notice" in body

    by_slug = client.get(f"/api/v1/restaurants/by-slug/{restaurant['slug']}")
    assert by_slug.status_code == 200
    assert by_slug.json()["data"]["slug"] == restaurant["slug"]


def test_restaurant_filters_and_nearby(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    hyderabad = client.get("/api/v1/restaurants", params={"city": "hyderabad"})
    assert hyderabad.status_code == 200
    assert hyderabad.json()["data"]["meta"]["total"] >= 1

    veg = client.get("/api/v1/restaurants", params={"vegetarian": True})
    assert veg.status_code == 200
    assert all(item["is_vegetarian"] for item in veg.json()["data"]["items"])

    cuisine = client.get("/api/v1/restaurants", params={"cuisine": "Hyderabadi"})
    assert cuisine.status_code == 200
    assert cuisine.json()["data"]["meta"]["total"] >= 1

    nearby = client.get(
        "/api/v1/restaurants/nearby",
        params={"lat": 17.385, "lng": 78.486, "radius_km": 80},
    )
    assert nearby.status_code == 200
    assert isinstance(nearby.json()["data"], list)
