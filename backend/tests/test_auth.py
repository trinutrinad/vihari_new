"""Authentication API tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_register_login_me_logout_flow(client: TestClient) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Asha Traveller",
            "email": "asha@example.com",
            "password": "SecurePass1",
        },
    )
    assert register.status_code == 201, register.text
    payload = register.json()
    assert payload["success"] is True
    assert payload["data"]["user"]["email"] == "asha@example.com"
    assert "password_hash" not in payload["data"]["user"]
    access = payload["data"]["tokens"]["access_token"]
    refresh = payload["data"]["tokens"]["refresh_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json()["data"]["full_name"] == "Asha Traveller"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "asha@example.com", "password": "SecurePass1"},
    )
    assert login.status_code == 200
    assert login.json()["data"]["tokens"]["access_token"]

    bad = client.post(
        "/api/v1/auth/login",
        json={"email": "asha@example.com", "password": "wrong-password"},
    )
    assert bad.status_code == 401

    logout = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert logout.status_code == 200

    refresh_after = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh},
    )
    assert refresh_after.status_code == 401


def test_phone_otp_login_architecture(client: TestClient) -> None:
    request = client.post(
        "/api/v1/auth/phone/request-otp",
        json={"phone": "+919876543210", "purpose": "login"},
    )
    assert request.status_code == 200
    data = request.json()["data"]
    assert data["is_mock"] is True
    assert data["debug_code"]

    verify = client.post(
        "/api/v1/auth/phone/verify-otp",
        json={
            "challenge_id": data["challenge_id"],
            "code": data["debug_code"],
            "full_name": "Phone Traveller",
        },
    )
    assert verify.status_code == 200
    user = verify.json()["data"]["user"]
    assert user["phone"] == "+919876543210"
    assert user["is_phone_verified"] is True


def test_forgot_and_reset_password(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Reset User",
            "email": "reset@example.com",
            "password": "OldPassword1",
        },
    )
    forgot = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "reset@example.com"},
    )
    assert forgot.status_code == 200
    token = forgot.json()["data"]["reset_token"]
    assert token

    reset = client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "new_password": "NewPassword1"},
    )
    assert reset.status_code == 200

    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "reset@example.com", "password": "OldPassword1"},
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": "reset@example.com", "password": "NewPassword1"},
    )
    assert new_login.status_code == 200


def test_profile_update(client: TestClient) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Profile User",
            "email": "profile@example.com",
            "password": "SecurePass1",
        },
    )
    access = register.json()["data"]["tokens"]["access_token"]
    updated = client.patch(
        "/api/v1/auth/me/profile",
        headers={"Authorization": f"Bearer {access}"},
        json={
            "home_city": "Hyderabad",
            "preferred_language": "hi",
            "travel_preferences": ["family", "temples"],
            "bio": "Loves weekend getaways",
        },
    )
    assert updated.status_code == 200
    profile = updated.json()["data"]["profile"]
    assert profile["home_city"] == "Hyderabad"
    assert profile["preferred_language"] == "hi"
    assert profile["travel_preferences"] == ["family", "temples"]


def test_duplicate_email_conflict(client: TestClient) -> None:
    body = {
        "full_name": "Dup User",
        "email": "dup@example.com",
        "password": "SecurePass1",
    }
    assert client.post("/api/v1/auth/register", json=body).status_code == 201
    again = client.post("/api/v1/auth/register", json=body)
    assert again.status_code == 409


def test_require_roles_allows_admin_and_blocks_user() -> None:
    from app.api.deps import require_roles
    from app.core.exceptions import ForbiddenError
    from app.models import User, UserRole

    dependency = require_roles("ADMIN")
    admin = User(full_name="Admin", primary_role=UserRole.ADMIN.value, email="a@x.com")
    admin.roles = []
    assert dependency(admin) is admin

    user = User(full_name="User", primary_role=UserRole.USER.value, email="u@x.com")
    user.roles = []
    try:
        dependency(user)
        raised = False
    except ForbiddenError:
        raised = True
    assert raised
