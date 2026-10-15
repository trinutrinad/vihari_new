"""Authentication routes."""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import AuthServiceDep, CurrentUser, bearer_scheme, client_meta
from app.models import User
from app.schemas.auth import (
    AuthSessionOut,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageOut,
    PhoneOtpChallengeOut,
    PhoneOtpRequest,
    PhoneOtpVerifyRequest,
    ProfileUpdateRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenPairOut,
    UserOut,
    UserProfileOut,
)
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/auth")


def _serialize_user(user: User) -> UserOut:
    preferences: list[str] = []
    profile_out = None
    if user.profile:
        raw = user.profile.travel_preferences
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    preferences = [str(item) for item in parsed]
            except json.JSONDecodeError:
                preferences = []
        profile_out = UserProfileOut(
            avatar_url=user.profile.avatar_url,
            bio=user.profile.bio,
            preferred_language=user.profile.preferred_language,
            home_city=user.profile.home_city,
            travel_preferences=preferences,
        )
    return UserOut(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        primary_role=user.primary_role,
        roles=[role.name for role in user.roles] or [user.primary_role],
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        is_phone_verified=user.is_phone_verified,
        last_login_at=user.last_login_at,
        profile=profile_out,
    )


def _session_response(user: User, access: str, refresh: str) -> ApiResponse[AuthSessionOut]:
    return ApiResponse(
        success=True,
        message="OK",
        data=AuthSessionOut(
            user=_serialize_user(user),
            tokens=TokenPairOut(access_token=access, refresh_token=refresh),
        ),
    )


@router.post(
    "/register",
    response_model=ApiResponse[AuthSessionOut],
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    auth: AuthServiceDep,
    meta: Annotated[tuple[str | None, str | None], Depends(client_meta)],
) -> ApiResponse[AuthSessionOut]:
    user = auth.register(
        full_name=payload.full_name,
        email=str(payload.email) if payload.email else None,
        phone=payload.phone,
        password=payload.password,
    )
    user, access, refresh = auth.login_with_password(
        email=user.email,
        phone=user.phone if not user.email else None,
        password=payload.password,
        user_agent=meta[0],
        ip_address=meta[1],
    )
    return _session_response(user, access, refresh)


@router.post("/login", response_model=ApiResponse[AuthSessionOut])
def login(
    payload: LoginRequest,
    auth: AuthServiceDep,
    meta: Annotated[tuple[str | None, str | None], Depends(client_meta)],
) -> ApiResponse[AuthSessionOut]:
    user, access, refresh = auth.login_with_password(
        email=str(payload.email) if payload.email else None,
        phone=payload.phone,
        password=payload.password,
        user_agent=meta[0],
        ip_address=meta[1],
    )
    return _session_response(user, access, refresh)


@router.post("/phone/request-otp", response_model=ApiResponse[PhoneOtpChallengeOut])
def request_phone_otp(
    payload: PhoneOtpRequest,
    auth: AuthServiceDep,
) -> ApiResponse[PhoneOtpChallengeOut]:
    result = auth.request_phone_otp(phone=payload.phone, purpose=payload.purpose)
    return ApiResponse(success=True, message="OTP dispatched", data=PhoneOtpChallengeOut(**result))


@router.post("/phone/verify-otp", response_model=ApiResponse[AuthSessionOut])
def verify_phone_otp(
    payload: PhoneOtpVerifyRequest,
    auth: AuthServiceDep,
    meta: Annotated[tuple[str | None, str | None], Depends(client_meta)],
) -> ApiResponse[AuthSessionOut]:
    user, access, refresh = auth.verify_phone_otp(
        challenge_id=payload.challenge_id,
        code=payload.code,
        full_name=payload.full_name,
        user_agent=meta[0],
        ip_address=meta[1],
    )
    return _session_response(user, access, refresh)


@router.post("/refresh", response_model=ApiResponse[AuthSessionOut])
def refresh_session(
    payload: RefreshRequest,
    auth: AuthServiceDep,
) -> ApiResponse[AuthSessionOut]:
    user, access, refresh = auth.refresh(refresh_token=payload.refresh_token)
    return _session_response(user, access, refresh)


@router.post("/logout", response_model=ApiResponse[MessageOut])
def logout(
    payload: LogoutRequest,
    auth: AuthServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> ApiResponse[MessageOut]:
    access = credentials.credentials if credentials else None
    auth.logout(refresh_token=payload.refresh_token, access_token=access)
    return ApiResponse(success=True, message="Logged out", data=MessageOut(message="Logged out"))


@router.post("/forgot-password", response_model=ApiResponse[MessageOut])
def forgot_password(
    payload: ForgotPasswordRequest,
    auth: AuthServiceDep,
) -> ApiResponse[MessageOut]:
    result = auth.forgot_password(email=str(payload.email))
    return ApiResponse(
        success=True,
        message=result["message"],
        data=MessageOut(message=result["message"], reset_token=result.get("reset_token")),
    )


@router.post("/reset-password", response_model=ApiResponse[MessageOut])
def reset_password(
    payload: ResetPasswordRequest,
    auth: AuthServiceDep,
) -> ApiResponse[MessageOut]:
    auth.reset_password(token=payload.token, new_password=payload.new_password)
    return ApiResponse(
        success=True,
        message="Password updated",
        data=MessageOut(message="Password updated"),
    )


@router.get("/me", response_model=ApiResponse[UserOut])
def me(current_user: CurrentUser) -> ApiResponse[UserOut]:
    return ApiResponse(success=True, message="OK", data=_serialize_user(current_user))


@router.patch("/me/profile", response_model=ApiResponse[UserOut])
def update_my_profile(
    payload: ProfileUpdateRequest,
    current_user: CurrentUser,
    auth: AuthServiceDep,
) -> ApiResponse[UserOut]:
    preferences_json = None
    if payload.travel_preferences is not None:
        preferences_json = json.dumps(payload.travel_preferences)
    user = auth.update_profile(
        user_id=current_user.id,
        full_name=payload.full_name,
        avatar_url=payload.avatar_url,
        bio=payload.bio,
        preferred_language=payload.preferred_language,
        home_city=payload.home_city,
        travel_preferences=preferences_json,
    )
    return ApiResponse(success=True, message="Profile updated", data=_serialize_user(user))
