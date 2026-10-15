"""Global search API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.schemas.common import ApiResponse
from app.schemas.search import (
    AutocompleteSuggestion,
    SearchResponseData,
    TrendingSearchesData,
)
from app.services.search import SearchService, parse_types

router = APIRouter(prefix="/search")


@router.get("", response_model=ApiResponse[SearchResponseData])
def search(
    db: DbSession,
    q: Annotated[str, Query(min_length=0, max_length=200)] = "",
    types: Annotated[str | None, Query(description="Comma-separated entity types")] = None,
    category: str | None = None,
    state: str | None = None,
    min_rating: Annotated[float | None, Query(ge=0, le=5)] = None,
    max_cost: Annotated[int | None, Query(ge=0)] = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_km: Annotated[float | None, Query(gt=0, le=1000)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
) -> ApiResponse[SearchResponseData]:
    data = SearchService(db).search(
        query=q,
        types=parse_types(types),
        category=category,
        state=state,
        min_rating=min_rating,
        max_cost=max_cost,
        lat=lat,
        lng=lng,
        radius_km=radius_km,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/autocomplete", response_model=ApiResponse[list[AutocompleteSuggestion]])
def autocomplete(
    db: DbSession,
    q: Annotated[str, Query(min_length=1, max_length=120)],
    limit: Annotated[int, Query(ge=1, le=20)] = 8,
) -> ApiResponse[list[AutocompleteSuggestion]]:
    data = SearchService(db).autocomplete(query=q, limit=limit)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/trending", response_model=ApiResponse[TrendingSearchesData])
def trending(db: DbSession) -> ApiResponse[TrendingSearchesData]:
    data = SearchService(db).trending()
    return ApiResponse(success=True, message="OK", data=data)
