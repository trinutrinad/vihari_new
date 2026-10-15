"""Booking API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

BookingResourceType = Literal[
    "hotel",
    "guide",
    "activity",
    "transport",
    "restaurant",
]


class BookingCreate(BaseModel):
    resource_type: BookingResourceType
    resource_id: UUID
    scheduled_at: datetime | None = None
    notes: str | None = Field(default=None, max_length=500)
    nights: int | None = Field(default=None, ge=1, le=30)
    duration_days: int | None = Field(default=None, ge=1, le=30)
    participants: int | None = Field(default=None, ge=1, le=50)
    distance_km: float | None = Field(default=None, gt=0, le=2000)


class BookingCancel(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class BookingSummaryOut(BaseModel):
    id: UUID
    booking_number: str
    resource_type: str
    resource_id: UUID
    resource_title: str
    resource_href: str | None = None
    status: str
    scheduled_at: datetime | None = None
    amount_inr: int
    currency: str = "INR"
    provider: str | None = None
    location_text: str | None = None
    is_mock: bool = True
    created_at: datetime | None = None


class BookingDetailOut(BookingSummaryOut):
    cancellation_reason: str | None = None
    notes: str | None = None
    metadata: dict | None = None
    data_notice: str = (
        "Mock bookings confirm instantly for demo UX. "
        "Pay with mock UPI/wallet/card from the booking — no real charges."
    )
