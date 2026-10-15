"""Transport API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def test_list_and_get_transport(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    listing = client.get("/api/v1/transport", params={"page_size": 20})
    assert listing.status_code == 200, listing.text
    payload = listing.json()["data"]
    assert payload["meta"]["total"] >= 8
    option = payload["items"][0]
    assert option["is_seed_data"] is True
    assert "vehicle_type" in option
    assert "base_fare_inr" in option

    detail = client.get(f"/api/v1/transport/{option['id']}")
    assert detail.status_code == 200
    body = detail.json()["data"]
    assert body["id"] == option["id"]
    assert "data_notice" in body

    by_code = client.get(f"/api/v1/transport/by-code/{option['code']}")
    assert by_code.status_code == 200
    assert by_code.json()["data"]["code"] == option["code"]


def test_transport_filters_and_estimate(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    auto = client.get("/api/v1/transport", params={"vehicle_type": "auto"})
    assert auto.status_code == 200
    assert auto.json()["data"]["meta"]["total"] >= 1
    assert all(item["vehicle_type"] == "auto" for item in auto.json()["data"]["items"])

    estimate = client.get(
        "/api/v1/transport/estimate",
        params={"code": "taxi", "distance_km": 10},
    )
    assert estimate.status_code == 200
    body = estimate.json()["data"]
    assert body["estimated_fare_inr"] == 80 + 18 * 10
    assert body["is_estimate"] is True

    missing = client.get("/api/v1/transport/estimate", params={"distance_km": 5})
    assert missing.status_code in {400, 422}
