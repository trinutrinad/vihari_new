"""Tourist places business logic."""

from __future__ import annotations

import math
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Hotel, Restaurant, TouristPlace
from app.repositories.places import PlaceRepository, as_float
from app.schemas.pagination import PageMeta, PaginatedData
from app.schemas.places import (
    NearbyAmenityOut,
    PlaceCategoryOut,
    PlaceDetailOut,
    PlaceImageOut,
    PlaceSummaryOut,
    SavedPlaceOut,
)


class PlaceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PlaceRepository(db)

    def list_places(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        category: str | None = None,
        state_code: str | None = None,
        city_slug: str | None = None,
        featured: bool | None = None,
        hidden_gem: bool | None = None,
        q: str | None = None,
        family_friendly: bool | None = None,
        lat: float | None = None,
        lng: float | None = None,
    ) -> PaginatedData[PlaceSummaryOut]:
        rows, total = self.repo.list_places(
            page=page,
            page_size=page_size,
            category=category,
            state_code=state_code,
            city_slug=city_slug,
            featured=featured,
            hidden_gem=hidden_gem,
            q=q,
            family_friendly=family_friendly,
        )
        items = [
            self._to_summary(
                place,
                distance_km=_distance_if_possible(place, lat, lng),
            )
            for place in rows
        ]
        if lat is not None and lng is not None:
            items.sort(key=lambda item: item.distance_km if item.distance_km is not None else 1e9)
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

    def list_categories(self) -> list[PlaceCategoryOut]:
        return [
            PlaceCategoryOut(
                id=category.id,
                name=category.name,
                slug=category.slug,
                icon=category.icon,
            )
            for category in self.repo.list_categories()
        ]

    def get_place(
        self,
        *,
        place_id: uuid.UUID | None = None,
        slug: str | None = None,
        user_id: uuid.UUID | None = None,
    ) -> PlaceDetailOut:
        place = None
        if place_id is not None:
            place = self.repo.get_by_id(place_id)
        elif slug:
            place = self.repo.get_by_slug(slug)
        if place is None:
            raise NotFoundError("Place not found")

        nearby_rows: list[tuple[TouristPlace, float]] = []
        if place.latitude is not None and place.longitude is not None:
            nearby_rows = self.repo.nearby(
                latitude=float(place.latitude),
                longitude=float(place.longitude),
                radius_km=80,
                limit=6,
                exclude_id=place.id,
            )
        elif place.city_id:
            same_city, _ = self.repo.list_places(
                page=1,
                page_size=6,
                city_slug=place.city.slug,
            )
            nearby_rows = [(item, 0.0) for item in same_city if item.id != place.id][:6]

        hotels = self.repo.hotels_in_city(place.city_id, limit=5)
        restaurants = self.repo.restaurants_in_city(place.city_id, limit=5)
        is_saved = False
        if user_id is not None:
            is_saved = self.repo.is_saved(user_id=user_id, place_id=place.id)

        summary = self._to_summary(place)
        return PlaceDetailOut(
            **summary.model_dump(),
            description=place.description,
            address=place.address,
            best_time_to_visit=place.best_time_to_visit,
            opening_hours=place.opening_hours,
            entry_fee_notes=place.entry_fee_notes,
            facilities=place.facilities,
            how_to_reach=place.how_to_reach,
            images=[
                PlaceImageOut(
                    id=image.id,
                    url=image.url,
                    caption=image.caption,
                    is_cover=image.is_cover,
                    sort_order=image.sort_order,
                )
                for image in sorted(place.images, key=lambda item: item.sort_order)
            ],
            nearby_places=[
                self._to_summary(item, distance_km=distance)
                for item, distance in nearby_rows
            ],
            nearby_hotels=[_hotel_brief(hotel) for hotel in hotels],
            nearby_restaurants=[_restaurant_brief(restaurant) for restaurant in restaurants],
            nearby_amenities=_unverified_amenities(place),
            is_saved=is_saved,
        )

    def nearby(
        self,
        *,
        lat: float,
        lng: float,
        radius_km: float = 50,
        limit: int = 20,
    ) -> list[PlaceSummaryOut]:
        rows = self.repo.nearby(
            latitude=lat,
            longitude=lng,
            radius_km=radius_km,
            limit=limit,
        )
        return [
            self._to_summary(place, distance_km=distance) for place, distance in rows
        ]

    def save(self, *, user_id: uuid.UUID, place_id: uuid.UUID) -> SavedPlaceOut:
        if self.repo.get_by_id(place_id) is None:
            raise NotFoundError("Place not found")
        self.repo.save_place(user_id=user_id, place_id=place_id)
        return SavedPlaceOut(place_id=place_id, saved=True)

    def unsave(self, *, user_id: uuid.UUID, place_id: uuid.UUID) -> SavedPlaceOut:
        if self.repo.get_by_id(place_id) is None:
            raise NotFoundError("Place not found")
        self.repo.unsave_place(user_id=user_id, place_id=place_id)
        return SavedPlaceOut(place_id=place_id, saved=False)

    def list_saved(self, *, user_id: uuid.UUID) -> list[PlaceSummaryOut]:
        return [self._to_summary(place) for place in self.repo.list_saved(user_id=user_id)]

    def _to_summary(
        self,
        place: TouristPlace,
        *,
        distance_km: float | None = None,
    ) -> PlaceSummaryOut:
        category = None
        if place.category:
            category = PlaceCategoryOut(
                id=place.category.id,
                name=place.category.name,
                slug=place.category.slug,
                icon=place.category.icon,
            )
        return PlaceSummaryOut(
            id=place.id,
            name=place.name,
            slug=place.slug,
            short_description=place.short_description,
            city_name=place.city.name,
            state_name=place.city.state.name,
            state_code=place.city.state.code,
            category=category,
            latitude=place.latitude,
            longitude=place.longitude,
            rating_avg=place.rating_avg,
            rating_count=place.rating_count,
            estimated_cost_inr=place.estimated_cost_inr,
            hero_image_url=place.hero_image_url,
            is_featured=place.is_featured,
            is_hidden_gem=place.is_hidden_gem,
            is_family_friendly=place.is_family_friendly,
            is_couple_friendly=place.is_couple_friendly,
            is_pet_friendly=place.is_pet_friendly,
            provenance=place.provenance,
            is_seed_data=place.is_seed_data,
            distance_km=round(distance_km, 1) if distance_km is not None else None,
        )


