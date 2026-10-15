"""Payments API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.seed import seed_all


def _auth_headers(client: TestClient, email: str) -> dict[str, str]:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Pay User",
            "email": email,
            "password": "SecurePass1",
        },
    )
    assert register.status_code in {200, 201}, register.text
    token = register.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_booking(client: TestClient, headers: dict[str, str]) -> dict:
    hotels = client.get("/api/v1/hotels", params={"page_size": 1}).json()["data"]["items"]
    assert hotels
    created = client.post(
        "/api/v1/bookings",
        headers=headers,
        json={"resource_type": "hotel", "resource_id": hotels[0]["id"], "nights": 1},
    )
    assert created.status_code == 201, created.text
    return created.json()["data"]


def test_payment_capture_list_refund(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    headers = _auth_headers(client, "payer1@example.com")
    booking = _create_booking(client, headers)

    coupon = client.get("/api/v1/coupons/BYDEMO10")
    assert coupon.status_code == 200
    assert coupon.json()["data"]["discount_percent"] == 10

    paid = client.post(
        "/api/v1/payments",
        headers=headers,
        json={
            "booking_id": booking["id"],
            "method": "upi",
            "coupon_code": "BYDEMO10",
        },
    )
    assert paid.status_code == 201, paid.text
    payment = paid.json()["data"]
    assert payment["status"] == "captured"
    assert payment["is_mock"] is True
    assert payment["amount_inr"] < booking["amount_inr"]

    listed = client.get("/api/v1/payments", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == payment["id"] for item in listed.json()["data"])

    duplicate = client.post(
        "/api/v1/payments",
        headers=headers,
        json={"booking_id": booking["id"], "method": "mock"},
    )
    assert duplicate.status_code == 409

    refunded = client.post(
        f"/api/v1/payments/{payment['id']}/refund",
        headers=headers,
    )
    assert refunded.status_code == 200
    assert refunded.json()["data"]["status"] == "refunded"


def test_wallet_topup_and_pay(client: TestClient, db_session: Session) -> None:
    seed_all(db_session, force=True)
    headers = _auth_headers(client, "payer2@example.com")
    booking = _create_booking(client, headers)

    wallet = client.get("/api/v1/wallet", headers=headers)
    assert wallet.status_code == 200
    assert float(wallet.json()["data"]["balance_inr"]) == 0

    topup = client.post(
        "/api/v1/wallet/topup",
        headers=headers,
        json={"amount_inr": 20000},
    )
    assert topup.status_code == 200
    assert float(topup.json()["data"]["balance_inr"]) == 20000

    paid = client.post(
        "/api/v1/payments",
        headers=headers,
        json={"booking_id": booking["id"], "method": "wallet"},
    )
    assert paid.status_code == 201, paid.text
    assert paid.json()["data"]["method"] == "wallet"

    after = client.get("/api/v1/wallet", headers=headers)
    assert float(after.json()["data"]["balance_inr"]) == 20000 - paid.json()["data"][
        "amount_inr"
    ]
