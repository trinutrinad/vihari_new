"""Map pin data access."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import City, PlaceCategory, TouristPlace


class MapRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def places_in_bounds(
        self,
        *,
        north: float,
        south: float,
        east: float,
        west: float,
        category: str | None = None,
        limit: int = 100,
    ) -> list[TouristPlace]:
        query = (
            select(TouristPlace)
            .where(
                TouristPlace.is_deleted.is_(False),
                TouristPlace.latitude.is_not(None),
                TouristPlace.longitude.is_not(None),
                TouristPlace.latitude <= north,
                TouristPlace.latitude >= south,
                TouristPlace.longitude <= east,
                TouristPlace.longitude >= west,
            )
            .options(
                selectinload(TouristPlace.category),
                selectinload(TouristPlace.city).selectinload(City.state),
            )
        )
        if category:
            query = query.join(PlaceCategory).where(
                PlaceCategory.slug == category.lower(),
            )
        rows = self.db.scalars(
            query.order_by(TouristPlace.rating_avg.desc()).limit(limit),
        ).all()
        return list(rows)

    def popular_cities_with_coords(self, *, limit: int = 20) -> list[tuple[City, int]]:
        cities = list(
            self.db.scalars(
                select(City)
                .where(
                    City.latitude.is_not(None),
                    City.longitude.is_not(None),
                )
                .options(selectinload(City.state))
                .order_by(City.is_popular.desc(), City.name.asc())
                .limit(max(limit * 3, 20)),
            ).all(),
        )
        scored: list[tuple[City, int]] = []
        for city in cities:
            count = _count_places(self.db, city.id)
            scored.append((city, count))
        scored.sort(key=lambda item: (-int(item[0].is_popular), -item[1], item[0].name))
        return scored[:limit]


def _count_places(db: Session, city_id: uuid.UUID) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(TouristPlace)
            .where(
                TouristPlace.city_id == city_id,
                TouristPlace.is_deleted.is_(False),
            ),
        )
        or 0,
    )
