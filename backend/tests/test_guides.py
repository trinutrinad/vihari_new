"""Guides API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def test_list_and_get_guides(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    listing = client.get("/api/v1/guides", params={"page_size": 20})
    assert listing.status_code == 200, listing.text
    payload = listing.json()["data"]
    assert payload["meta"]["total"] >= 4
    guide = payload["items"][0]
    assert guide["is_seed_data"] is True
    assert "languages" in guide
    assert "price_per_day_inr" in guide

    detail = client.get(f"/api/v1/guides/{guide['id']}")
    assert detail.status_code == 200
    body = detail.json()["data"]
    assert body["id"] == guide["id"]
    assert body["availability"]
    assert "data_notice" in body


def test_guide_filters_and_nearby(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    jaipur = client.get("/api/v1/guides", params={"city": "jaipur"})
    assert jaipur.status_code == 200
    assert jaipur.json()["data"]["meta"]["total"] >= 1

    language = client.get("/api/v1/guides", params={"language": "Kannada"})
    assert language.status_code == 200
    assert language.json()["data"]["meta"]["total"] >= 1

    specialization = client.get("/api/v1/guides", params={"specialization": "Heritage"})
    assert specialization.status_code == 200
    assert specialization.json()["data"]["meta"]["total"] >= 1

    nearby = client.get(
        "/api/v1/guides/nearby",
        params={"lat": 26.9124, "lng": 75.7873, "radius_km": 100},
    )
    assert nearby.status_code == 200
    assert isinstance(nearby.json()["data"], list)
