"""Guides API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.schemas.common import ApiResponse
from app.schemas.guides import GuideDetailOut, GuideSummaryOut
from app.schemas.pagination import PaginatedData
from app.services.guides import GuideService

router = APIRouter(prefix="/guides")


@router.get("", response_model=ApiResponse[PaginatedData[GuideSummaryOut]])
def list_guides(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
    city: str | None = None,
    state: str | None = None,
    q: str | None = None,
    language: str | None = None,
    specialization: str | None = None,
    max_price: Annotated[int | None, Query(ge=0)] = None,
    lat: float | None = None,
    lng: float | None = None,
) -> ApiResponse[PaginatedData[GuideSummaryOut]]:
    data = GuideService(db).list_guides(
        page=page,
        page_size=page_size,
        city_slug=city,
        state_code=state,
        q=q,
        language=language,
        specialization=specialization,
        max_price=max_price,
        lat=lat,
        lng=lng,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/nearby", response_model=ApiResponse[list[GuideSummaryOut]])
def nearby_guides(
    db: DbSession,
    lat: Annotated[float, Query()],
    lng: Annotated[float, Query()],
    radius_km: Annotated[float, Query(gt=0, le=500)] = 80,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> ApiResponse[list[GuideSummaryOut]]:
    data = GuideService(db).nearby(lat=lat, lng=lng, radius_km=radius_km, limit=limit)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/{guide_id}", response_model=ApiResponse[GuideDetailOut])
def get_guide(guide_id: UUID, db: DbSession) -> ApiResponse[GuideDetailOut]:
    data = GuideService(db).get_guide(guide_id=guide_id)
    return ApiResponse(success=True, message="OK", data=data)
