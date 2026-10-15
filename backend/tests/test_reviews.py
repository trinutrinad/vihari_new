"""Reviews API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def _auth_headers(client: TestClient, email: str) -> dict[str, str]:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Reviewer",
            "email": email,
            "password": "SecurePass1",
        },
    )
    assert register.status_code in {200, 201}, register.text
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_place_review_upsert_list_delete(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    headers = _auth_headers(client, "reviewer1@example.com")
    places = client.get("/api/v1/places", params={"page_size": 1}).json()["data"]["items"]
    assert places
    place_id = places[0]["id"]

    created = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={
            "target_type": "place",
            "target_id": place_id,
            "rating": 5,
            "title": "Loved it",
            "body": "Great demo place for the weekend.",
        },
    )
    assert created.status_code == 201, created.text
    review = created.json()["data"]
    assert review["rating"] == 5
    assert review["title"] == "Loved it"

    listed = client.get(
        "/api/v1/reviews",
        params={"target_type": "place", "target_id": place_id},
    )
    assert listed.status_code == 200
    assert any(item["id"] == review["id"] for item in listed.json()["data"])

    mine = client.get("/api/v1/reviews/me", headers=headers)
    assert mine.status_code == 200
    assert len(mine.json()["data"]) >= 1

    updated = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={
            "target_type": "place",
            "target_id": place_id,
            "rating": 4,
            "title": "Still good",
            "body": "Updated thoughts.",
        },
    )
    assert updated.status_code == 201
    assert updated.json()["data"]["id"] == review["id"]
    assert updated.json()["data"]["rating"] == 4

    deleted = client.delete(f"/api/v1/reviews/{review['id']}", headers=headers)
    assert deleted.status_code == 200

    after = client.get(
        "/api/v1/reviews",
        params={"target_type": "place", "target_id": place_id},
    )
    assert all(item["id"] != review["id"] for item in after.json()["data"])


def test_hotel_review_requires_auth(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    hotels = client.get("/api/v1/hotels", params={"page_size": 1}).json()["data"]["items"]
    assert hotels

    unauth = client.post(
        "/api/v1/reviews",
        json={
            "target_type": "hotel",
            "target_id": hotels[0]["id"],
            "rating": 5,
            "body": "Nice stay",
        },
    )
    assert unauth.status_code == 401

    headers = _auth_headers(client, "reviewer2@example.com")
    created = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={
            "target_type": "hotel",
            "target_id": hotels[0]["id"],
            "rating": 5,
            "body": "Nice stay",
        },
    )
    assert created.status_code == 201, created.text
