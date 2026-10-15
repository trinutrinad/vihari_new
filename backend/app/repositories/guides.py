"""Guide data-access helpers."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import City, Guide, GuideAvailability, State
from app.repositories.places import haversine_km


class GuideRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return (
            select(Guide)
            .where(Guide.is_active.is_(True))
            .options(
                selectinload(Guide.city).selectinload(City.state),
                selectinload(Guide.availability),
            )
        )

    def list_guides(
        self,
        *,
        page: int,
        page_size: int,
        city_slug: str | None = None,
        state_code: str | None = None,
        q: str | None = None,
        language: str | None = None,
        specialization: str | None = None,
        max_price: int | None = None,
    ) -> tuple[list[Guide], int]:
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
                    Guide.display_name.ilike(like),
                    Guide.bio.ilike(like),
                    Guide.specialization.ilike(like),
                    Guide.languages.ilike(like),
                ),
            )
        if language:
            query = query.where(Guide.languages.ilike(f"%{language.strip()}%"))
        if specialization:
            query = query.where(
                Guide.specialization.ilike(f"%{specialization.strip()}%"),
            )
        if max_price is not None:
            query = query.where(Guide.price_per_day_inr <= max_price)

        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total = int(self.db.scalar(count_query) or 0)
        rows = self.db.scalars(
            query.order_by(
                Guide.rating_avg.desc(),
                Guide.price_per_day_inr.asc(),
                Guide.display_name.asc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size),
        ).all()
        return list(rows), total

    def get_by_id(self, guide_id: uuid.UUID) -> Guide | None:
        return self.db.scalar(self._base_query().where(Guide.id == guide_id))

    def nearby(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[tuple[Guide, float]]:
        guides = list(self.db.scalars(self._base_query()).all())
        scored: list[tuple[Guide, float]] = []
        for guide in guides:
            lat, lng = guide_coords(guide)
            if lat is None or lng is None:
                continue
            distance = haversine_km(latitude, longitude, lat, lng)
            if distance <= radius_km:
                scored.append((guide, distance))
        scored.sort(key=lambda item: item[1])
        return scored[:limit]

    def upcoming_availability(
        self,
        guide_id: uuid.UUID,
        *,
        from_date: date,
        limit: int = 14,
    ) -> list[GuideAvailability]:
        return list(
            self.db.scalars(
                select(GuideAvailability)
                .where(
                    GuideAvailability.guide_id == guide_id,
                    GuideAvailability.available_date >= from_date,
                    GuideAvailability.is_available.is_(True),
                )
                .order_by(GuideAvailability.available_date.asc())
                .limit(limit),
            ).all(),
        )


def guide_coords(guide: Guide) -> tuple[float | None, float | None]:
    if guide.city and guide.city.latitude is not None and guide.city.longitude is not None:
        return float(guide.city.latitude), float(guide.city.longitude)
    return None, None
