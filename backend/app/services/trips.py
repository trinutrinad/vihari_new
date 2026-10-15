"""Trip planning business logic."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationAppError
from app.models import Trip, TripDay, TripPlace
from app.models.enums import TripStatus
from app.repositories.trips import TripRepository
from app.schemas.trips import (
    TripCreate,
    TripDayCreate,
    TripDayOut,
    TripDayUpdate,
    TripDetailOut,
    TripMapPointOut,
    TripPlaceCreate,
    TripPlaceOut,
    TripShareOut,
    TripSummaryOut,
    TripUpdate,
)


class TripService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = TripRepository(db)

    def list_trips(
        self,
        *,
        user_id: uuid.UUID,
        status: str | None = None,
    ) -> list[TripSummaryOut]:
        return [self._to_summary(trip) for trip in self.repo.list_for_user(
            user_id=user_id,
            status=status,
        )]

    def get_trip(self, *, trip_id: uuid.UUID, user_id: uuid.UUID) -> TripDetailOut:
        trip = self.repo.get_for_user(trip_id=trip_id, user_id=user_id)
        if trip is None:
            raise NotFoundError("Trip not found")
        return self._to_detail(trip)

    def get_shared_trip(self, share_code: str) -> TripDetailOut:
        trip = self.repo.get_by_share_code(share_code.strip())
        if trip is None:
            raise NotFoundError("Shared trip not found")
        return self._to_detail(trip)

    def create_trip(self, *, user_id: uuid.UUID, payload: TripCreate) -> TripDetailOut:
        trip = Trip(
            user_id=user_id,
            title=payload.title.strip(),
            summary=payload.summary,
            start_date=payload.start_date,
            end_date=payload.end_date,
            origin_city=payload.origin_city,
            destination_summary=payload.destination_summary,
            budget_inr=payload.budget_inr,
            status=payload.status.value,
            is_ai_generated=payload.is_ai_generated,
            ai_prompt=payload.ai_prompt,
        )
        for day_payload in payload.days:
            trip.days.append(self._build_day(day_payload))
        self._recompute_estimated_cost(trip)
        saved = self.repo.create(trip)
        return self._to_detail(saved)

    def update_trip(
        self,
        *,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: TripUpdate,
    ) -> TripDetailOut:
        trip = self._require_owned(trip_id=trip_id, user_id=user_id)
        data = payload.model_dump(exclude_unset=True)
        if "status" in data and data["status"] is not None:
            data["status"] = (
                data["status"].value
                if isinstance(data["status"], TripStatus)
                else str(data["status"])
            )
        if "title" in data and data["title"] is not None:
            data["title"] = data["title"].strip()
        for key, value in data.items():
            setattr(trip, key, value)
        if trip.end_date and trip.start_date and trip.end_date < trip.start_date:
            raise ValidationAppError("end_date must be on or after start_date")
        saved = self.repo.save(trip)
        return self._to_detail(saved)

    def delete_trip(self, *, trip_id: uuid.UUID, user_id: uuid.UUID) -> None:
        trip = self._require_owned(trip_id=trip_id, user_id=user_id)
        self.repo.delete(trip)

    def add_day(
        self,
        *,
        trip_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: TripDayCreate,
    ) -> TripDetailOut:
        trip = self._require_owned(trip_id=trip_id, user_id=user_id)
        if any(day.day_number == payload.day_number for day in trip.days):
            raise ValidationAppError(f"Day {payload.day_number} already exists")
        trip.days.append(self._build_day(payload))
        self._recompute_estimated_cost(trip)
        return self._to_detail(self.repo.save(trip))

    def update_day(
        self,
        *,
        trip_id: uuid.UUID,
        day_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: TripDayUpdate,
    ) -> TripDetailOut:
        trip = self._require_owned(trip_id=trip_id, user_id=user_id)
        day = self.repo.get_day(day_id=day_id, trip_id=trip.id)
        if day is None:
            raise NotFoundError("Trip day not found")
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(day, key, value)
        return self._to_detail(self.repo.save(trip))

    def delete_day(
        self,
        *,
        trip_id: uuid.UUID,
        day_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> TripDetailOut:
        trip = self._require_owned(trip_id=trip_id, user_id=user_id)
        day = next((item for item in trip.days if item.id == day_id), None)
        if day is None:
            raise NotFoundError("Trip day not found")
        trip.days.remove(day)
        self._recompute_estimated_cost(trip)
        return self._to_detail(self.repo.save(trip))

    def add_place(
        self,
        *,
        trip_id: uuid.UUID,
        day_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: TripPlaceCreate,
    ) -> TripDetailOut:
        trip = self._require_owned(trip_id=trip_id, user_id=user_id)
        day = next((item for item in trip.days if item.id == day_id), None)
        if day is None:
            raise NotFoundError("Trip day not found")
        if payload.place_id is None and not (payload.custom_title or "").strip():
            raise ValidationAppError("place_id or custom_title is required")
        if payload.place_id is not None:
            place = self.repo.get_place(payload.place_id)
            if place is None:
                raise NotFoundError("Place not found")
        day.places.append(
            TripPlace(
                place_id=payload.place_id,
                custom_title=payload.custom_title,
                time_slot=payload.time_slot,
                notes=payload.notes,
                estimated_cost_inr=payload.estimated_cost_inr,
                sort_order=payload.sort_order or len(day.places),
            ),
        )
        self._recompute_estimated_cost(trip)
        return self._to_detail(self.repo.save(trip))

    def remove_place(
        self,
        *,
        trip_id: uuid.UUID,
        day_id: uuid.UUID,
        stop_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> TripDetailOut:
        trip = self._require_owned(trip_id=trip_id, user_id=user_id)
        day = next((item for item in trip.days if item.id == day_id), None)
        if day is None:
            raise NotFoundError("Trip day not found")
        stop = next((item for item in day.places if item.id == stop_id), None)
        if stop is None:
            raise NotFoundError("Trip stop not found")
        day.places.remove(stop)
        self._recompute_estimated_cost(trip)
        return self._to_detail(self.repo.save(trip))

    def enable_share(self, *, trip_id: uuid.UUID, user_id: uuid.UUID) -> TripShareOut:
        trip = self._require_owned(trip_id=trip_id, user_id=user_id)
        if not trip.share_code:
            trip.share_code = self.repo.new_share_code()
            trip = self.repo.save(trip)
        assert trip.share_code is not None
        return TripShareOut(
            share_code=trip.share_code,
            share_path=f"/trips/shared/{trip.share_code}",
        )

    def _require_owned(self, *, trip_id: uuid.UUID, user_id: uuid.UUID) -> Trip:
        trip = self.repo.get_for_user(trip_id=trip_id, user_id=user_id)
        if trip is None:
            # Distinguish missing vs forbidden only when trip exists for another user
            if self.repo.get_by_id(trip_id) is not None:
                raise ForbiddenError("Not allowed to access this trip")
            raise NotFoundError("Trip not found")
        return trip

    def _build_day(self, payload: TripDayCreate) -> TripDay:
        day = TripDay(
            day_number=payload.day_number,
            title=payload.title,
            notes=payload.notes,
        )
        for index, stop in enumerate(payload.places):
            if stop.place_id is None and not (stop.custom_title or "").strip():
                raise ValidationAppError("Each stop needs place_id or custom_title")
            if stop.place_id is not None and self.repo.get_place(stop.place_id) is None:
                raise NotFoundError("Place not found")
            day.places.append(
                TripPlace(
                    place_id=stop.place_id,
                    custom_title=stop.custom_title,
                    time_slot=stop.time_slot,
                    notes=stop.notes,
                    estimated_cost_inr=stop.estimated_cost_inr,
                    sort_order=stop.sort_order if stop.sort_order else index,
                ),
            )
        return day

    def _recompute_estimated_cost(self, trip: Trip) -> None:
        total = 0
        for day in trip.days:
            for stop in day.places:
                if stop.estimated_cost_inr:
                    total += stop.estimated_cost_inr
                    continue
                place = stop.place
                if place is None and stop.place_id is not None:
                    place = self.repo.get_place(stop.place_id)
                if place is not None and place.estimated_cost_inr is not None:
                    total += int(place.estimated_cost_inr)
        trip.estimated_cost_inr = total or None

    def _to_summary(self, trip: Trip) -> TripSummaryOut:
        stop_count = sum(len(day.places) for day in trip.days)
        return TripSummaryOut(
            id=trip.id,
            title=trip.title,
            summary=trip.summary,
            start_date=trip.start_date,
            end_date=trip.end_date,
            origin_city=trip.origin_city,
            destination_summary=trip.destination_summary,
            budget_inr=trip.budget_inr,
            estimated_cost_inr=trip.estimated_cost_inr,
            status=trip.status,
            is_ai_generated=trip.is_ai_generated,
            share_code=trip.share_code,
            day_count=len(trip.days),
            stop_count=stop_count,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )

    def _to_detail(self, trip: Trip) -> TripDetailOut:
        summary = self._to_summary(trip)
        days = [
            TripDayOut(
                id=day.id,
                day_number=day.day_number,
                title=day.title,
                notes=day.notes,
                places=[self._to_place(stop) for stop in sorted(
                    day.places,
                    key=lambda item: item.sort_order,
                )],
            )
            for day in sorted(trip.days, key=lambda item: item.day_number)
        ]
        return TripDetailOut(
            **summary.model_dump(),
            days=days,
            map_points=self._map_points(days),
        )

    def _to_place(self, stop: TripPlace) -> TripPlaceOut:
        place = stop.place
        title = stop.custom_title or (place.name if place else "Stop")
        return TripPlaceOut(
            id=stop.id,
            place_id=stop.place_id,
            custom_title=stop.custom_title,
            title=title,
            time_slot=stop.time_slot,
            notes=stop.notes,
            estimated_cost_inr=stop.estimated_cost_inr
            or (int(place.estimated_cost_inr) if place and place.estimated_cost_inr else None),
            sort_order=stop.sort_order,
            place_slug=place.slug if place else None,
            city_name=place.city.name if place and place.city else None,
            latitude=place.latitude if place else None,
            longitude=place.longitude if place else None,
            is_seed_data=bool(place.is_seed_data) if place else False,
        )

    def _map_points(self, days: list[TripDayOut]) -> list[TripMapPointOut]:
        points: list[TripMapPointOut] = []
        for day in days:
            for stop in day.places:
                if stop.latitude is None or stop.longitude is None:
                    continue
                points.append(
                    TripMapPointOut(
                        id=str(stop.id),
                        label=stop.title,
                        day_number=day.day_number,
                        latitude=stop.latitude,
                        longitude=stop.longitude,
                        href=f"/places/{stop.place_id}" if stop.place_id else None,
                    ),
                )
        return points
