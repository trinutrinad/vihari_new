"""Hotel and room inventory models."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
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

if TYPE_CHECKING:
    from app.models.geo import City
    from app.models.user import User


class Hotel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "hotels"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_hotels_slug"),
        Index("ix_hotels_city_id", "city_id"),
        Index("ix_hotels_name", "name"),
    )

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    rating_avg: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=Decimal("0.00"), nullable=False
    )
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    starting_price_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_ac: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_parking: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_breakfast: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_pool: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_family_friendly: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_couple_friendly: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cancellation_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    hero_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    city: Mapped[City] = relationship()
    owner: Mapped[User | None] = relationship()
    rooms: Mapped[list[HotelRoom]] = relationship(
        back_populates="hotel",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list[HotelReview]] = relationship(
        back_populates="hotel",
        cascade="all, delete-orphan",
    )


class HotelRoom(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "hotel_rooms"
    __table_args__ = (Index("ix_hotel_rooms_hotel_id", "hotel_id"),)

    hotel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    max_guests: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    price_per_night_inr: Mapped[int] = mapped_column(Integer, nullable=False)
    total_rooms: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    hotel: Mapped[Hotel] = relationship(back_populates="rooms")


class HotelReview(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "hotel_reviews"
    __table_args__ = (
        UniqueConstraint("hotel_id", "user_id", name="uq_hotel_reviews_hotel_user"),
        Index("ix_hotel_reviews_hotel_id", "hotel_id"),
    )

    hotel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_moderated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    hotel: Mapped[Hotel] = relationship(back_populates="reviews")
    user: Mapped[User] = relationship()
