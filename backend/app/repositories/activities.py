"""Activity data-access helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Activity, City, State
from app.repositories.places import haversine_km


class ActivityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return (
            select(Activity)
            .where(Activity.is_deleted.is_(False), Activity.is_available.is_(True))
            .options(selectinload(Activity.city).selectinload(City.state))
        )

    def list_activities(
        self,
        *,
        page: int,
        page_size: int,
        city_slug: str | None = None,
        state_code: str | None = None,
        q: str | None = None,
        category: str | None = None,
        max_price: int | None = None,
    ) -> tuple[list[Activity], int]:
        query = self._base_query()
        if city_slug or state_code:
            query = query.join(City)
            if city_slug:
                query = query.where(City.slug == city_slug.lower())
            if state_code:
                query = query.join(State).where(State.code == state_code.upper())
        if q:
            like = f"%{q.strip()}%"
            query = query.where(
                or_(
                    Activity.name.ilike(like),
                    Activity.description.ilike(like),
                    Activity.category.ilike(like),
                    Activity.slug.ilike(like),
                ),
            )
        if category:
            query = query.where(Activity.category.ilike(category.strip()))
        if max_price is not None:
            query = query.where(Activity.price_inr <= max_price)

        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total = int(self.db.scalar(count_query) or 0)
        rows = self.db.scalars(
            query.order_by(
                Activity.rating_avg.desc(),
                Activity.price_inr.asc(),
                Activity.name.asc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size),
        ).all()
        return list(rows), total

    def get_by_id(self, activity_id: uuid.UUID) -> Activity | None:
        return self.db.scalar(self._base_query().where(Activity.id == activity_id))

    def get_by_slug(self, slug: str) -> Activity | None:
        return self.db.scalar(self._base_query().where(Activity.slug == slug))

    def nearby(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[tuple[Activity, float]]:
        activities = list(self.db.scalars(self._base_query()).all())
        scored: list[tuple[Activity, float]] = []
        for activity in activities:
            lat, lng = activity_coords(activity)
            if lat is None or lng is None:
                continue
            distance = haversine_km(latitude, longitude, lat, lng)
            if distance <= radius_km:
                scored.append((activity, distance))
        scored.sort(key=lambda item: item[1])
        return scored[:limit]


def activity_coords(activity: Activity) -> tuple[float | None, float | None]:
    if activity.latitude is not None and activity.longitude is not None:
        return float(activity.latitude), float(activity.longitude)
    if (
        activity.city
        and activity.city.latitude is not None
        and activity.city.longitude is not None
    ):
        return float(activity.city.latitude), float(activity.city.longitude)
    return None, None
