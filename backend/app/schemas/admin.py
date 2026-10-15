"""Admin dashboard API schemas (Phase 22)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AdminAccessOut(BaseModel):
    has_access: bool
    roles: list[str] = Field(default_factory=list)


class AdminSummaryOut(BaseModel):
    users_total: int
    users_active: int
    places_total: int
    hotels_total: int
    restaurants_total: int
    guides_total: int
    activities_total: int
    bookings_total: int
    bookings_open: int
    payments_captured_total: int
    revenue_captured_inr: int
    support_tickets_open: int
    seed_entities_total: int
    data_notice: str = (
        "Platform-wide mock admin overview. "
        "Not a production CMS — seed/demo rows remain unmarked as official."
    )


class AdminUserOut(BaseModel):
    id: UUID
    full_name: str
    email: str | None = None
    phone: str | None = None
    primary_role: str
    is_active: bool
    is_seed_data: bool
    created_at: datetime | None = None


class AdminBookingOut(BaseModel):
    id: UUID
    booking_number: str
    resource_type: str
    resource_id: UUID
    status: str
    amount_inr: int
    currency: str = "INR"
    user_id: UUID
    created_at: datetime | None = None


class AdminPaymentOut(BaseModel):
    id: UUID
    payment_number: str
    amount_inr: int
    status: str
    method: str
    user_id: UUID
    booking_id: UUID | None = None
    is_mock: bool = True
    created_at: datetime | None = None


class AdminTicketOut(BaseModel):
    id: UUID
    ticket_number: str
    subject: str
    status: str
    priority: str
    user_id: UUID
    created_at: datetime | None = None
