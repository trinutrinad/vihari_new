"""Tourist place API schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PlaceCategoryOut(BaseModel):
    id: UUID
    name: str
    slug: str
    icon: str | None = None


class PlaceImageOut(BaseModel):
    id: UUID
    url: str
    caption: str | None = None
    is_cover: bool = False
    sort_order: int = 0


class PlaceSummaryOut(BaseModel):
    id: UUID
    name: str
    slug: str
    short_description: str | None = None
    city_name: str
    state_name: str
    state_code: str
    category: PlaceCategoryOut | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    rating_avg: Decimal
    rating_count: int
    estimated_cost_inr: int | None = None
    hero_image_url: str | None = None
    is_featured: bool = False
    is_hidden_gem: bool = False
    is_family_friendly: bool = True
    is_couple_friendly: bool = True
    is_pet_friendly: bool = False
    provenance: str
    is_seed_data: bool = False
    distance_km: float | None = None


class NearbyAmenityOut(BaseModel):
    """Non-verified amenity hints for map UX. Never treat as official data."""

    name: str
    kind: str
    note: str
    provenance: str = "unverified"


class PlaceDetailOut(PlaceSummaryOut):
    description: str | None = None
    address: str | None = None
    best_time_to_visit: str | None = None
    opening_hours: str | None = None
    entry_fee_notes: str | None = None
    facilities: str | None = None
    how_to_reach: str | None = None
    images: list[PlaceImageOut] = Field(default_factory=list)
    nearby_places: list[PlaceSummaryOut] = Field(default_factory=list)
    nearby_hotels: list[dict] = Field(default_factory=list)
    nearby_restaurants: list[dict] = Field(default_factory=list)
    nearby_amenities: list[NearbyAmenityOut] = Field(default_factory=list)
    is_saved: bool = False
    data_notice: str = (
        "Official timings and fees are not fabricated. "
        "Verify on-site or via official sources before travel."
    )


class SavedPlaceOut(BaseModel):
    place_id: UUID
    saved: bool
