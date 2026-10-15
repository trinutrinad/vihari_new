"""Map pins and city centers for Leaflet/OSM."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import ValidationAppError
from app.models import TouristPlace
from app.repositories.maps import MapRepository
from app.schemas.maps import CityMapCenterOut, MapPinOut, MapPinsData


class MapService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = MapRepository(db)

    def pins_in_bounds(
        self,
        *,
        north: float,
        south: float,
        east: float,
        west: float,
        category: str | None = None,
        limit: int = 100,
    ) -> MapPinsData:
        if south >= north:
            raise ValidationAppError("south must be less than north")
        if west >= east:
            raise ValidationAppError("west must be less than east")
        if north > 90 or south < -90 or east > 180 or west < -180:
            raise ValidationAppError("Bounds are out of valid lat/lng range")

        places = self.repo.places_in_bounds(
            north=north,
            south=south,
            east=east,
            west=west,
            category=category,
            limit=limit,
        )
        pins = [self._to_pin(place) for place in places]
        return MapPinsData(pins=pins, total=len(pins))

    def city_centers(self, *, limit: int = 20) -> list[CityMapCenterOut]:
        rows = self.repo.popular_cities_with_coords(limit=limit)
        result: list[CityMapCenterOut] = []
        for city, place_count in rows:
            if city.latitude is None or city.longitude is None:
                continue
            result.append(
                CityMapCenterOut(
                    id=city.id,
                    name=city.name,
                    slug=city.slug,
                    state_code=city.state.code,
                    latitude=city.latitude,
                    longitude=city.longitude,
                    place_count=place_count,
                    is_seed_data=city.is_seed_data,
                ),
            )
        return result

    def _to_pin(self, place: TouristPlace) -> MapPinOut:
        assert place.latitude is not None and place.longitude is not None
        return MapPinOut(
            id=place.id,
            name=place.name,
            slug=place.slug,
            entity_type="place",
            latitude=Decimal(place.latitude),
            longitude=Decimal(place.longitude),
            city_name=place.city.name if place.city else "",
            state_code=place.city.state.code if place.city and place.city.state else "",
            category_slug=place.category.slug if place.category else None,
            rating_avg=place.rating_avg,
            is_seed_data=place.is_seed_data,
            href=f"/places/{place.id}",
        )