def _distance_if_possible(
    place: TouristPlace,
    lat: float | None,
    lng: float | None,
) -> float | None:
    if lat is None or lng is None:
        return None
    plat = as_float(place.latitude)
    plng = as_float(place.longitude)
    if plat is None or plng is None:
        return None
    from app.repositories.places import haversine_km

    return haversine_km(lat, lng, plat, plng)


def _hotel_brief(hotel: Hotel) -> dict:
    return {
        "id": str(hotel.id),
        "name": hotel.name,
        "slug": hotel.slug,
        "rating_avg": float(hotel.rating_avg),
        "starting_price_inr": hotel.starting_price_inr,
        "is_seed_data": hotel.is_seed_data,
    }


def _restaurant_brief(restaurant: Restaurant) -> dict:
    return {
        "id": str(restaurant.id),
        "name": restaurant.name,
        "slug": restaurant.slug,
        "rating_avg": float(restaurant.rating_avg),
        "cuisine_tags": restaurant.cuisine_tags,
        "is_seed_data": restaurant.is_seed_data,
    }


def _unverified_amenities(place: TouristPlace) -> list[NearbyAmenityOut]:
    """Return guidance placeholders only — not official POI data."""
    city = place.city.name
    return [
        NearbyAmenityOut(
            name=f"Hospitals near {city}",
            kind="hospital",
            note="Use offline maps or local emergency numbers. Locations not verified here.",
        ),
        NearbyAmenityOut(
            name=f"ATMs near {city}",
            kind="atm",
            note="ATM availability varies. Confirm on a live map before relying on cash access.",
        ),
        NearbyAmenityOut(
            name=f"Parking near {place.name}",
            kind="parking",
            note="Parking details are community/unverified unless marked official.",
        ),
        NearbyAmenityOut(
            name=f"Petrol pumps near {city}",
            kind="petrol",
            note="Fuel station locations are not verified in this demo dataset.",
        ),
        NearbyAmenityOut(
            name="Emergency services",
            kind="emergency",
            note="In India dial 112 for emergencies. Share live location with trusted contacts.",
        ),
    ]
