"""Guide API schemas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class GuideAvailabilityOut(BaseModel):
    id: UUID
    available_date: date
    is_available: bool = True


class GuideSummaryOut(BaseModel):
    id: UUID
    display_name: str
    bio: str | None = None
    languages: str
    specialization: str | None = None
    experience_years: int = 0
    price_per_day_inr: int
    rating_avg: Decimal
    rating_count: int
    profile_image_url: str | None = None
    city_name: str
    state_name: str
    state_code: str
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_active: bool = True
    is_seed_data: bool = False
    distance_km: float | None = None
    provenance: str = "seed_demo"


class GuideDetailOut(GuideSummaryOut):
    availability: list[GuideAvailabilityOut] = Field(default_factory=list)
    data_notice: str = (
        "Seed/demo guides are fictional profiles for discovery UX. "
        "Live booking arrives later — verify credentials independently."
    )
