"""Global search API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def test_global_search_returns_multi_entity_results(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_all(db_session, force=True)

    response = client.get("/api/v1/search", params={"q": "Hyderabad"})
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["total"] >= 1
    assert data["items"]
    types = {item["entity_type"] for item in data["items"]}
    assert "place" in types or "city" in types or "hotel" in types or "restaurant" in types
    assert "facets" in data


def test_search_filters_by_type_and_state(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    response = client.get(
        "/api/v1/search",
        params={"q": "demo", "types": "hotels", "state": "TG"},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert all(item["entity_type"] == "hotel" for item in items)


def test_autocomplete_and_trending(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    auto = client.get("/api/v1/search/autocomplete", params={"q": "jai"})
    assert auto.status_code == 200
    suggestions = auto.json()["data"]
    assert isinstance(suggestions, list)

    trending = client.get("/api/v1/search/trending")
    assert trending.status_code == 200
    payload = trending.json()["data"]
    assert len(payload["queries"]) >= 5
    assert isinstance(payload["places"], list)


def test_location_aware_search(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    response = client.get(
        "/api/v1/search",
        params={"q": "", "types": "places", "lat": 17.385, "lng": 78.486, "radius_km": 40},
    )
    assert response.status_code == 200
    items = response.json()["data"]["items"]
    for item in items:
        if item.get("distance_km") is not None:
            assert item["distance_km"] <= 40
