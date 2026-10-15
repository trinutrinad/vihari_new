"""Tourist places API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DbSession, get_current_user_optional
from app.models import User
from app.schemas.common import ApiResponse
from app.schemas.pagination import PaginatedData
from app.schemas.places import (
    PlaceCategoryOut,
    PlaceDetailOut,
    PlaceSummaryOut,
    SavedPlaceOut,
)
from app.services.places import PlaceService

router = APIRouter(prefix="/places")


@router.get("", response_model=ApiResponse[PaginatedData[PlaceSummaryOut]])
def list_places(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
    category: str | None = None,
    state: str | None = None,
    city: str | None = None,
    featured: bool | None = None,
    hidden_gem: bool | None = None,
    family_friendly: bool | None = None,
    q: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
) -> ApiResponse[PaginatedData[PlaceSummaryOut]]:
    data = PlaceService(db).list_places(
        page=page,
        page_size=page_size,
        category=category,
        state_code=state,
        city_slug=city,
        featured=featured,
        hidden_gem=hidden_gem,
        family_friendly=family_friendly,
        q=q,
        lat=lat,
        lng=lng,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/categories", response_model=ApiResponse[list[PlaceCategoryOut]])
def list_categories(db: DbSession) -> ApiResponse[list[PlaceCategoryOut]]:
    return ApiResponse(success=True, message="OK", data=PlaceService(db).list_categories())


@router.get("/nearby", response_model=ApiResponse[list[PlaceSummaryOut]])
def nearby_places(
    db: DbSession,
    lat: Annotated[float, Query()],
    lng: Annotated[float, Query()],
    radius_km: Annotated[float, Query(gt=0, le=500)] = 50,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> ApiResponse[list[PlaceSummaryOut]]:
    data = PlaceService(db).nearby(lat=lat, lng=lng, radius_km=radius_km, limit=limit)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/saved", response_model=ApiResponse[list[PlaceSummaryOut]])
def list_saved_places(
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[list[PlaceSummaryOut]]:
    data = PlaceService(db).list_saved(user_id=current_user.id)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/by-slug/{slug}", response_model=ApiResponse[PlaceDetailOut])
def get_place_by_slug(
    slug: str,
    db: DbSession,
    current_user: Annotated[User | None, Depends(get_current_user_optional)] = None,
) -> ApiResponse[PlaceDetailOut]:
    data = PlaceService(db).get_place(
        slug=slug,
        user_id=current_user.id if current_user else None,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/{place_id}", response_model=ApiResponse[PlaceDetailOut])
def get_place(
    place_id: UUID,
    db: DbSession,
    current_user: Annotated[User | None, Depends(get_current_user_optional)] = None,
) -> ApiResponse[PlaceDetailOut]:
    data = PlaceService(db).get_place(
        place_id=place_id,
        user_id=current_user.id if current_user else None,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.post(
    "/{place_id}/save",
    response_model=ApiResponse[SavedPlaceOut],
    status_code=status.HTTP_201_CREATED,
)
def save_place(
    place_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[SavedPlaceOut]:
    data = PlaceService(db).save(user_id=current_user.id, place_id=place_id)
    return ApiResponse(success=True, message="Place saved", data=data)


@router.delete("/{place_id}/save", response_model=ApiResponse[SavedPlaceOut])
def unsave_place(
    place_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[SavedPlaceOut]:
    data = PlaceService(db).unsave(user_id=current_user.id, place_id=place_id)
    return ApiResponse(success=True, message="Place removed from saved", data=data)
