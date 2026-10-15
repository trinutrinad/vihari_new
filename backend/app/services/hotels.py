"""Hotels business logic."""

from __future__ import annotations

import math
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Hotel
from app.repositories.hotels import HotelRepository, hotel_coords
from app.repositories.places import haversine_km
from app.schemas.hotels import HotelDetailOut, HotelRoomOut, HotelSummaryOut
from app.schemas.pagination import PageMeta, PaginatedData


class HotelService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = HotelRepository(db)

    def list_hotels(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
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
        lat: float | None = None,
        lng: float | None = None,
    ) -> PaginatedData[HotelSummaryOut]:
        rows, total = self.repo.list_hotels(
            page=page,
            page_size=page_size,
            city_slug=city_slug,
            state_code=state_code,
            q=q,
            min_price=min_price,
            max_price=max_price,
            has_wifi=has_wifi,
            has_breakfast=has_breakfast,
            has_parking=has_parking,
            has_pool=has_pool,
            family_friendly=family_friendly,
        )
        items = [
            self._to_summary(hotel, distance_km=_distance_if_possible(hotel, lat, lng))
            for hotel in rows
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

    def get_hotel(
        self,
        *,
        hotel_id: uuid.UUID | None = None,
        slug: str | None = None,
    ) -> HotelDetailOut:
        hotel = None
        if hotel_id is not None:
            hotel = self.repo.get_by_id(hotel_id)
        elif slug:
            hotel = self.repo.get_by_slug(slug)
        if hotel is None:
            raise NotFoundError("Hotel not found")
        summary = self._to_summary(hotel)
        return HotelDetailOut(
            **summary.model_dump(),
            address=hotel.address,
            cancellation_policy=hotel.cancellation_policy
            or "Demo policy: free cancellation not guaranteed — verify with property.",
            rooms=[
                HotelRoomOut(
                    id=room.id,
                    name=room.name,
                    description=room.description,
                    max_guests=room.max_guests,
                    price_per_night_inr=room.price_per_night_inr,
                    total_rooms=room.total_rooms,
                    is_available=room.is_available,
                )
                for room in sorted(hotel.rooms, key=lambda item: item.price_per_night_inr)
            ],
        )

    def nearby(
        self,
        *,
        lat: float,
        lng: float,
        radius_km: float = 50,
        limit: int = 20,
    ) -> list[HotelSummaryOut]:
        rows = self.repo.nearby(
            latitude=lat,
            longitude=lng,
            radius_km=radius_km,
            limit=limit,
        )
        return [
            self._to_summary(hotel, distance_km=distance) for hotel, distance in rows
        ]

    def _to_summary(
        self,
        hotel: Hotel,
        *,
        distance_km: float | None = None,
    ) -> HotelSummaryOut:
        lat, lng = hotel_coords(hotel)
        return HotelSummaryOut(
            id=hotel.id,
            name=hotel.name,
            slug=hotel.slug,
            description=hotel.description,
            city_name=hotel.city.name if hotel.city else "",
            state_name=hotel.city.state.name if hotel.city and hotel.city.state else "",
            state_code=hotel.city.state.code if hotel.city and hotel.city.state else "",
            latitude=lat,
            longitude=lng,
            rating_avg=hotel.rating_avg,
            rating_count=hotel.rating_count,
            starting_price_inr=hotel.starting_price_inr,
            has_ac=hotel.has_ac,
            has_wifi=hotel.has_wifi,
            has_parking=hotel.has_parking,
            has_breakfast=hotel.has_breakfast,
            has_pool=hotel.has_pool,
            is_family_friendly=hotel.is_family_friendly,
            is_couple_friendly=hotel.is_couple_friendly,
            hero_image_url=hotel.hero_image_url,
            is_seed_data=hotel.is_seed_data,
            distance_km=distance_km,
            provenance="seed_demo" if hotel.is_seed_data else "user_generated",
        )


def _distance_if_possible(
    hotel: Hotel,
    lat: float | None,
    lng: float | None,
) -> float | None:
    if lat is None or lng is None:
        return None
    h_lat, h_lng = hotel_coords(hotel)
    if h_lat is None or h_lng is None:
        return None
    return round(haversine_km(lat, lng, h_lat, h_lng), 1)
