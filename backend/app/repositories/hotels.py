"""Hotel data-access helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import City, Hotel, State
from app.repositories.places import haversine_km


class HotelRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return (
            select(Hotel)
            .where(Hotel.is_deleted.is_(False))
            .options(
                selectinload(Hotel.city).selectinload(City.state),
                selectinload(Hotel.rooms),
            )
        )

    def list_hotels(
        self,
        *,
        page: int,
        page_size: int,
        city_slug: str | None = None,
        state_code: str | None = None,
        q: str | None = None,
        min_price: int | None = None,
        max_price: int | None = None,
        has_wifi: bool | None = None,
        has_breakfast: bool | None = None,
        has_parking: bool | None = None,
        has_pool: bool | None = None,
        family_friendly: bool | None = None,
    ) -> tuple[list[Hotel], int]:
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
                or_(Hotel.name.ilike(like), Hotel.description.ilike(like)),
            )
        if min_price is not None:
            query = query.where(Hotel.starting_price_inr >= min_price)
        if max_price is not None:
            query = query.where(Hotel.starting_price_inr <= max_price)
        if has_wifi is not None:
            query = query.where(Hotel.has_wifi.is_(has_wifi))
        if has_breakfast is not None:
            query = query.where(Hotel.has_breakfast.is_(has_breakfast))
        if has_parking is not None:
            query = query.where(Hotel.has_parking.is_(has_parking))
        if has_pool is not None:
            query = query.where(Hotel.has_pool.is_(has_pool))
        if family_friendly is not None:
            query = query.where(Hotel.is_family_friendly.is_(family_friendly))

        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total = int(self.db.scalar(count_query) or 0)
        rows = self.db.scalars(
            query.order_by(
                Hotel.rating_avg.desc(),
                Hotel.starting_price_inr.asc(),
                Hotel.name.asc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size),
        ).all()
        return list(rows), total

    def get_by_id(self, hotel_id: uuid.UUID) -> Hotel | None:
        return self.db.scalar(self._base_query().where(Hotel.id == hotel_id))

    def get_by_slug(self, slug: str) -> Hotel | None:
        return self.db.scalar(self._base_query().where(Hotel.slug == slug))

    def nearby(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[tuple[Hotel, float]]:
        hotels = list(self.db.scalars(self._base_query()).all())
        scored: list[tuple[Hotel, float]] = []
        for hotel in hotels:
            lat, lng = hotel_coords(hotel)
            if lat is None or lng is None:
                continue
            distance = haversine_km(latitude, longitude, lat, lng)
            if distance <= radius_km:
                scored.append((hotel, distance))
        scored.sort(key=lambda item: item[1])
        return scored[:limit]


def hotel_coords(hotel: Hotel) -> tuple[float | None, float | None]:
    if hotel.latitude is not None and hotel.longitude is not None:
        return float(hotel.latitude), float(hotel.longitude)
    if hotel.city and hotel.city.latitude is not None and hotel.city.longitude is not None:
        return float(hotel.city.latitude), float(hotel.city.longitude)
    return None, None
