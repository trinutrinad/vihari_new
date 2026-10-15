"""Local guide models."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
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
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import BookingStatus

if TYPE_CHECKING:
    from app.models.geo import City
    from app.models.user import User


class Guide(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "guides"
    __table_args__ = (
        Index("ix_guides_city_id", "city_id"),
        Index("ix_guides_user_id", "user_id"),
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    languages: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    price_per_day_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    rating_avg: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=Decimal("0.00"), nullable=False
    )
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User | None] = relationship()
    city: Mapped[City] = relationship()
    availability: Mapped[list[GuideAvailability]] = relationship(
        back_populates="guide",
        cascade="all, delete-orphan",
    )
    bookings: Mapped[list[GuideBooking]] = relationship(back_populates="guide")


class GuideAvailability(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "guide_availability"
    __table_args__ = (
        UniqueConstraint("guide_id", "available_date", name="uq_guide_availability_guide_date"),
        Index("ix_guide_availability_guide_id", "guide_id"),
    )

    guide_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("guides.id", ondelete="CASCADE"),
        nullable=False,
    )
    available_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    guide: Mapped[Guide] = relationship(back_populates="availability")


class GuideBooking(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "guide_bookings"
    __table_args__ = (
        Index("ix_guide_bookings_guide_id", "guide_id"),
        Index("ix_guide_bookings_user_id", "user_id"),
        UniqueConstraint("booking_number", name="uq_guide_bookings_booking_number"),
    )

    guide_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("guides.id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    booking_number: Mapped[str] = mapped_column(String(40), nullable=False)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    total_amount_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default=BookingStatus.PENDING.value,
        nullable=False,
    )
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    guide: Mapped[Guide] = relationship(back_populates="bookings")
    user: Mapped[User] = relationship()
