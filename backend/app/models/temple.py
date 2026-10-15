"""Temple tourism models. Official timings must not be fabricated."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import DataProvenance

if TYPE_CHECKING:
    from app.models.place import TouristPlace


class Temple(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "temples"
    __table_args__ = (
        UniqueConstraint("place_id", name="uq_temples_place_id"),
        Index("ix_temples_name", "name"),
    )

    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tourist_places.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    deity: Mapped[str | None] = mapped_column(String(160), nullable=True)
    history: Mapped[str | None] = mapped_column(Text, nullable=True)
    festival_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    entry_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    prasadam_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    parking_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    accommodation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance: Mapped[str] = mapped_column(
        String(32),
        default=DataProvenance.UNVERIFIED.value,
        nullable=False,
    )
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    place: Mapped[TouristPlace] = relationship()
    timings: Mapped[list[TempleTiming]] = relationship(
        back_populates="temple",
        cascade="all, delete-orphan",
    )


class TempleTiming(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "temple_timings"
    __table_args__ = (Index("ix_temple_timings_temple_id", "temple_id"),)

    temple_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("temples.id", ondelete="CASCADE"),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    provenance: Mapped[str] = mapped_column(
        String(32),
        default=DataProvenance.UNVERIFIED.value,
        nullable=False,
    )
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    temple: Mapped[Temple] = relationship(back_populates="timings")
