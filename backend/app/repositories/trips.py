"""Trip data-access helpers."""

from __future__ import annotations

import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import TouristPlace, Trip, TripDay, TripPlace


class TripRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _detail_options(self):
        return (
            selectinload(Trip.days)
            .selectinload(TripDay.places)
            .selectinload(TripPlace.place)
            .selectinload(TouristPlace.city),
        )

    def list_for_user(
        self,
        *,
        user_id: uuid.UUID,
        status: str | None = None,
    ) -> list[Trip]:
        query = (
            select(Trip)
            .where(Trip.user_id == user_id)
            .options(*self._detail_options())
            .order_by(Trip.updated_at.desc())
        )
        if status:
            query = query.where(Trip.status == status)
        return list(self.db.scalars(query).all())

    def get_for_user(self, *, trip_id: uuid.UUID, user_id: uuid.UUID) -> Trip | None:
        return self.db.scalar(
            select(Trip)
            .where(Trip.id == trip_id, Trip.user_id == user_id)
            .options(*self._detail_options()),
        )

    def get_by_id(self, trip_id: uuid.UUID) -> Trip | None:
        return self.db.scalar(
            select(Trip).where(Trip.id == trip_id).options(*self._detail_options()),
        )

    def get_by_share_code(self, share_code: str) -> Trip | None:
        return self.db.scalar(
            select(Trip)
            .where(Trip.share_code == share_code)
            .options(*self._detail_options()),
        )

    def create(self, trip: Trip) -> Trip:
        self.db.add(trip)
        self.db.commit()
        self.db.refresh(trip)
        return self.get_by_id(trip.id) or trip

    def save(self, trip: Trip) -> Trip:
        self.db.add(trip)
        self.db.commit()
        return self.get_by_id(trip.id) or trip

    def delete(self, trip: Trip) -> None:
        self.db.delete(trip)
        self.db.commit()

    def get_day(self, *, day_id: uuid.UUID, trip_id: uuid.UUID) -> TripDay | None:
        return self.db.scalar(
            select(TripDay)
            .where(TripDay.id == day_id, TripDay.trip_id == trip_id)
            .options(
                selectinload(TripDay.places).selectinload(TripPlace.place).selectinload(
                    TouristPlace.city,
                ),
            ),
        )

    def get_place(self, place_id: uuid.UUID) -> TouristPlace | None:
        return self.db.scalar(
            select(TouristPlace)
            .where(TouristPlace.id == place_id, TouristPlace.is_deleted.is_(False))
            .options(selectinload(TouristPlace.city)),
        )

    @staticmethod
    def new_share_code() -> str:
        return secrets.token_urlsafe(8)[:12]
