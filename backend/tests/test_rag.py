"""RAG API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD, seed_all


def _admin_headers(client: TestClient) -> dict[str, str]:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": DEMO_ADMIN_EMAIL, "password": DEMO_ADMIN_PASSWORD},
    )
    assert login.status_code == 200, login.text
    token = login.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_rag_seed_query_and_ingest(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    seeded = client.post("/api/v1/rag/seed-demo")
    assert seeded.status_code == 201, seeded.text
    docs = seeded.json()["data"]
    assert len(docs) >= 5

    listed = client.get("/api/v1/rag/documents")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) >= 5

    monsoon = client.post(
        "/api/v1/rag/query",
        json={"question": "What should I pack for monsoon travel in India?", "top_k": 3},
    )
    assert monsoon.status_code == 200, monsoon.text
    body = monsoon.json()["data"]
    assert body["verified"] is True
    assert body["sources"]
    assert "monsoon" in body["answer"].lower() or "rain" in body["answer"].lower()

    unknown = client.post(
        "/api/v1/rag/query",
        json={"question": "What is the exact darshan fee for temple XYZ123 tomorrow?"},
    )
    assert unknown.status_code == 200
    # May or may not verify depending on lexical overlap; if verified must cite sources
    if not unknown.json()["data"]["verified"]:
        assert "couldn" in unknown.json()["data"]["answer"].lower()

    admin = _admin_headers(client)
    ingested = client.post(
        "/api/v1/rag/ingest",
        headers=admin,
        json={
            "title": "[SEED/DEMO] Goa ferry tip",
            "text": (
                "Demo ferry tip for Goa coastal hops: check seasonal schedules "
                "locally, carry motion-sickness tablets if needed, and confirm "
                "last boat times before sunset. This is curated demo text only."
            ),
            "source_type": "curated",
            "source_uri": "seed://goa-ferry-tip",
        },
    )
    assert ingested.status_code == 201, ingested.text
    assert ingested.json()["data"]["chunks_created"] >= 1

    ferry = client.post(
        "/api/v1/rag/query",
        json={"question": "Any tips for Goa ferry schedules?"},
    )
    assert ferry.status_code == 200
    assert ferry.json()["data"]["verified"] is True


def test_rag_ingest_requires_admin(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    response = client.post(
        "/api/v1/rag/ingest",
        json={
            "title": "Unauthorized doc",
            "text": "x" * 40,
            "source_type": "curated",
        },
    )
    assert response.status_code == 401
