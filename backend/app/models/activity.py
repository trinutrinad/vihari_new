"""Activity catalog and bookings."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import BookingStatus

if TYPE_CHECKING:
    from app.models.geo import City
    from app.models.user import User


class Activity(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "activities"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_activities_slug"),
        Index("ix_activities_city_id", "city_id"),
        Index("ix_activities_name", "name"),
    )

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    price_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    safety_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    rating_avg: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=Decimal("0.00"), nullable=False
    )
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hero_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    city: Mapped[City] = relationship()
    bookings: Mapped[list[ActivityBooking]] = relationship(back_populates="activity")


class ActivityBooking(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "activity_bookings"
    __table_args__ = (
        Index("ix_activity_bookings_activity_id", "activity_id"),
        Index("ix_activity_bookings_user_id", "user_id"),
        UniqueConstraint("booking_number", name="uq_activity_bookings_booking_number"),
    )

    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    booking_number: Mapped[str] = mapped_column(String(40), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    participants: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_amount_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default=BookingStatus.PENDING.value,
        nullable=False,
    )
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    activity: Mapped[Activity] = relationship(back_populates="bookings")
    user: Mapped[User] = relationship()
