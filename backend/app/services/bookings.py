"""Mock bookings business logic (Phase 16)."""

from __future__ import annotations

import json
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError, ValidationAppError
from app.models import (
    Activity,
    ActivityBooking,
    Booking,
    City,
    FoodOrder,
    Guide,
    GuideBooking,
    Hotel,
    Restaurant,
    Ride,
    TransportOption,
)
from app.models.enums import BookingStatus, RideStatus
from app.repositories.bookings import BookingRepository
from app.schemas.bookings import (
    BookingCancel,
    BookingCreate,
    BookingDetailOut,
    BookingSummaryOut,
)
from app.services.transport import _estimate_fare


class BookingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = BookingRepository(db)

    def list_bookings(
        self,
        *,
        user_id: uuid.UUID,
        status: str | None = None,
        resource_type: str | None = None,
    ) -> list[BookingSummaryOut]:
        rows = self.repo.list_for_user(
            user_id=user_id,
            status=status,
            resource_type=resource_type,
        )
        return [self._to_summary(row) for row in rows]

    def get_booking(self, *, booking_id: uuid.UUID, user_id: uuid.UUID) -> BookingDetailOut:
        booking = self.repo.get_for_user(booking_id=booking_id, user_id=user_id)
        if booking is None:
            raise NotFoundError("Booking not found")
        return self._to_detail(booking)

    def create_booking(
        self,
        *,
        user_id: uuid.UUID,
        payload: BookingCreate,
    ) -> BookingDetailOut:
        now = datetime.now(UTC)
        scheduled_at = payload.scheduled_at or (now + timedelta(days=1))
        resolved = self._resolve_resource(
            user_id=user_id,
            payload=payload,
            scheduled_at=scheduled_at,
        )

        booking = Booking(
            user_id=user_id,
            booking_number=_booking_number("BY"),
            resource_type=payload.resource_type,
            resource_id=payload.resource_id,
            status=BookingStatus.CONFIRMED.value,
            scheduled_at=scheduled_at,
            amount_inr=resolved["amount_inr"],
            currency="INR",
            provider="mock",
            location_text=resolved.get("location_text"),
            metadata_json=json.dumps(
                {
                    "title": resolved["title"],
                    "href": resolved.get("href"),
                    "notes": payload.notes,
                    "extras": resolved.get("extras") or {},
                    "is_mock": True,
                },
            ),
        )
        self.repo.add(booking)

        domain = resolved.get("domain")
        if domain is not None:
            self.db.add(domain)

        self.db.commit()
        self.db.refresh(booking)
        from app.services.notify import notify_user

        notify_user(
            self.db,
            user_id=user_id,
            title="Booking confirmed (mock)",
            body=f"{resolved['title']} · {booking.booking_number} · ₹{booking.amount_inr}",
            category="booking",
            payload={
                "booking_id": str(booking.id),
                "href": f"/bookings/{booking.id}",
            },
        )
        return self._to_detail(booking)

    def cancel_booking(
        self,
        *,
        booking_id: uuid.UUID,
        user_id: uuid.UUID,
        payload: BookingCancel,
    ) -> BookingDetailOut:
        booking = self.repo.get_for_user(booking_id=booking_id, user_id=user_id)
        if booking is None:
            raise NotFoundError("Booking not found")
        if booking.status == BookingStatus.CANCELLED.value:
            raise ValidationAppError("Booking is already cancelled")
        if booking.status == BookingStatus.COMPLETED.value:
            raise ValidationAppError("Completed bookings cannot be cancelled")

        booking.status = BookingStatus.CANCELLED.value
        booking.cancellation_reason = payload.reason or "Cancelled by traveller (mock)"
        self.db.commit()
        self.db.refresh(booking)
        from app.services.notify import notify_user

        notify_user(
            self.db,
            user_id=user_id,
            title="Booking cancelled",
            body=f"{booking.booking_number} was cancelled (mock).",
            category="booking",
            payload={
                "booking_id": str(booking.id),
                "href": f"/bookings/{booking.id}",
            },
        )
        return self._to_detail(booking)

    def _resolve_resource(
        self,
        *,
        user_id: uuid.UUID,
        payload: BookingCreate,
        scheduled_at: datetime,
    ) -> dict[str, Any]:
        if payload.resource_type == "hotel":
            return self._resolve_hotel(payload)
        if payload.resource_type == "guide":
            return self._resolve_guide(user_id, payload, scheduled_at)
        if payload.resource_type == "activity":
            return self._resolve_activity(user_id, payload, scheduled_at)
        if payload.resource_type == "transport":
            return self._resolve_transport(user_id, payload, scheduled_at)
        if payload.resource_type == "restaurant":
            return self._resolve_restaurant(user_id, payload)
        raise ValidationAppError("Unsupported resource type")

    def _resolve_hotel(self, payload: BookingCreate) -> dict[str, Any]:
        hotel = self.db.scalar(
            select(Hotel)
            .where(Hotel.id == payload.resource_id, Hotel.is_deleted.is_(False))
            .options(selectinload(Hotel.city)),
        )
        if hotel is None:
            raise NotFoundError("Hotel not found")
        nights = payload.nights or 1
        unit = hotel.starting_price_inr or 1500
        city = hotel.city.name if hotel.city else ""
        return {
            "title": hotel.name,
            "href": f"/hotels/{hotel.id}",
            "amount_inr": unit * nights,
            "location_text": city or hotel.address,
            "extras": {"nights": nights, "unit_price_inr": unit},
        }

    def _resolve_guide(
        self,
        user_id: uuid.UUID,
        payload: BookingCreate,
        scheduled_at: datetime,
    ) -> dict[str, Any]:
        guide = self.db.scalar(
            select(Guide)
            .where(Guide.id == payload.resource_id, Guide.is_active.is_(True))
            .options(selectinload(Guide.city).selectinload(City.state)),
        )
        if guide is None:
            raise NotFoundError("Guide not found")
        days = payload.duration_days or 1
        amount = guide.price_per_day_inr * days
        end_at = scheduled_at + timedelta(days=days)
        return {
            "title": guide.display_name,
            "href": f"/guides/{guide.id}",
            "amount_inr": amount,
            "location_text": (
                f"{guide.city.name}, {guide.city.state.name}"
                if guide.city and guide.city.state
                else None
            ),
            "extras": {"duration_days": days},
            "domain": GuideBooking(
                guide_id=guide.id,
                user_id=user_id,
                booking_number=_booking_number("GB"),
                start_at=scheduled_at,
                end_at=end_at,
                duration_days=days,
                total_amount_inr=amount,
                status=BookingStatus.CONFIRMED.value,
                is_mock=True,
            ),
        }

    def _resolve_activity(
        self,
        user_id: uuid.UUID,
        payload: BookingCreate,
        scheduled_at: datetime,
    ) -> dict[str, Any]:
        activity = self.db.scalar(
            select(Activity)
            .where(
                Activity.id == payload.resource_id,
                Activity.is_deleted.is_(False),
                Activity.is_available.is_(True),
            )
            .options(selectinload(Activity.city).selectinload(City.state)),
        )
        if activity is None:
            raise NotFoundError("Activity not found")
        participants = payload.participants or 1
        amount = activity.price_inr * participants
        return {
            "title": activity.name,
            "href": f"/activities/{activity.id}",
            "amount_inr": amount,
            "location_text": (
                f"{activity.city.name}, {activity.city.state.name}"
                if activity.city and activity.city.state
                else None
            ),
            "extras": {"participants": participants},
            "domain": ActivityBooking(
                activity_id=activity.id,
                user_id=user_id,
                booking_number=_booking_number("AB"),
                scheduled_at=scheduled_at,
                participants=participants,
                total_amount_inr=amount,
                status=BookingStatus.CONFIRMED.value,
                is_mock=True,
            ),
        }

    def _resolve_transport(
        self,
        user_id: uuid.UUID,
        payload: BookingCreate,
        scheduled_at: datetime,
    ) -> dict[str, Any]:
        option = self.db.scalar(
            select(TransportOption).where(
                TransportOption.id == payload.resource_id,
                TransportOption.is_active.is_(True),
            ),
        )
        if option is None:
            raise NotFoundError("Transport option not found")
        distance = payload.distance_km or 10.0
        estimated = _estimate_fare(option, distance)
        amount = estimated if estimated is not None else max(option.base_fare_inr, 100)
        return {
            "title": option.name,
            "href": f"/transport/{option.id}",
            "amount_inr": amount,
            "location_text": "Local transfer (demo)",
            "extras": {
                "distance_km": distance,
                "vehicle_type": option.vehicle_type,
                "code": option.code,
            },
            "domain": Ride(
                user_id=user_id,
                ride_number=_booking_number("RD"),
                vehicle_type=option.vehicle_type,
                pickup_address="Demo pickup point",
                dropoff_address="Demo dropoff point",
                estimated_fare_inr=amount,
                final_fare_inr=amount,
                distance_km=distance,
                eta_minutes=max(5, int(distance * 3)),
                status=RideStatus.COMPLETED.value,
                started_at=scheduled_at,
                completed_at=scheduled_at + timedelta(minutes=max(5, int(distance * 3))),
                is_mock=True,
            ),
        }

    def _resolve_restaurant(
        self,
        user_id: uuid.UUID,
        payload: BookingCreate,
    ) -> dict[str, Any]:
        restaurant = self.db.scalar(
            select(Restaurant)
            .where(
                Restaurant.id == payload.resource_id,
                Restaurant.is_deleted.is_(False),
            )
            .options(
                selectinload(Restaurant.city).selectinload(City.state),
                selectinload(Restaurant.menu_items),
            ),
        )
        if restaurant is None:
            raise NotFoundError("Restaurant not found")
        menu = [item for item in restaurant.menu_items if item.is_available]
        if menu:
            amount = min(item.price_inr for item in menu)
        else:
            amount = 249
        return {
            "title": restaurant.name,
            "href": f"/restaurants/{restaurant.id}",
            "amount_inr": amount,
            "location_text": (
                f"{restaurant.city.name}, {restaurant.city.state.name}"
                if restaurant.city and restaurant.city.state
                else restaurant.address
            ),
            "extras": {"order_style": "demo_single_item"},
            "domain": FoodOrder(
                user_id=user_id,
                restaurant_id=restaurant.id,
                order_number=_booking_number("FO"),
                status=BookingStatus.CONFIRMED.value,
                total_amount_inr=amount,
                notes=payload.notes or "Mock demo food order",
                is_mock=True,
            ),
        }

    def _to_summary(self, booking: Booking) -> BookingSummaryOut:
        meta = _parse_meta(booking.metadata_json)
        return BookingSummaryOut(
            id=booking.id,
            booking_number=booking.booking_number,
            resource_type=booking.resource_type,
            resource_id=booking.resource_id,
            resource_title=str(meta.get("title") or booking.resource_type.title()),
            resource_href=meta.get("href"),
            status=booking.status,
            scheduled_at=booking.scheduled_at,
            amount_inr=booking.amount_inr,
            currency=booking.currency,
            provider=booking.provider,
            location_text=booking.location_text,
            is_mock=(booking.provider == "mock") or bool(meta.get("is_mock", True)),
            created_at=booking.created_at,
        )

    def _to_detail(self, booking: Booking) -> BookingDetailOut:
        summary = self._to_summary(booking)
        meta = _parse_meta(booking.metadata_json)
        return BookingDetailOut(
            **summary.model_dump(),
            cancellation_reason=booking.cancellation_reason,
            notes=meta.get("notes"),
            metadata=meta,
        )


def _booking_number(prefix: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    return f"{prefix}-{stamp}-{secrets.token_hex(3).upper()}"


def _parse_meta(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
