"""Activity API schemas."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ActivitySummaryOut(BaseModel):
    id: UUID
    name: str
    slug: str
    category: str
    description: str | None = None
    duration_hours: Decimal | None = None
    price_inr: int
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    rating_avg: Decimal
    rating_count: int
    hero_image_url: str | None = None
    city_name: str
    state_name: str
    state_code: str
    is_available: bool = True
    is_seed_data: bool = False
    distance_km: float | None = None
    provenance: str = "seed_demo"


class ActivityDetailOut(ActivitySummaryOut):
    safety_information: str | None = None
    data_notice: str = Field(
        default=(
            "Seed/demo activities are fictional for discovery UX. "
            "Live booking arrives later — verify operators and safety locally."
        ),
    )
