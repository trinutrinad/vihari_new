"""Guides business logic."""

from __future__ import annotations

import math
import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Guide
from app.repositories.guides import GuideRepository, guide_coords
from app.repositories.places import haversine_km
from app.schemas.guides import GuideAvailabilityOut, GuideDetailOut, GuideSummaryOut
from app.schemas.pagination import PageMeta, PaginatedData


class GuideService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = GuideRepository(db)

    def list_guides(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        city_slug: str | None = None,
        state_code: str | None = None,
        q: str | None = None,
        language: str | None = None,
        specialization: str | None = None,
        max_price: int | None = None,
        lat: float | None = None,
        lng: float | None = None,
    ) -> PaginatedData[GuideSummaryOut]:
        rows, total = self.repo.list_guides(
            page=page,
            page_size=page_size,
            city_slug=city_slug,
            state_code=state_code,
            q=q,
            language=language,
            specialization=specialization,
            max_price=max_price,
        )
        items = [
            self._to_summary(guide, distance_km=_distance_if_possible(guide, lat, lng))
            for guide in rows
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

    def get_guide(self, *, guide_id: uuid.UUID) -> GuideDetailOut:
        guide = self.repo.get_by_id(guide_id)
        if guide is None:
            raise NotFoundError("Guide not found")
        summary = self._to_summary(guide)
        today = date.today()
        availability = self.repo.upcoming_availability(
            guide.id,
            from_date=today,
            limit=14,
        )
        # Fall back to relationship rows if query empty but loaded
        if not availability and guide.availability:
            availability = [
                row
                for row in sorted(guide.availability, key=lambda item: item.available_date)
                if row.available_date >= today and row.is_available
            ][:14]
        return GuideDetailOut(
            **summary.model_dump(),
            availability=[
                GuideAvailabilityOut(
                    id=row.id,
                    available_date=row.available_date,
                    is_available=row.is_available,
                )
                for row in availability
            ],
        )

    def nearby(
        self,
        *,
        lat: float,
        lng: float,
        radius_km: float = 80,
        limit: int = 20,
    ) -> list[GuideSummaryOut]:
        rows = self.repo.nearby(
            latitude=lat,
            longitude=lng,
            radius_km=radius_km,
            limit=limit,
        )
        return [self._to_summary(guide, distance_km=distance) for guide, distance in rows]

    def _to_summary(
        self,
        guide: Guide,
        *,
        distance_km: float | None = None,
    ) -> GuideSummaryOut:
        lat, lng = guide_coords(guide)
        return GuideSummaryOut(
            id=guide.id,
            display_name=guide.display_name,
            bio=guide.bio,
            languages=guide.languages,
            specialization=guide.specialization,
            experience_years=guide.experience_years,
            price_per_day_inr=guide.price_per_day_inr,
            rating_avg=guide.rating_avg,
            rating_count=guide.rating_count,
            profile_image_url=guide.profile_image_url,
            city_name=guide.city.name if guide.city else "",
            state_name=guide.city.state.name if guide.city and guide.city.state else "",
            state_code=guide.city.state.code if guide.city and guide.city.state else "",
            latitude=lat,
            longitude=lng,
            is_active=guide.is_active,
            is_seed_data=guide.is_seed_data,
            distance_km=distance_km,
            provenance="seed_demo" if guide.is_seed_data else "user_generated",
        )


def _distance_if_possible(
    guide: Guide,
    lat: float | None,
    lng: float | None,
) -> float | None:
    if lat is None or lng is None:
        return None
    g_lat, g_lng = guide_coords(guide)
    if g_lat is None or g_lng is None:
        return None
    return round(haversine_km(lat, lng, g_lat, g_lng), 1)
