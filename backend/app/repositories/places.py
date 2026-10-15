"""Place data-access helpers."""

from __future__ import annotations

import math
import uuid
from decimal import Decimal

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    City,
    Hotel,
    PlaceCategory,
    Restaurant,
    SavedPlace,
    State,
    TouristPlace,
)


class PlaceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return (
            select(TouristPlace)
            .where(TouristPlace.is_deleted.is_(False))
            .options(
                selectinload(TouristPlace.category),
                selectinload(TouristPlace.city).selectinload(City.state),
                selectinload(TouristPlace.images),
            )
        )

    def list_places(
        self,
        *,
        page: int,
        page_size: int,
        category: str | None = None,
        state_code: str | None = None,
        city_slug: str | None = None,
        featured: bool | None = None,
        hidden_gem: bool | None = None,
        q: str | None = None,
        family_friendly: bool | None = None,
    ) -> tuple[list[TouristPlace], int]:
        query = self._base_query()
        if category:
            query = query.join(PlaceCategory).where(
                or_(
                    PlaceCategory.slug == category.lower(),
                    PlaceCategory.name.ilike(category),
                ),
            )
        if state_code or city_slug:
            query = query.join(City)
            if state_code:
                query = query.join(State).where(State.code == state_code.upper())
            if city_slug:
                query = query.where(City.slug == city_slug.lower())
        if featured is not None:
            query = query.where(TouristPlace.is_featured.is_(featured))
        if hidden_gem is not None:
            query = query.where(TouristPlace.is_hidden_gem.is_(hidden_gem))
        if family_friendly is not None:
            query = query.where(TouristPlace.is_family_friendly.is_(family_friendly))
        if q:
            like = f"%{q.strip()}%"
            query = query.where(
                or_(
                    TouristPlace.name.ilike(like),
                    TouristPlace.short_description.ilike(like),
                    TouristPlace.description.ilike(like),
                ),
            )

        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total = int(self.db.scalar(count_query) or 0)
        rows = self.db.scalars(
            query.order_by(
                TouristPlace.is_featured.desc(),
                TouristPlace.rating_avg.desc(),
                TouristPlace.name.asc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size),
        ).all()
        return list(rows), total

    def get_by_id(self, place_id: uuid.UUID) -> TouristPlace | None:
        return self.db.scalar(self._base_query().where(TouristPlace.id == place_id))

    def get_by_slug(self, slug: str) -> TouristPlace | None:
        return self.db.scalar(self._base_query().where(TouristPlace.slug == slug))

    def list_categories(self) -> list[PlaceCategory]:
        return list(
            self.db.scalars(
                select(PlaceCategory).order_by(
                    PlaceCategory.sort_order.asc(),
                    PlaceCategory.name.asc(),
                ),
            ).all(),
        )

    def nearby(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
        exclude_id: uuid.UUID | None = None,
    ) -> list[tuple[TouristPlace, float]]:
        places = list(
            self.db.scalars(
                self._base_query().where(
                    and_(
                        TouristPlace.latitude.is_not(None),
                        TouristPlace.longitude.is_not(None),
                    ),
                ),
            ).all(),
        )
        scored: list[tuple[TouristPlace, float]] = []
        for place in places:
            if exclude_id and place.id == exclude_id:
                continue
            if place.latitude is None or place.longitude is None:
                continue
            distance = haversine_km(
                latitude,
                longitude,
                float(place.latitude),
                float(place.longitude),
            )
            if distance <= radius_km:
                scored.append((place, distance))
        scored.sort(key=lambda item: item[1])
        return scored[:limit]

    def hotels_in_city(self, city_id: uuid.UUID, *, limit: int = 5) -> list[Hotel]:
        return list(
            self.db.scalars(
                select(Hotel)
                .where(Hotel.city_id == city_id, Hotel.is_deleted.is_(False))
                .order_by(Hotel.rating_avg.desc())
                .limit(limit),
            ).all(),
        )

    def restaurants_in_city(self, city_id: uuid.UUID, *, limit: int = 5) -> list[Restaurant]:
        return list(
            self.db.scalars(
                select(Restaurant)
                .where(Restaurant.city_id == city_id, Restaurant.is_deleted.is_(False))
                .order_by(Restaurant.rating_avg.desc())
                .limit(limit),
            ).all(),
        )

    def is_saved(self, *, user_id: uuid.UUID, place_id: uuid.UUID) -> bool:
        return (
            self.db.scalar(
                select(SavedPlace.id).where(
                    SavedPlace.user_id == user_id,
                    SavedPlace.place_id == place_id,
                ),
            )
            is not None
        )

    def save_place(self, *, user_id: uuid.UUID, place_id: uuid.UUID) -> SavedPlace:
        existing = self.db.scalar(
            select(SavedPlace).where(
                SavedPlace.user_id == user_id,
                SavedPlace.place_id == place_id,
            ),
        )
        if existing:
            return existing
        row = SavedPlace(user_id=user_id, place_id=place_id)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def unsave_place(self, *, user_id: uuid.UUID, place_id: uuid.UUID) -> bool:
        row = self.db.scalar(
            select(SavedPlace).where(
                SavedPlace.user_id == user_id,
                SavedPlace.place_id == place_id,
            ),
        )
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True

    def list_saved(self, *, user_id: uuid.UUID) -> list[TouristPlace]:
        return list(
            self.db.scalars(
                self._base_query()
                .join(SavedPlace, SavedPlace.place_id == TouristPlace.id)
                .where(SavedPlace.user_id == user_id)
                .order_by(SavedPlace.created_at.desc()),
            ).all(),
        )


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def as_float(value: Decimal | float | None) -> float | None:
    if value is None:
        return None
    return float(value)
