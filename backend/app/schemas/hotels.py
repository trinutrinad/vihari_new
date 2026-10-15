"""Hotel API schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class HotelRoomOut(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    max_guests: int
    price_per_night_inr: int
    total_rooms: int
    is_available: bool


class HotelSummaryOut(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None = None
    city_name: str
    state_name: str
    state_code: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    rating_avg: Decimal
    rating_count: int
    starting_price_inr: int | None = None
    has_ac: bool = True
    has_wifi: bool = True
    has_parking: bool = False
    has_breakfast: bool = False
    has_pool: bool = False
    is_family_friendly: bool = True
    is_couple_friendly: bool = True
    hero_image_url: str | None = None
    is_seed_data: bool = False
    distance_km: float | None = None
    provenance: str = "seed_demo"


class HotelDetailOut(HotelSummaryOut):
    address: str | None = None
    cancellation_policy: str | None = None
    rooms: list[HotelRoomOut] = Field(default_factory=list)
    data_notice: str = (
        "Seed/demo hotels are fictional inventory for UX testing. "
        "Live booking arrives in a later phase — verify real properties independently."
    )
