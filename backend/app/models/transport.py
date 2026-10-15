"""Transport, drivers, vehicles, and rides."""

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
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import RideStatus, VehicleType

if TYPE_CHECKING:
    from app.models.geo import City
    from app.models.user import User


class TransportOption(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "transport_options"
    __table_args__ = (UniqueConstraint("code", name="uq_transport_options_code"),)

    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_fare_inr: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    per_km_inr: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Driver(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "drivers"
    __table_args__ = (Index("ix_drivers_user_id", "user_id"),)

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    city_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="SET NULL"),
        nullable=True,
    )
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    license_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rating_avg: Mapped[Decimal] = mapped_column(
        Numeric(3, 2), default=Decimal("0.00"), nullable=False
    )
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_seed_data: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User | None] = relationship()
    city: Mapped[City | None] = relationship()
    vehicles: Mapped[list[Vehicle]] = relationship(
        back_populates="driver",
        cascade="all, delete-orphan",
    )
    rides: Mapped[list[Ride]] = relationship(back_populates="driver")


class Vehicle(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "vehicles"
    __table_args__ = (
        Index("ix_vehicles_driver_id", "driver_id"),
        UniqueConstraint("registration_number", name="uq_vehicles_registration_number"),
    )

    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="CASCADE"),
        nullable=False,
    )
    vehicle_type: Mapped[str] = mapped_column(
        String(40),
        default=VehicleType.TAXI.value,
        nullable=False,
    )
    make_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    registration_number: Mapped[str] = mapped_column(String(40), nullable=False)
    color: Mapped[str | None] = mapped_column(String(40), nullable=True)
    seats: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    driver: Mapped[Driver] = relationship(back_populates="vehicles")


class Ride(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "rides"
    __table_args__ = (
        Index("ix_rides_user_id", "user_id"),
        Index("ix_rides_driver_id", "driver_id"),
        UniqueConstraint("ride_number", name="uq_rides_ride_number"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True,
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
    )
    ride_number: Mapped[str] = mapped_column(String(40), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(40), nullable=False)
    pickup_address: Mapped[str] = mapped_column(String(500), nullable=False)
    dropoff_address: Mapped[str] = mapped_column(String(500), nullable=False)
    pickup_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    pickup_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    dropoff_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    dropoff_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    estimated_fare_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    final_fare_inr: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distance_km: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    eta_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        default=RideStatus.SEARCHING.value,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_mock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped[User] = relationship()
    driver: Mapped[Driver | None] = relationship(back_populates="rides")
    vehicle: Mapped[Vehicle | None] = relationship()
    locations: Mapped[list[RideLocation]] = relationship(
        back_populates="ride",
        cascade="all, delete-orphan",
    )


class RideLocation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ride_locations"
    __table_args__ = (Index("ix_ride_locations_ride_id", "ride_id"),)

    ride_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rides.id", ondelete="CASCADE"),
        nullable=False,
    )
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    ride: Mapped[Ride] = relationship(back_populates="locations")
