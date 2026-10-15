"""Restaurant data-access helpers."""

from __future__ import annotations

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import City, Restaurant, State
from app.repositories.places import haversine_km


class RestaurantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return (
            select(Restaurant)
            .where(Restaurant.is_deleted.is_(False))
            .options(
                selectinload(Restaurant.city).selectinload(City.state),
                selectinload(Restaurant.menu_items),
            )
        )

    def list_restaurants(
        self,
        *,
        page: int,
        page_size: int,
        city_slug: str | None = None,
        state_code: str | None = None,
        q: str | None = None,
        cuisine: str | None = None,
        vegetarian: bool | None = None,
        street_food: bool | None = None,
        max_price_level: int | None = None,
    ) -> tuple[list[Restaurant], int]:
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
                    Restaurant.name.ilike(like),
                    Restaurant.description.ilike(like),
                    Restaurant.cuisine_tags.ilike(like),
                ),
            )
        if cuisine:
            query = query.where(Restaurant.cuisine_tags.ilike(f"%{cuisine.strip()}%"))
        if vegetarian is not None:
            query = query.where(Restaurant.is_vegetarian.is_(vegetarian))
        if street_food is not None:
            query = query.where(Restaurant.is_street_food.is_(street_food))
        if max_price_level is not None:
            query = query.where(Restaurant.price_level <= max_price_level)

        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total = int(self.db.scalar(count_query) or 0)
        rows = self.db.scalars(
            query.order_by(
                Restaurant.rating_avg.desc(),
                Restaurant.price_level.asc(),
                Restaurant.name.asc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size),
        ).all()
        return list(rows), total

    def get_by_id(self, restaurant_id: uuid.UUID) -> Restaurant | None:
        return self.db.scalar(self._base_query().where(Restaurant.id == restaurant_id))

    def get_by_slug(self, slug: str) -> Restaurant | None:
        return self.db.scalar(self._base_query().where(Restaurant.slug == slug))

    def nearby(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[tuple[Restaurant, float]]:
        restaurants = list(self.db.scalars(self._base_query()).all())
        scored: list[tuple[Restaurant, float]] = []
        for restaurant in restaurants:
            lat, lng = restaurant_coords(restaurant)
            if lat is None or lng is None:
                continue
            distance = haversine_km(latitude, longitude, lat, lng)
            if distance <= radius_km:
                scored.append((restaurant, distance))
        scored.sort(key=lambda item: item[1])
        return scored[:limit]


def restaurant_coords(restaurant: Restaurant) -> tuple[float | None, float | None]:
    if restaurant.latitude is not None and restaurant.longitude is not None:
        return float(restaurant.latitude), float(restaurant.longitude)
    if (
        restaurant.city
        and restaurant.city.latitude is not None
        and restaurant.city.longitude is not None
    ):
        return float(restaurant.city.latitude), float(restaurant.city.longitude)
    return None, None
