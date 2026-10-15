"""Trip planning API schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.enums import TripStatus


class TripPlaceCreate(BaseModel):
    place_id: UUID | None = None
    custom_title: str | None = Field(default=None, max_length=200)
    time_slot: str | None = Field(default=None, max_length=40)
    notes: str | None = None
    estimated_cost_inr: int | None = Field(default=None, ge=0)
    sort_order: int = Field(default=0, ge=0)


class TripDayCreate(BaseModel):
    day_number: int = Field(ge=1, le=60)
    title: str | None = Field(default=None, max_length=160)
    notes: str | None = None
    places: list[TripPlaceCreate] = Field(default_factory=list)


class TripCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    summary: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    origin_city: str | None = Field(default=None, max_length=120)
    destination_summary: str | None = Field(default=None, max_length=255)
    budget_inr: int | None = Field(default=None, ge=0)
    status: TripStatus = TripStatus.DRAFT
    is_ai_generated: bool = False
    ai_prompt: str | None = None
    days: list[TripDayCreate] = Field(default_factory=list)

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, value: date | None, info) -> date | None:
        start = info.data.get("start_date")
        if value and start and value < start:
            raise ValueError("end_date must be on or after start_date")
        return value


class TripUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    summary: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    origin_city: str | None = Field(default=None, max_length=120)
    destination_summary: str | None = Field(default=None, max_length=255)
    budget_inr: int | None = Field(default=None, ge=0)
    status: TripStatus | None = None


class TripDayUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=160)
    notes: str | None = None


class TripPlaceOut(BaseModel):
    id: UUID
    place_id: UUID | None = None
    custom_title: str | None = None
    title: str
    time_slot: str | None = None
    notes: str | None = None
    estimated_cost_inr: int | None = None
    sort_order: int
    place_slug: str | None = None
    city_name: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    is_seed_data: bool = False


class TripDayOut(BaseModel):
    id: UUID
    day_number: int
    title: str | None = None
    notes: str | None = None
    places: list[TripPlaceOut] = Field(default_factory=list)


class TripMapPointOut(BaseModel):
    id: str
    label: str
    day_number: int
    latitude: Decimal
    longitude: Decimal
    href: str | None = None


class TripSummaryOut(BaseModel):
    id: UUID
    title: str
    summary: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    origin_city: str | None = None
    destination_summary: str | None = None
    budget_inr: int | None = None
    estimated_cost_inr: int | None = None
    status: str
    is_ai_generated: bool = False
    share_code: str | None = None
    day_count: int = 0
    stop_count: int = 0
    created_at: datetime
    updated_at: datetime


class TripDetailOut(TripSummaryOut):
    days: list[TripDayOut] = Field(default_factory=list)
    map_points: list[TripMapPointOut] = Field(default_factory=list)


class TripShareOut(BaseModel):
    share_code: str
    share_path: str
