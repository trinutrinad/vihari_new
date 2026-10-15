"""Activities API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.schemas.activities import ActivityDetailOut, ActivitySummaryOut
from app.schemas.common import ApiResponse
from app.schemas.pagination import PaginatedData
from app.services.activities import ActivityService

router = APIRouter(prefix="/activities")


@router.get("", response_model=ApiResponse[PaginatedData[ActivitySummaryOut]])
def list_activities(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
    city: str | None = None,
    state: str | None = None,
    q: str | None = None,
    category: str | None = None,
    max_price: Annotated[int | None, Query(ge=0)] = None,
    lat: float | None = None,
    lng: float | None = None,
) -> ApiResponse[PaginatedData[ActivitySummaryOut]]:
    data = ActivityService(db).list_activities(
        page=page,
        page_size=page_size,
        city_slug=city,
        state_code=state,
        q=q,
        category=category,
        max_price=max_price,
        lat=lat,
        lng=lng,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/nearby", response_model=ApiResponse[list[ActivitySummaryOut]])
def nearby_activities(
    db: DbSession,
    lat: Annotated[float, Query()],
    lng: Annotated[float, Query()],
    radius_km: Annotated[float, Query(gt=0, le=500)] = 80,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> ApiResponse[list[ActivitySummaryOut]]:
    data = ActivityService(db).nearby(
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        limit=limit,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/by-slug/{slug}", response_model=ApiResponse[ActivityDetailOut])
def get_activity_by_slug(slug: str, db: DbSession) -> ApiResponse[ActivityDetailOut]:
    data = ActivityService(db).get_activity(slug=slug)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/{activity_id}", response_model=ApiResponse[ActivityDetailOut])
def get_activity(activity_id: UUID, db: DbSession) -> ApiResponse[ActivityDetailOut]:
    data = ActivityService(db).get_activity(activity_id=activity_id)
    return ApiResponse(success=True, message="OK", data=data)
