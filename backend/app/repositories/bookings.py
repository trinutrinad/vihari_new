"""Booking data-access helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking


class BookingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_user(
        self,
        *,
        user_id: uuid.UUID,
        status: str | None = None,
        resource_type: str | None = None,
    ) -> list[Booking]:
        query = select(Booking).where(Booking.user_id == user_id)
        if status:
            query = query.where(Booking.status == status.strip().lower())
        if resource_type:
            query = query.where(Booking.resource_type == resource_type.strip().lower())
        return list(
            self.db.scalars(query.order_by(Booking.created_at.desc())).all(),
        )

    def get_for_user(
        self,
        *,
        booking_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Booking | None:
        return self.db.scalar(
            select(Booking).where(
                Booking.id == booking_id,
                Booking.user_id == user_id,
            ),
        )

    def add(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.flush()
        return booking
