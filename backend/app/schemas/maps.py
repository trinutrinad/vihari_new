"""Map API schemas — lightweight pins for Leaflet/OSM."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class MapPinOut(BaseModel):
    id: UUID
    name: str
    slug: str
    entity_type: str = "place"
    latitude: Decimal
    longitude: Decimal
    city_name: str
    state_code: str
    category_slug: str | None = None
    rating_avg: Decimal
    is_seed_data: bool = False
    href: str


class CityMapCenterOut(BaseModel):
    id: UUID
    name: str
    slug: str
    state_code: str
    latitude: Decimal
    longitude: Decimal
    place_count: int = 0
    is_seed_data: bool = False


class MapPinsData(BaseModel):
    pins: list[MapPinOut] = Field(default_factory=list)
    total: int = 0
    provider: str = "leaflet_osm"
    notice: str = (
        "Map pins use seed/demo coordinates where marked. "
        "Verify locations before travel."
    )
