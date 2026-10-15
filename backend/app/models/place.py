"""Tourist places, categories, images, reviews, and saved places."""

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
from app.models.enums import DataProvenance

if TYPE_CHECKING:
    from app.models.geo import City
    from app.models.user import User


class PlaceCategory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "place_categories"
    __table_args__ = (UniqueConstraint("slug", name="uq_place_categories_slug"),)

    name: Mapped[str] = mapped_column(String(80), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    places: Mapped[list[TouristPlace]] = relationship(back_populates="category")


class TouristPlace(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tourist_places"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_tourist_places_slug"),
        Index("ix_tourist_places_city_id", "city_id"),
        Index("ix_tourist_places_category_id", "category_id"),
        Index("ix_tourist_places_name", "name"),
        Index("ix_tourist_places_rating", "rating_avg"),
    )

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("place_categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    rating_avg: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=Decimal("0.00"), nullable=False
    )
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    best_time_to_visit: Mapped[str | None] = mapped_column(String(255), nullable=True)
    opening_hours: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Unverified/community hours unless provenance is official",
    )
    entry_fee_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    facilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    how_to_reach: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_family_friendly: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_couple_friendly: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_pet_friendly: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_hidden_gem: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hero_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    provenance: Mapped[str] = mapped_column(
        String(32),
        default=DataProvenance.SEED_DEMO.value,
        nullable=False,
    )
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    city: Mapped[City] = relationship(back_populates="places")
    category: Mapped[PlaceCategory | None] = relationship(back_populates="places")
    images: Mapped[list[PlaceImage]] = relationship(
        back_populates="place",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list[PlaceReview]] = relationship(
        back_populates="place",
        cascade="all, delete-orphan",
    )


class PlaceImage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "place_images"
    __table_args__ = (Index("ix_place_images_place_id", "place_id"),)

    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tourist_places.id", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    place: Mapped[TouristPlace] = relationship(back_populates="images")


class PlaceReview(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "place_reviews"
    __table_args__ = (
        UniqueConstraint("place_id", "user_id", name="uq_place_reviews_place_user"),
        Index("ix_place_reviews_place_id", "place_id"),
    )

    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tourist_places.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_moderated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    place: Mapped[TouristPlace] = relationship(back_populates="reviews")
    user: Mapped[User] = relationship()


class SavedPlace(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "saved_places"
    __table_args__ = (
        UniqueConstraint("user_id", "place_id", name="uq_saved_places_user_place"),
        Index("ix_saved_places_user_id", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tourist_places.id", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped[User] = relationship()
    place: Mapped[TouristPlace] = relationship()
