"""Authentication business logic."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationAppError,
)
from app.core.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    RESET_TOKEN_TYPE,
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import Role, User, UserProfile, UserRole, UserRoleLink
from app.models.auth import OtpChallenge, PasswordResetToken, RefreshToken
from app.services.otp import (
    generate_otp_code,
    get_otp_provider,
    hash_otp,
    verify_otp_hash,
)


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def register(
        self,
        *,
        full_name: str,
        email: str | None,
        phone: str | None,
        password: str,
    ) -> User:
        if not email and not phone:
            raise ValidationAppError("Email or phone is required")
        if email:
            email = email.strip().lower()
            if self._get_user_by_email(email):
                raise ConflictError("Email already registered")
        if phone:
            phone = _normalize_phone(phone)
            if self._get_user_by_phone(phone):
                raise ConflictError("Phone already registered")

        user = User(
            full_name=full_name.strip(),
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            primary_role=UserRole.USER.value,
            is_email_verified=False,
            is_phone_verified=False,
        )
        self.db.add(user)
        self.db.flush()

        self.db.add(
            UserProfile(
                user_id=user.id,
                preferred_language="en",
            ),
        )
        self._ensure_role_assignment(user, UserRole.USER.value)
        self.db.commit()
        self.db.refresh(user)
        return self.get_user(user.id)

    def login_with_password(
        self,
        *,
        email: str | None,
        phone: str | None,
        password: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        user = None
        if email:
            user = self._get_user_by_email(email.strip().lower())
        elif phone:
            user = self._get_user_by_phone(_normalize_phone(phone))
        else:
            raise ValidationAppError("Email or phone is required")

        if not user or not user.password_hash:
            raise UnauthorizedError("Invalid credentials")
        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid credentials")
        if not user.is_active:
            raise ForbiddenError("Account is deactivated")

        access, refresh = self._issue_session(
            user,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        user.last_login_at = _utcnow()
        self.db.commit()
        return self.get_user(user.id), access, refresh

    def request_phone_otp(self, *, phone: str, purpose: str = "login") -> dict:
        phone = _normalize_phone(phone)
        code = generate_otp_code()
        expires_at = _utcnow() + timedelta(minutes=self.settings.otp_expire_minutes)

        challenge = OtpChallenge(
            phone=phone,
            purpose=purpose,
            code_hash=hash_otp(code),
            expires_at=expires_at,
            provider=self.settings.otp_provider,
            is_mock=self.settings.otp_provider == "mock",
        )
        self.db.add(challenge)
        self.db.commit()
        self.db.refresh(challenge)

        dispatch = get_otp_provider().send_otp(phone=phone, code=code, purpose=purpose)
        result = {
            "challenge_id": str(challenge.id),
            "expires_at": expires_at.isoformat(),
            "provider": dispatch.provider,
            "is_mock": dispatch.is_mock,
            "message": "OTP sent",
        }
        if self.settings.expose_otp_debug_code and dispatch.debug_code:
            result["debug_code"] = dispatch.debug_code
        return result

    def verify_phone_otp(
        self,
        *,
        challenge_id: uuid.UUID,
        code: str,
        full_name: str | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        challenge = self.db.get(OtpChallenge, challenge_id)
        if not challenge:
            raise NotFoundError("OTP challenge not found")
        if challenge.consumed_at is not None:
            raise ValidationAppError("OTP already used")
        if _as_utc(challenge.expires_at) < _utcnow():
            raise ValidationAppError("OTP expired")
        if challenge.attempts >= challenge.max_attempts:
            raise ValidationAppError("Too many OTP attempts")

        challenge.attempts += 1
        if not verify_otp_hash(code, challenge.code_hash):
            self.db.commit()
            raise UnauthorizedError("Invalid OTP")

        challenge.consumed_at = _utcnow()
        user = self._get_user_by_phone(challenge.phone)
        if not user:
            user = User(
                full_name=(full_name or "Traveller").strip(),
                phone=challenge.phone,
                primary_role=UserRole.USER.value,
                is_phone_verified=True,
            )
            self.db.add(user)
            self.db.flush()
            self.db.add(UserProfile(user_id=user.id, preferred_language="en"))
            self._ensure_role_assignment(user, UserRole.USER.value)
        else:
            if not user.is_active:
                raise ForbiddenError("Account is deactivated")
            user.is_phone_verified = True

        access, refresh = self._issue_session(
            user,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        user.last_login_at = _utcnow()
        self.db.commit()
        return self.get_user(user.id), access, refresh

    def refresh(self, *, refresh_token: str) -> tuple[User, str, str]:
        payload = decode_token(refresh_token, expected_type=REFRESH_TOKEN_TYPE)
        jti_raw = payload.get("jti")
        if not jti_raw:
            raise UnauthorizedError("Invalid refresh token")
        jti = uuid.UUID(str(jti_raw))
        stored = self.db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
        if not stored or stored.revoked_at is not None:
            raise UnauthorizedError("Refresh token revoked")
        if _as_utc(stored.expires_at) < _utcnow():
            raise UnauthorizedError("Refresh token expired")
        if stored.token_hash != _hash_token(refresh_token):
            raise UnauthorizedError("Invalid refresh token")

        user = self.get_user(stored.user_id)
        if not user.is_active:
            raise ForbiddenError("Account is deactivated")

        stored.revoked_at = _utcnow()
        access, new_refresh = self._issue_session(user)
        self.db.commit()
        return user, access, new_refresh

    def logout(self, *, refresh_token: str | None, access_token: str | None = None) -> None:
        if refresh_token:
            try:
                payload = decode_token(refresh_token, expected_type=REFRESH_TOKEN_TYPE)
                jti = uuid.UUID(str(payload["jti"]))
                stored = self.db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
                if stored and stored.revoked_at is None:
                    stored.revoked_at = _utcnow()
                    self.db.commit()
            except UnauthorizedError:
                pass
        # Access tokens are short-lived; blacklist can be added later via Redis.
        _ = access_token

    def forgot_password(self, *, email: str) -> dict:
        email = email.strip().lower()
        user = self._get_user_by_email(email)
        # Always return generic message to avoid account enumeration
        message = "If an account exists, password reset instructions were issued"
        if not user:
            return {"message": message, "reset_token": None}

        raw = create_password_reset_token(user_id=user.id)
        self.db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=_hash_token(raw),
                expires_at=_utcnow() + timedelta(minutes=30),
            ),
        )
        self.db.commit()
        result = {"message": message, "reset_token": None}
        if self.settings.debug:
            result["reset_token"] = raw
        return result

    def reset_password(self, *, token: str, new_password: str) -> None:
        payload = decode_token(token, expected_type=RESET_TOKEN_TYPE)
        user_id = uuid.UUID(str(payload["sub"]))
        token_hash = _hash_token(token)
        stored = self.db.scalar(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash),
        )
        if not stored or stored.used_at is not None:
            raise UnauthorizedError("Invalid reset token")
        if _as_utc(stored.expires_at) < _utcnow():
            raise UnauthorizedError("Reset token expired")
        if stored.user_id != user_id:
            raise UnauthorizedError("Invalid reset token")

        user = self.get_user(user_id)
        user.password_hash = hash_password(new_password)
        stored.used_at = _utcnow()
        # revoke refresh sessions
        tokens = self.db.scalars(
            select(RefreshToken).where(
                RefreshToken.user_id == user.id,
                RefreshToken.revoked_at.is_(None),
            ),
        ).all()
        now = _utcnow()
        for item in tokens:
            item.revoked_at = now
        self.db.commit()

    def get_user(self, user_id: uuid.UUID) -> User:
        user = self.db.scalar(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.profile), selectinload(User.roles)),
        )
        if not user:
            raise NotFoundError("User not found")
        return user

    def update_profile(
        self,
        *,
        user_id: uuid.UUID,
        full_name: str | None = None,
        avatar_url: str | None = None,
        bio: str | None = None,
        preferred_language: str | None = None,
        home_city: str | None = None,
        travel_preferences: str | None = None,
    ) -> User:
        user = self.get_user(user_id)
        if full_name is not None:
            user.full_name = full_name.strip()
        if user.profile is None:
            user.profile = UserProfile(user_id=user.id)
            self.db.add(user.profile)
            self.db.flush()
        profile = user.profile
        if avatar_url is not None:
            profile.avatar_url = avatar_url
        if bio is not None:
            profile.bio = bio
        if preferred_language is not None:
            profile.preferred_language = preferred_language
        if home_city is not None:
            profile.home_city = home_city
        if travel_preferences is not None:
            profile.travel_preferences = travel_preferences
        self.db.commit()
        return self.get_user(user_id)

    def _issue_session(
        self,
        user: User,
        *,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, str]:
        role_names = [role.name for role in user.roles] or [user.primary_role]
        access = create_access_token(
            user_id=user.id,
            role=user.primary_role,
            roles=role_names,
        )
        jti = uuid.uuid4()
        refresh = create_refresh_token(user_id=user.id, token_id=jti)
        self.db.add(
            RefreshToken(
                user_id=user.id,
                jti=jti,
                token_hash=_hash_token(refresh),
                expires_at=_utcnow()
                + timedelta(days=self.settings.refresh_token_expire_days),
                user_agent=user_agent,
                ip_address=ip_address,
            ),
        )
        self.db.flush()
        return access, refresh

    def _ensure_role_assignment(self, user: User, role_name: str) -> None:
        role = self.db.scalar(select(Role).where(Role.name == role_name))
        if role is None:
            role = Role(name=role_name, description=f"System role {role_name}")
            self.db.add(role)
            self.db.flush()
        exists = self.db.scalar(
            select(UserRoleLink).where(
                UserRoleLink.user_id == user.id,
                UserRoleLink.role_id == role.id,
            ),
        )
        if not exists:
            self.db.add(UserRoleLink(user_id=user.id, role_id=role.id))

    def _get_user_by_email(self, email: str) -> User | None:
        return self.db.scalar(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.profile), selectinload(User.roles)),
        )

    def _get_user_by_phone(self, phone: str) -> User | None:
        return self.db.scalar(
            select(User)
            .where(User.phone == phone)
            .options(selectinload(User.profile), selectinload(User.roles)),
        )


def _normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone.strip() if ch.isdigit() or ch == "+")
    if len(digits) < 10:
        raise ValidationAppError("Invalid phone number")
    return digits


def parse_bearer_user_id(token: str) -> uuid.UUID:
    payload = decode_token(token, expected_type=ACCESS_TOKEN_TYPE)
    return uuid.UUID(str(payload["sub"]))


def random_password_hint() -> str:
    return secrets.token_urlsafe(8)
