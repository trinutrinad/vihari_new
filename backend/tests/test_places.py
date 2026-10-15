"""Tourist places API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def test_list_and_get_places(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    listing = client.get("/api/v1/places", params={"page_size": 10})
    assert listing.status_code == 200, listing.text
    payload = listing.json()["data"]
    assert payload["meta"]["total"] >= 10
    assert len(payload["items"]) >= 1
    place = payload["items"][0]
    assert "password_hash" not in place
    assert place["is_seed_data"] is True
    assert place["provenance"] == "seed_demo"

    detail = client.get(f"/api/v1/places/{place['id']}")
    assert detail.status_code == 200
    body = detail.json()["data"]
    assert body["id"] == place["id"]
    assert "data_notice" in body
    assert body["nearby_amenities"]
    assert all(item["provenance"] == "unverified" for item in body["nearby_amenities"])

    by_slug = client.get(f"/api/v1/places/by-slug/{place['slug']}")
    assert by_slug.status_code == 200
    assert by_slug.json()["data"]["slug"] == place["slug"]


def test_places_filters_and_nearby(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    categories = client.get("/api/v1/places/categories")
    assert categories.status_code == 200
    assert len(categories.json()["data"]) >= 5

    featured = client.get("/api/v1/places", params={"featured": True})
    assert featured.status_code == 200
    assert all(item["is_featured"] for item in featured.json()["data"]["items"])

    temple = client.get("/api/v1/places", params={"category": "temple"})
    assert temple.status_code == 200
    assert temple.json()["data"]["meta"]["total"] >= 1

    # Hyderabad-ish coordinates
    nearby = client.get(
        "/api/v1/places/nearby",
        params={"lat": 17.385, "lng": 78.486, "radius_km": 30},
    )
    assert nearby.status_code == 200
    assert isinstance(nearby.json()["data"], list)


def test_save_place_requires_auth_and_works(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_all(db_session, force=True)
    places = client.get("/api/v1/places").json()["data"]["items"]
    place_id = places[0]["id"]

    denied = client.post(f"/api/v1/places/{place_id}/save")
    assert denied.status_code == 401

    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Saver",
            "email": "saver@example.com",
            "password": "SecurePass1",
        },
    )
    token = register.json()["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    saved = client.post(f"/api/v1/places/{place_id}/save", headers=headers)
    assert saved.status_code == 201
    assert saved.json()["data"]["saved"] is True

    listed = client.get("/api/v1/places/saved", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == place_id for item in listed.json()["data"])

    detail = client.get(f"/api/v1/places/{place_id}", headers=headers)
    assert detail.json()["data"]["is_saved"] is True

    removed = client.delete(f"/api/v1/places/{place_id}/save", headers=headers)
    assert removed.status_code == 200
    assert removed.json()["data"]["saved"] is False
