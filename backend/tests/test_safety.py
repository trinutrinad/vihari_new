"""Safety API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def _auth_headers(client: TestClient, email: str) -> dict[str, str]:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Safe Traveller",
            "email": email,
            "password": "SecurePass1",
        },
    )
    assert register.status_code in {200, 201}, register.text
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_safety_tips_and_numbers(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)

    tips = client.get("/api/v1/safety/tips")
    assert tips.status_code == 200, tips.text
    body = tips.json()["data"]
    assert body["tips"]
    assert any(item["number"] == "112" for item in body["emergency_numbers"])
    assert "disclaimer" in body

    city_tips = client.get("/api/v1/safety/tips", params={"city": "jaipur"})
    assert city_tips.status_code == 200
    city_body = city_tips.json()["data"]
    assert city_body["city"]
    assert city_body["nearby_hints"]

    numbers = client.get("/api/v1/safety/emergency-numbers")
    assert numbers.status_code == 200
    assert len(numbers.json()["data"]) >= 4


def test_emergency_contacts_and_sos(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    headers = _auth_headers(client, "safe1@example.com")

    unauth = client.get("/api/v1/safety/contacts")
    assert unauth.status_code == 401

    created = client.post(
        "/api/v1/safety/contacts",
        headers=headers,
        json={
            "name": "Parent",
            "phone": "+919999000111",
            "relationship_label": "Family",
            "is_primary": True,
        },
    )
    assert created.status_code == 201, created.text
    contact = created.json()["data"]
    assert contact["is_primary"] is True

    listed = client.get("/api/v1/safety/contacts", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1

    updated = client.patch(
        f"/api/v1/safety/contacts/{contact['id']}",
        headers=headers,
        json={"phone": "+919999000222"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["phone"] == "+919999000222"

    sos = client.post(
        "/api/v1/safety/sos",
        headers=headers,
        json={"message": "Demo check-in", "city": "Jaipur"},
    )
    assert sos.status_code == 201, sos.text
    sos_body = sos.json()["data"]
    assert sos_body["is_mock"] is True
    assert sos_body["ticket_number"].startswith("SOS-")

    deleted = client.delete(
        f"/api/v1/safety/contacts/{contact['id']}",
        headers=headers,
    )
    assert deleted.status_code == 200
    after = client.get("/api/v1/safety/contacts", headers=headers)
    assert after.json()["data"] == []
