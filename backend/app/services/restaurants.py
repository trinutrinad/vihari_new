"""Restaurants business logic."""

from __future__ import annotations

import math
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Restaurant
from app.repositories.places import haversine_km
from app.repositories.restaurants import RestaurantRepository, restaurant_coords
from app.schemas.pagination import PageMeta, PaginatedData
from app.schemas.restaurants import MenuItemOut, RestaurantDetailOut, RestaurantSummaryOut


class RestaurantService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RestaurantRepository(db)

    def list_restaurants(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        city_slug: str | None = None,
        state_code: str | None = None,
        q: str | None = None,
        cuisine: str | None = None,
        vegetarian: bool | None = None,
        street_food: bool | None = None,
        max_price_level: int | None = None,
        lat: float | None = None,
        lng: float | None = None,
    ) -> PaginatedData[RestaurantSummaryOut]:
        rows, total = self.repo.list_restaurants(
            page=page,
            page_size=page_size,
            city_slug=city_slug,
            state_code=state_code,
            q=q,
            cuisine=cuisine,
            vegetarian=vegetarian,
            street_food=street_food,
            max_price_level=max_price_level,
        )
        items = [
            self._to_summary(
                restaurant,
                distance_km=_distance_if_possible(restaurant, lat, lng),
            )
            for restaurant in rows
        ]
        if lat is not None and lng is not None:
            items.sort(
                key=lambda item: item.distance_km if item.distance_km is not None else 1e9,
            )
        total_pages = math.ceil(total / page_size) if page_size else 0
        return PaginatedData(
            items=items,
            meta=PageMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    def get_restaurant(
        self,
        *,
        restaurant_id: uuid.UUID | None = None,
        slug: str | None = None,
    ) -> RestaurantDetailOut:
        restaurant = None
        if restaurant_id is not None:
            restaurant = self.repo.get_by_id(restaurant_id)
        elif slug:
            restaurant = self.repo.get_by_slug(slug)
        if restaurant is None:
            raise NotFoundError("Restaurant not found")
        summary = self._to_summary(restaurant)
        return RestaurantDetailOut(
            **summary.model_dump(),
            address=restaurant.address,
            opening_hours=restaurant.opening_hours
            or "Hours not verified — confirm locally before visiting.",
            menu_items=[
                MenuItemOut(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    price_inr=item.price_inr,
                    is_veg=item.is_veg,
                    is_available=item.is_available,
                )
                for item in sorted(restaurant.menu_items, key=lambda row: row.price_inr)
            ],
        )

    def nearby(
        self,
        *,
        lat: float,
        lng: float,
        radius_km: float = 50,
        limit: int = 20,
    ) -> list[RestaurantSummaryOut]:
        rows = self.repo.nearby(
            latitude=lat,
            longitude=lng,
            radius_km=radius_km,
            limit=limit,
        )
        return [
            self._to_summary(restaurant, distance_km=distance)
            for restaurant, distance in rows
        ]

    def _to_summary(
        self,
        restaurant: Restaurant,
        *,
        distance_km: float | None = None,
    ) -> RestaurantSummaryOut:
        lat, lng = restaurant_coords(restaurant)
        return RestaurantSummaryOut(
            id=restaurant.id,
            name=restaurant.name,
            slug=restaurant.slug,
            description=restaurant.description,
            cuisine_tags=restaurant.cuisine_tags,
            city_name=restaurant.city.name if restaurant.city else "",
            state_name=(
                restaurant.city.state.name if restaurant.city and restaurant.city.state else ""
            ),
            state_code=(
                restaurant.city.state.code if restaurant.city and restaurant.city.state else ""
            ),
            latitude=lat,
            longitude=lng,
            rating_avg=restaurant.rating_avg,
            rating_count=restaurant.rating_count,
            price_level=restaurant.price_level,
            is_vegetarian=restaurant.is_vegetarian,
            is_street_food=restaurant.is_street_food,
            hero_image_url=restaurant.hero_image_url,
            is_seed_data=restaurant.is_seed_data,
            distance_km=distance_km,
            provenance="seed_demo" if restaurant.is_seed_data else "user_generated",
        )


def _distance_if_possible(
    restaurant: Restaurant,
    lat: float | None,
    lng: float | None,
) -> float | None:
    if lat is None or lng is None:
        return None
    r_lat, r_lng = restaurant_coords(restaurant)
    if r_lat is None or r_lng is None:
        return None
    return round(haversine_km(lat, lng, r_lat, r_lng), 1)
