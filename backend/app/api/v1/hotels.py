"""Hotels API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.schemas.common import ApiResponse
from app.schemas.hotels import HotelDetailOut, HotelSummaryOut
from app.schemas.pagination import PaginatedData
from app.services.hotels import HotelService

router = APIRouter(prefix="/hotels")


@router.get("", response_model=ApiResponse[PaginatedData[HotelSummaryOut]])
def list_hotels(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
    city: str | None = None,
    state: str | None = None,
    q: str | None = None,
    min_price: Annotated[int | None, Query(ge=0)] = None,
    max_price: Annotated[int | None, Query(ge=0)] = None,
    wifi: bool | None = None,
    breakfast: bool | None = None,
    parking: bool | None = None,
    pool: bool | None = None,
    family_friendly: bool | None = None,
    lat: float | None = None,
    lng: float | None = None,
) -> ApiResponse[PaginatedData[HotelSummaryOut]]:
    data = HotelService(db).list_hotels(
        page=page,
        page_size=page_size,
        city_slug=city,
        state_code=state,
        q=q,
        min_price=min_price,
        max_price=max_price,
        has_wifi=wifi,
        has_breakfast=breakfast,
        has_parking=parking,
        has_pool=pool,
        family_friendly=family_friendly,
        lat=lat,
        lng=lng,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/nearby", response_model=ApiResponse[list[HotelSummaryOut]])
def nearby_hotels(
    db: DbSession,
    lat: Annotated[float, Query()],
    lng: Annotated[float, Query()],
    radius_km: Annotated[float, Query(gt=0, le=500)] = 50,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> ApiResponse[list[HotelSummaryOut]]:
    data = HotelService(db).nearby(lat=lat, lng=lng, radius_km=radius_km, limit=limit)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/by-slug/{slug}", response_model=ApiResponse[HotelDetailOut])
def get_hotel_by_slug(slug: str, db: DbSession) -> ApiResponse[HotelDetailOut]:
    data = HotelService(db).get_hotel(slug=slug)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/{hotel_id}", response_model=ApiResponse[HotelDetailOut])
def get_hotel(hotel_id: UUID, db: DbSession) -> ApiResponse[HotelDetailOut]:
    data = HotelService(db).get_hotel(hotel_id=hotel_id)
    return ApiResponse(success=True, message="OK", data=data)
