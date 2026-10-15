"""Auth and profile request/response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def require_email_or_phone(self) -> RegisterRequest:
        if not self.email and not self.phone:
            raise ValueError("Either email or phone is required")
        return self


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def require_email_or_phone(self) -> LoginRequest:
        if not self.email and not self.phone:
            raise ValueError("Either email or phone is required")
        return self


class PhoneOtpRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=20)
    purpose: str = Field(default="login", max_length=40)


class PhoneOtpVerifyRequest(BaseModel):
    challenge_id: UUID
    code: str = Field(min_length=4, max_length=8)
    full_name: str | None = Field(default=None, max_length=160)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    avatar_url: str | None = Field(default=None, max_length=500)
    bio: str | None = None
    preferred_language: str | None = Field(default=None, max_length=16)
    home_city: str | None = Field(default=None, max_length=120)
    travel_preferences: list[str] | None = None

    @field_validator("travel_preferences")
    @classmethod
    def limit_preferences(cls, value: list[str] | None) -> list[str] | None:
        if value is not None and len(value) > 20:
            raise ValueError("Too many travel preferences")
        return value


class UserProfileOut(BaseModel):
    avatar_url: str | None = None
    bio: str | None = None
    preferred_language: str = "en"
    home_city: str | None = None
    travel_preferences: list[str] = Field(default_factory=list)


class UserOut(BaseModel):
    id: UUID
    full_name: str
    email: str | None = None
    phone: str | None = None
    primary_role: str
    roles: list[str] = Field(default_factory=list)
    is_active: bool
    is_email_verified: bool
    is_phone_verified: bool
    last_login_at: datetime | None = None
    profile: UserProfileOut | None = None


class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthSessionOut(BaseModel):
    user: UserOut
    tokens: TokenPairOut


class PhoneOtpChallengeOut(BaseModel):
    challenge_id: str
    expires_at: str
    provider: str
    is_mock: bool
    message: str
    debug_code: str | None = None


class MessageOut(BaseModel):
    message: str
    reset_token: str | None = None
