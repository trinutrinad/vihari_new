"""Global search request/response schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    id: UUID | str
    entity_type: str
    title: str
    subtitle: str | None = None
    slug: str | None = None
    category: str | None = None
    location_label: str | None = None
    rating_avg: Decimal | float | None = None
    estimated_cost_inr: int | None = None
    latitude: Decimal | float | None = None
    longitude: Decimal | float | None = None
    distance_km: float | None = None
    is_seed_data: bool = False
    href: str


class SearchResponseData(BaseModel):
    query: str
    total: int
    items: list[SearchResultItem]
    facets: dict[str, int] = Field(default_factory=dict)
    page: int = 1
    page_size: int = 20


class AutocompleteSuggestion(BaseModel):
    label: str
    entity_type: str
    id: UUID | str | None = None
    slug: str | None = None
    href: str | None = None


class TrendingSearchesData(BaseModel):
    queries: list[str]
    places: list[SearchResultItem] = Field(default_factory=list)
