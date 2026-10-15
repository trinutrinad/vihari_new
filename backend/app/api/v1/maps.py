"""Maps API — viewport pins and city centers for Leaflet."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.schemas.common import ApiResponse
from app.schemas.maps import CityMapCenterOut, MapPinsData
from app.services.maps import MapService

router = APIRouter(prefix="/maps")


@router.get("/pins", response_model=ApiResponse[MapPinsData])
def map_pins(
    db: DbSession,
    north: Annotated[float, Query(ge=-90, le=90)],
    south: Annotated[float, Query(ge=-90, le=90)],
    east: Annotated[float, Query(ge=-180, le=180)],
    west: Annotated[float, Query(ge=-180, le=180)],
    category: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> ApiResponse[MapPinsData]:
    data = MapService(db).pins_in_bounds(
        north=north,
        south=south,
        east=east,
        west=west,
        category=category,
        limit=limit,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/cities", response_model=ApiResponse[list[CityMapCenterOut]])
def map_cities(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> ApiResponse[list[CityMapCenterOut]]:
    data = MapService(db).city_centers(limit=limit)
    return ApiResponse(success=True, message="OK", data=data)
