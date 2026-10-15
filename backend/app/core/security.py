"""Password hashing and JWT helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
RESET_TOKEN_TYPE = "password_reset"


def hash_password(password: str) -> str:
    """Hash a password with bcrypt. Never store plaintext."""
    password_bytes = password.encode("utf-8")
    # bcrypt only uses the first 72 bytes
    digest = bcrypt.hashpw(password_bytes[:72], bcrypt.gensalt(rounds=12))
    return digest.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8")[:72],
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_token(
    *,
    subject: UUID | str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(
    *,
    user_id: UUID,
    role: str,
    roles: list[str] | None = None,
) -> str:
    settings = get_settings()
    return create_token(
        subject=user_id,
        token_type=ACCESS_TOKEN_TYPE,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        extra_claims={
            "role": role,
            "roles": roles or [role],
        },
    )


def create_refresh_token(*, user_id: UUID, token_id: UUID) -> str:
    settings = get_settings()
    return create_token(
        subject=user_id,
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        extra_claims={"jti": str(token_id)},
    )


def create_password_reset_token(*, user_id: UUID) -> str:
    return create_token(
        subject=user_id,
        token_type=RESET_TOKEN_TYPE,
        expires_delta=timedelta(minutes=30),
    )


def decode_token(token: str, *, expected_type: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    if expected_type and payload.get("type") != expected_type:
        raise UnauthorizedError("Invalid token type")
    if "sub" not in payload:
        raise UnauthorizedError("Invalid token payload")
    return payload
