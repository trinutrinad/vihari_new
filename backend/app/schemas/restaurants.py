"""Restaurant API schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class MenuItemOut(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    price_inr: int
    is_veg: bool = True
    is_available: bool = True


class RestaurantSummaryOut(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None = None
    cuisine_tags: str | None = None
    city_name: str
    state_name: str
    state_code: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    rating_avg: Decimal
    rating_count: int
    price_level: int = 2
    is_vegetarian: bool = False
    is_street_food: bool = False
    hero_image_url: str | None = None
    is_seed_data: bool = False
    distance_km: float | None = None
    provenance: str = "seed_demo"


class RestaurantDetailOut(RestaurantSummaryOut):
    address: str | None = None
    opening_hours: str | None = None
    menu_items: list[MenuItemOut] = Field(default_factory=list)
    data_notice: str = (
        "Seed/demo restaurants are fictional for food-discovery UX. "
        "Official hours and live menus are not verified — confirm locally."
    )
