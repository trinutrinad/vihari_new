"""Trip planning and itinerary models."""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import TripStatus

if TYPE_CHECKING:
    from app.models.place import TouristPlace
    from app.models.user import User


class Trip(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "trips"
    __table_args__ = (
        Index("ix_trips_user_id", "user_id"),
        Index("ix_trips_status", "status"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    origin_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    destination_summary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    budget_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        default=TripStatus.DRAFT.value,
        nullable=False,
    )
    ai_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    share_code: Mapped[str | None] = mapped_column(String(32), unique=True, nullable=True)

    user: Mapped[User] = relationship(back_populates="trips")
    days: Mapped[list[TripDay]] = relationship(
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="TripDay.day_number",
    )


class TripDay(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "trip_days"
    __table_args__ = (
        UniqueConstraint("trip_id", "day_number", name="uq_trip_days_trip_day_number"),
        Index("ix_trip_days_trip_id", "trip_id"),
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    trip: Mapped[Trip] = relationship(back_populates="days")
    places: Mapped[list[TripPlace]] = relationship(
        back_populates="trip_day",
        cascade="all, delete-orphan",
        order_by="TripPlace.sort_order",
    )


class TripPlace(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "trip_places"
    __table_args__ = (Index("ix_trip_places_trip_day_id", "trip_day_id"),)

    trip_day_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trip_days.id", ondelete="CASCADE"),
        nullable=False,
    )
    place_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tourist_places.id", ondelete="SET NULL"),
        nullable=True,
    )
    custom_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    time_slot: Mapped[str | None] = mapped_column(String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_cost_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    trip_day: Mapped[TripDay] = relationship(back_populates="places")
    place: Mapped[TouristPlace | None] = relationship()
