"""Business dashboard API schemas (Phase 21)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BusinessAccessOut(BaseModel):
    has_access: bool
    roles: list[str] = Field(default_factory=list)
    hotels_count: int = 0
    restaurants_count: int = 0
    guides_count: int = 0


class BusinessPropertyOut(BaseModel):
    id: UUID
    resource_type: str
    name: str
    slug: str | None = None
    city_name: str | None = None
    rating_avg: float | None = None
    rating_count: int = 0
    href: str | None = None
    is_seed_data: bool = False


class BusinessBookingOut(BaseModel):
    id: UUID
    booking_number: str
    resource_type: str
    resource_id: UUID
    resource_title: str
    status: str
    amount_inr: int
    currency: str = "INR"
    scheduled_at: datetime | None = None
    location_text: str | None = None
    created_at: datetime | None = None
    is_mock: bool = True


class BusinessSummaryOut(BaseModel):
    hotels_count: int
    restaurants_count: int
    guides_count: int
    bookings_total: int
    bookings_pending: int
    bookings_confirmed: int
    bookings_cancelled: int
    bookings_completed: int
    revenue_captured_inr: int
    data_notice: str = (
        "Owner-scoped mock dashboard for demo properties. "
        "Not a live PMS or payment settlement console."
    )
