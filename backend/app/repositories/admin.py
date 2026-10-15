"""Admin dashboard data access."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.models import (
    Activity,
    Booking,
    Guide,
    Hotel,
    Payment,
    Restaurant,
    SupportTicket,
    TouristPlace,
    User,
)
from app.models.enums import BookingStatus, PaymentStatus


class AdminRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count(self, model: type[Any]) -> int:
        return int(self.db.scalar(select(func.count()).select_from(model)) or 0)

    def count_where(self, model: type[Any], *clauses: ColumnElement[bool]) -> int:
        stmt = select(func.count()).select_from(model)
        if clauses:
            stmt = stmt.where(*clauses)
        return int(self.db.scalar(stmt) or 0)

    def seed_entity_total(self) -> int:
        total = 0
        for model in (TouristPlace, Hotel, Restaurant, Guide, Activity, User):
            total += self.count_where(model, model.is_seed_data.is_(True))
        return total

    def open_bookings(self) -> int:
        return self.count_where(
            Booking,
            Booking.status.in_(
                [
                    BookingStatus.PENDING.value,
                    BookingStatus.CONFIRMED.value,
                    BookingStatus.IN_PROGRESS.value,
                ],
            ),
        )

    def captured_revenue_inr(self) -> int:
        total = self.db.scalar(
            select(func.coalesce(func.sum(Payment.amount_inr), 0)).where(
                Payment.status == PaymentStatus.CAPTURED.value,
            ),
        )
        return int(total or 0)

    def list_users(self, *, limit: int = 50) -> Sequence[User]:
        return list(
            self.db.scalars(
                select(User).order_by(User.created_at.desc()).limit(limit),
            ).all(),
        )

    def list_bookings(self, *, limit: int = 50) -> Sequence[Booking]:
        return list(
            self.db.scalars(
                select(Booking).order_by(Booking.created_at.desc()).limit(limit),
            ).all(),
        )

    def list_payments(self, *, limit: int = 50) -> Sequence[Payment]:
        return list(
            self.db.scalars(
                select(Payment).order_by(Payment.created_at.desc()).limit(limit),
            ).all(),
        )

    def list_tickets(
        self,
        *,
        limit: int = 50,
        open_only: bool = False,
    ) -> Sequence[SupportTicket]:
        stmt = select(SupportTicket).order_by(SupportTicket.created_at.desc()).limit(limit)
        if open_only:
            stmt = stmt.where(SupportTicket.status == "open")
        return list(self.db.scalars(stmt).all())
