"""Trip planning API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.trips import (
    TripCreate,
    TripDayCreate,
    TripDayUpdate,
    TripDetailOut,
    TripPlaceCreate,
    TripShareOut,
    TripSummaryOut,
    TripUpdate,
)
from app.services.trips import TripService

router = APIRouter(prefix="/trips")


@router.get("", response_model=ApiResponse[list[TripSummaryOut]])
def list_trips(
    db: DbSession,
    current_user: CurrentUser,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> ApiResponse[list[TripSummaryOut]]:
    data = TripService(db).list_trips(user_id=current_user.id, status=status_filter)
    return ApiResponse(success=True, message="OK", data=data)


@router.post("", response_model=ApiResponse[TripDetailOut], status_code=status.HTTP_201_CREATED)
def create_trip(
    payload: TripCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[TripDetailOut]:
    data = TripService(db).create_trip(user_id=current_user.id, payload=payload)
    return ApiResponse(success=True, message="Trip created", data=data)


@router.get("/shared/{share_code}", response_model=ApiResponse[TripDetailOut])
def get_shared_trip(share_code: str, db: DbSession) -> ApiResponse[TripDetailOut]:
    data = TripService(db).get_shared_trip(share_code)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/{trip_id}", response_model=ApiResponse[TripDetailOut])
def get_trip(
    trip_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[TripDetailOut]:
    data = TripService(db).get_trip(trip_id=trip_id, user_id=current_user.id)
    return ApiResponse(success=True, message="OK", data=data)


@router.patch("/{trip_id}", response_model=ApiResponse[TripDetailOut])
def update_trip(
    trip_id: UUID,
    payload: TripUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[TripDetailOut]:
    data = TripService(db).update_trip(
        trip_id=trip_id,
        user_id=current_user.id,
        payload=payload,
    )
    return ApiResponse(success=True, message="Trip updated", data=data)


@router.delete("/{trip_id}", response_model=ApiResponse[dict])
def delete_trip(
    trip_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[dict]:
    TripService(db).delete_trip(trip_id=trip_id, user_id=current_user.id)
    return ApiResponse(success=True, message="Trip deleted", data={"deleted": True})


@router.post(
    "/{trip_id}/days",
    response_model=ApiResponse[TripDetailOut],
    status_code=status.HTTP_201_CREATED,
)
def add_day(
    trip_id: UUID,
    payload: TripDayCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[TripDetailOut]:
    data = TripService(db).add_day(
        trip_id=trip_id,
        user_id=current_user.id,
        payload=payload,
    )
    return ApiResponse(success=True, message="Day added", data=data)


@router.patch("/{trip_id}/days/{day_id}", response_model=ApiResponse[TripDetailOut])
def update_day(
    trip_id: UUID,
    day_id: UUID,
    payload: TripDayUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[TripDetailOut]:
    data = TripService(db).update_day(
        trip_id=trip_id,
        day_id=day_id,
        user_id=current_user.id,
        payload=payload,
    )
    return ApiResponse(success=True, message="Day updated", data=data)


@router.delete("/{trip_id}/days/{day_id}", response_model=ApiResponse[TripDetailOut])
def delete_day(
    trip_id: UUID,
    day_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[TripDetailOut]:
    data = TripService(db).delete_day(
        trip_id=trip_id,
        day_id=day_id,
        user_id=current_user.id,
    )
    return ApiResponse(success=True, message="Day removed", data=data)


@router.post(
    "/{trip_id}/days/{day_id}/places",
    response_model=ApiResponse[TripDetailOut],
    status_code=status.HTTP_201_CREATED,
)
def add_place(
    trip_id: UUID,
    day_id: UUID,
    payload: TripPlaceCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[TripDetailOut]:
    data = TripService(db).add_place(
        trip_id=trip_id,
        day_id=day_id,
        user_id=current_user.id,
        payload=payload,
    )
    return ApiResponse(success=True, message="Stop added", data=data)


@router.delete(
    "/{trip_id}/days/{day_id}/places/{stop_id}",
    response_model=ApiResponse[TripDetailOut],
)
def remove_place(
    trip_id: UUID,
    day_id: UUID,
    stop_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[TripDetailOut]:
    data = TripService(db).remove_place(
        trip_id=trip_id,
        day_id=day_id,
        stop_id=stop_id,
        user_id=current_user.id,
    )
    return ApiResponse(success=True, message="Stop removed", data=data)


@router.post("/{trip_id}/share", response_model=ApiResponse[TripShareOut])
def share_trip(
    trip_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[TripShareOut]:
    data = TripService(db).enable_share(trip_id=trip_id, user_id=current_user.id)
    return ApiResponse(success=True, message="Share link ready", data=data)
