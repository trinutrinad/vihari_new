"""Bookings API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.bookings import (
    BookingCancel,
    BookingCreate,
    BookingDetailOut,
    BookingSummaryOut,
)
from app.schemas.common import ApiResponse
from app.services.bookings import BookingService

router = APIRouter(prefix="/bookings")


@router.get("", response_model=ApiResponse[list[BookingSummaryOut]])
def list_bookings(
    db: DbSession,
    current_user: CurrentUser,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    resource_type: str | None = None,
) -> ApiResponse[list[BookingSummaryOut]]:
    data = BookingService(db).list_bookings(
        user_id=current_user.id,
        status=status_filter,
        resource_type=resource_type,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.post(
    "",
    response_model=ApiResponse[BookingDetailOut],
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    payload: BookingCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[BookingDetailOut]:
    data = BookingService(db).create_booking(user_id=current_user.id, payload=payload)
    return ApiResponse(success=True, message="Booking confirmed (mock)", data=data)


@router.get("/{booking_id}", response_model=ApiResponse[BookingDetailOut])
def get_booking(
    booking_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[BookingDetailOut]:
    data = BookingService(db).get_booking(booking_id=booking_id, user_id=current_user.id)
    return ApiResponse(success=True, message="OK", data=data)


@router.post("/{booking_id}/cancel", response_model=ApiResponse[BookingDetailOut])
def cancel_booking(
    booking_id: UUID,
    payload: BookingCancel,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[BookingDetailOut]:
    data = BookingService(db).cancel_booking(
        booking_id=booking_id,
        user_id=current_user.id,
        payload=payload,
    )
    return ApiResponse(success=True, message="Booking cancelled", data=data)
