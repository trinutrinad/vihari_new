"""Admin dashboard API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession, require_roles
from app.models import User
from app.models.enums import UserRole
from app.schemas.admin import (
    AdminAccessOut,
    AdminBookingOut,
    AdminPaymentOut,
    AdminSummaryOut,
    AdminTicketOut,
    AdminUserOut,
)
from app.schemas.common import ApiResponse
from app.services.admin import AdminService

router = APIRouter(prefix="/admin")

AdminUser = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.ADMIN.value,
            UserRole.SUPER_ADMIN.value,
        ),
    ),
]


@router.get("/access", response_model=ApiResponse[AdminAccessOut])
def admin_access(
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[AdminAccessOut]:
    data = AdminService(db).access(user=current_user)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/summary", response_model=ApiResponse[AdminSummaryOut])
def admin_summary(
    db: DbSession,
    current_user: AdminUser,
) -> ApiResponse[AdminSummaryOut]:
    data = AdminService(db).summary()
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/users", response_model=ApiResponse[list[AdminUserOut]])
def admin_users(
    db: DbSession,
    current_user: AdminUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ApiResponse[list[AdminUserOut]]:
    data = AdminService(db).list_users(limit=limit)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/bookings", response_model=ApiResponse[list[AdminBookingOut]])
def admin_bookings(
    db: DbSession,
    current_user: AdminUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ApiResponse[list[AdminBookingOut]]:
    data = AdminService(db).list_bookings(limit=limit)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/payments", response_model=ApiResponse[list[AdminPaymentOut]])
def admin_payments(
    db: DbSession,
    current_user: AdminUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ApiResponse[list[AdminPaymentOut]]:
    data = AdminService(db).list_payments(limit=limit)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/tickets", response_model=ApiResponse[list[AdminTicketOut]])
def admin_tickets(
    db: DbSession,
    current_user: AdminUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    open_only: bool = False,
) -> ApiResponse[list[AdminTicketOut]]:
    data = AdminService(db).list_tickets(limit=limit, open_only=open_only)
    return ApiResponse(success=True, message="OK", data=data)
