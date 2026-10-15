"""Maps API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def test_map_pins_in_india_bounds(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    response = client.get(
        "/api/v1/maps/pins",
        params={
            "north": 35.5,
            "south": 6.5,
            "east": 97.5,
            "west": 68.0,
            "limit": 50,
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["total"] >= 1
    assert data["provider"] == "leaflet_osm"
    pin = data["pins"][0]
    assert pin["entity_type"] == "place"
    assert pin["href"].startswith("/places/")
    assert pin["latitude"] is not None
    assert pin["longitude"] is not None


def test_map_pins_rejects_invalid_bounds(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    response = client.get(
        "/api/v1/maps/pins",
        params={"north": 10, "south": 20, "east": 80, "west": 70},
    )
    assert response.status_code == 422


def test_map_cities(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    response = client.get("/api/v1/maps/cities", params={"limit": 10})
    assert response.status_code == 200
    cities = response.json()["data"]
    assert isinstance(cities, list)
    assert len(cities) >= 1
    assert "latitude" in cities[0]
    assert "place_count" in cities[0]
