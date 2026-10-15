"""Restaurants API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.schemas.common import ApiResponse
from app.schemas.pagination import PaginatedData
from app.schemas.restaurants import RestaurantDetailOut, RestaurantSummaryOut
from app.services.restaurants import RestaurantService

router = APIRouter(prefix="/restaurants")


@router.get("", response_model=ApiResponse[PaginatedData[RestaurantSummaryOut]])
def list_restaurants(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
    city: str | None = None,
    state: str | None = None,
    q: str | None = None,
    cuisine: str | None = None,
    vegetarian: bool | None = None,
    street_food: bool | None = None,
    max_price_level: Annotated[int | None, Query(ge=1, le=4)] = None,
    lat: float | None = None,
    lng: float | None = None,
) -> ApiResponse[PaginatedData[RestaurantSummaryOut]]:
    data = RestaurantService(db).list_restaurants(
        page=page,
        page_size=page_size,
        city_slug=city,
        state_code=state,
        q=q,
        cuisine=cuisine,
        vegetarian=vegetarian,
        street_food=street_food,
        max_price_level=max_price_level,
        lat=lat,
        lng=lng,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/nearby", response_model=ApiResponse[list[RestaurantSummaryOut]])
def nearby_restaurants(
    db: DbSession,
    lat: Annotated[float, Query()],
    lng: Annotated[float, Query()],
    radius_km: Annotated[float, Query(gt=0, le=500)] = 50,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> ApiResponse[list[RestaurantSummaryOut]]:
    data = RestaurantService(db).nearby(
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        limit=limit,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/by-slug/{slug}", response_model=ApiResponse[RestaurantDetailOut])
def get_restaurant_by_slug(slug: str, db: DbSession) -> ApiResponse[RestaurantDetailOut]:
    data = RestaurantService(db).get_restaurant(slug=slug)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/{restaurant_id}", response_model=ApiResponse[RestaurantDetailOut])
def get_restaurant(
    restaurant_id: UUID,
    db: DbSession,
) -> ApiResponse[RestaurantDetailOut]:
    data = RestaurantService(db).get_restaurant(restaurant_id=restaurant_id)
    return ApiResponse(success=True, message="OK", data=data)
