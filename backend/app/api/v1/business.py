"""Business dashboard API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUser, DbSession, require_roles
from app.models import User
from app.models.enums import UserRole
from app.schemas.business import (
    BusinessAccessOut,
    BusinessBookingOut,
    BusinessPropertyOut,
    BusinessSummaryOut,
)
from app.schemas.common import ApiResponse
from app.services.business import BusinessService

router = APIRouter(prefix="/business")

BusinessOwner = Annotated[
    User,
    Depends(
        require_roles(
            UserRole.HOTEL_OWNER.value,
            UserRole.RESTAURANT_OWNER.value,
            UserRole.GUIDE.value,
            UserRole.TOUR_OPERATOR.value,
            UserRole.DRIVER.value,
            UserRole.ADMIN.value,
        ),
    ),
]


@router.get("/access", response_model=ApiResponse[BusinessAccessOut])
def business_access(
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[BusinessAccessOut]:
    """Any authenticated user can check whether they have business access."""
    data = BusinessService(db).access(user=current_user)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/summary", response_model=ApiResponse[BusinessSummaryOut])
def business_summary(
    db: DbSession,
    current_user: BusinessOwner,
) -> ApiResponse[BusinessSummaryOut]:
    data = BusinessService(db).summary(user=current_user)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/properties", response_model=ApiResponse[list[BusinessPropertyOut]])
def business_properties(
    db: DbSession,
    current_user: BusinessOwner,
) -> ApiResponse[list[BusinessPropertyOut]]:
    data = BusinessService(db).list_properties(user=current_user)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/bookings", response_model=ApiResponse[list[BusinessBookingOut]])
def business_bookings(
    db: DbSession,
    current_user: BusinessOwner,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ApiResponse[list[BusinessBookingOut]]:
    data = BusinessService(db).list_bookings(user=current_user, limit=limit)
    return ApiResponse(success=True, message="OK", data=data)
