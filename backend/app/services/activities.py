"""Activities business logic."""

from __future__ import annotations

import math
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Activity
from app.repositories.activities import ActivityRepository, activity_coords
from app.repositories.places import haversine_km
from app.schemas.activities import ActivityDetailOut, ActivitySummaryOut
from app.schemas.pagination import PageMeta, PaginatedData


class ActivityService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ActivityRepository(db)

    def list_activities(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        city_slug: str | None = None,
        state_code: str | None = None,
        q: str | None = None,
        category: str | None = None,
        max_price: int | None = None,
        lat: float | None = None,
        lng: float | None = None,
    ) -> PaginatedData[ActivitySummaryOut]:
        rows, total = self.repo.list_activities(
            page=page,
            page_size=page_size,
            city_slug=city_slug,
            state_code=state_code,
            q=q,
            category=category,
            max_price=max_price,
        )
        items = [
            self._to_summary(activity, distance_km=_distance_if_possible(activity, lat, lng))
            for activity in rows
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

    def get_activity(
        self,
        *,
        activity_id: uuid.UUID | None = None,
        slug: str | None = None,
    ) -> ActivityDetailOut:
        activity = None
        if activity_id is not None:
            activity = self.repo.get_by_id(activity_id)
        elif slug:
            activity = self.repo.get_by_slug(slug)
        if activity is None:
            raise NotFoundError("Activity not found")
        summary = self._to_summary(activity)
        return ActivityDetailOut(
            **summary.model_dump(),
            safety_information=activity.safety_information,
        )

    def nearby(
        self,
        *,
        lat: float,
        lng: float,
        radius_km: float = 80,
        limit: int = 20,
    ) -> list[ActivitySummaryOut]:
        rows = self.repo.nearby(
            latitude=lat,
            longitude=lng,
            radius_km=radius_km,
            limit=limit,
        )
        return [
            self._to_summary(activity, distance_km=distance)
            for activity, distance in rows
        ]

    def _to_summary(
        self,
        activity: Activity,
        *,
        distance_km: float | None = None,
    ) -> ActivitySummaryOut:
        lat, lng = activity_coords(activity)
        return ActivitySummaryOut(
            id=activity.id,
            name=activity.name,
            slug=activity.slug,
            category=activity.category,
            description=activity.description,
            duration_hours=activity.duration_hours,
            price_inr=activity.price_inr,
            latitude=lat,
            longitude=lng,
            rating_avg=activity.rating_avg,
            rating_count=activity.rating_count,
            hero_image_url=activity.hero_image_url,
            city_name=activity.city.name if activity.city else "",
            state_name=activity.city.state.name if activity.city and activity.city.state else "",
            state_code=activity.city.state.code if activity.city and activity.city.state else "",
            is_available=activity.is_available,
            is_seed_data=activity.is_seed_data,
            distance_km=distance_km,
            provenance="seed_demo" if activity.is_seed_data else "user_generated",
        )


def _distance_if_possible(
    activity: Activity,
    lat: float | None,
    lng: float | None,
) -> float | None:
    if lat is None or lng is None:
        return None
    a_lat, a_lng = activity_coords(activity)
    if a_lat is None or a_lng is None:
        return None
    return round(haversine_km(lat, lng, a_lat, a_lng), 1)
