"""Business dashboard data access."""

from __future__ import annotations

import uuid

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Booking, Guide, Hotel, Payment, Restaurant
from app.models.enums import PaymentStatus


class BusinessRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_hotels(self, *, owner_user_id: uuid.UUID) -> list[Hotel]:
        return list(
            self.db.scalars(
                select(Hotel)
                .where(Hotel.owner_user_id == owner_user_id)
                .options(selectinload(Hotel.city))
                .order_by(Hotel.name.asc()),
            ).all(),
        )

    def list_restaurants(self, *, owner_user_id: uuid.UUID) -> list[Restaurant]:
        return list(
            self.db.scalars(
                select(Restaurant)
                .where(Restaurant.owner_user_id == owner_user_id)
                .options(selectinload(Restaurant.city))
                .order_by(Restaurant.name.asc()),
            ).all(),
        )

    def list_guides(self, *, user_id: uuid.UUID) -> list[Guide]:
        return list(
            self.db.scalars(
                select(Guide)
                .where(Guide.user_id == user_id)
                .options(selectinload(Guide.city))
                .order_by(Guide.display_name.asc()),
            ).all(),
        )

    def owned_resource_pairs(
        self,
        *,
        owner_user_id: uuid.UUID,
    ) -> list[tuple[str, uuid.UUID]]:
        pairs: list[tuple[str, uuid.UUID]] = []
        for hotel in self.list_hotels(owner_user_id=owner_user_id):
            pairs.append(("hotel", hotel.id))
        for restaurant in self.list_restaurants(owner_user_id=owner_user_id):
            pairs.append(("restaurant", restaurant.id))
        for guide in self.list_guides(user_id=owner_user_id):
            pairs.append(("guide", guide.id))
        return pairs

    def list_bookings_for_resources(
        self,
        *,
        resource_pairs: list[tuple[str, uuid.UUID]],
        limit: int = 50,
    ) -> list[Booking]:
        if not resource_pairs:
            return []
        conditions = [
            and_(
                Booking.resource_type == resource_type,
                Booking.resource_id == resource_id,
            )
            for resource_type, resource_id in resource_pairs
        ]
        return list(
            self.db.scalars(
                select(Booking)
                .where(or_(*conditions))
                .order_by(Booking.created_at.desc())
                .limit(limit),
            ).all(),
        )

    def booking_status_counts(
        self,
        *,
        resource_pairs: list[tuple[str, uuid.UUID]],
    ) -> dict[str, int]:
        if not resource_pairs:
            return {}
        conditions = [
            and_(
                Booking.resource_type == resource_type,
                Booking.resource_id == resource_id,
            )
            for resource_type, resource_id in resource_pairs
        ]
        rows = self.db.execute(
            select(Booking.status, func.count())
            .where(or_(*conditions))
            .group_by(Booking.status),
        ).all()
        return {str(status): int(count) for status, count in rows}

    def captured_revenue_inr(
        self,
        *,
        resource_pairs: list[tuple[str, uuid.UUID]],
    ) -> int:
        if not resource_pairs:
            return 0
        booking_ids = [
            booking.id
            for booking in self.list_bookings_for_resources(
                resource_pairs=resource_pairs,
                limit=10_000,
            )
        ]
        if not booking_ids:
            return 0
        total = self.db.scalar(
            select(func.coalesce(func.sum(Payment.amount_inr), 0)).where(
                Payment.booking_id.in_(booking_ids),
                Payment.status == PaymentStatus.CAPTURED.value,
            ),
        )
        return int(total or 0)

    def property_title_map(
        self,
        *,
        owner_user_id: uuid.UUID,
    ) -> dict[tuple[str, uuid.UUID], str]:
        titles: dict[tuple[str, uuid.UUID], str] = {}
        for hotel in self.list_hotels(owner_user_id=owner_user_id):
            titles[("hotel", hotel.id)] = hotel.name
        for restaurant in self.list_restaurants(owner_user_id=owner_user_id):
            titles[("restaurant", restaurant.id)] = restaurant.name
        for guide in self.list_guides(user_id=owner_user_id):
            titles[("guide", guide.id)] = guide.display_name
        return titles
