"""Geographic reference models: states and cities."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.place import TouristPlace


class State(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "states"
    __table_args__ = (
        UniqueConstraint("code", name="uq_states_code"),
        Index("ix_states_name", "name"),
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    is_union_territory: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    cities: Mapped[list[City]] = relationship(back_populates="state", cascade="all, delete-orphan")


class City(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cities"
    __table_args__ = (
        UniqueConstraint("state_id", "slug", name="uq_cities_state_slug"),
        Index("ix_cities_name", "name"),
        Index("ix_cities_state_id", "state_id"),
    )

    state_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("states.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    state: Mapped[State] = relationship(back_populates="cities")
    places: Mapped[list[TouristPlace]] = relationship(back_populates="city")
