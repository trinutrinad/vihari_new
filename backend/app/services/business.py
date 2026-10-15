"""Business dashboard business logic."""

from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.models import Booking, User
from app.models.enums import BookingStatus, UserRole
from app.repositories.business import BusinessRepository
from app.schemas.business import (
    BusinessAccessOut,
    BusinessBookingOut,
    BusinessPropertyOut,
    BusinessSummaryOut,
)

BUSINESS_ROLES = frozenset(
    {
        UserRole.HOTEL_OWNER.value,
        UserRole.RESTAURANT_OWNER.value,
        UserRole.GUIDE.value,
        UserRole.TOUR_OPERATOR.value,
        UserRole.DRIVER.value,
    },
)


def user_business_roles(user: User) -> list[str]:
    role_names = {role.name for role in user.roles} | {user.primary_role}
    if user.primary_role == UserRole.SUPER_ADMIN.value or UserRole.SUPER_ADMIN.value in role_names:
        return sorted(BUSINESS_ROLES | {UserRole.SUPER_ADMIN.value})
    return sorted(role_names & BUSINESS_ROLES)


def has_business_access(user: User) -> bool:
    role_names = {role.name for role in user.roles} | {user.primary_role}
    if user.primary_role == UserRole.SUPER_ADMIN.value or UserRole.SUPER_ADMIN.value in role_names:
        return True
    return not role_names.isdisjoint(BUSINESS_ROLES)


class BusinessService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = BusinessRepository(db)

    def access(self, *, user: User) -> BusinessAccessOut:
        roles = user_business_roles(user)
        hotels = self.repo.list_hotels(owner_user_id=user.id)
        restaurants = self.repo.list_restaurants(owner_user_id=user.id)
        guides = self.repo.list_guides(user_id=user.id)
        return BusinessAccessOut(
            has_access=has_business_access(user),
            roles=roles,
            hotels_count=len(hotels),
            restaurants_count=len(restaurants),
            guides_count=len(guides),
        )

    def summary(self, *, user: User) -> BusinessSummaryOut:
        hotels = self.repo.list_hotels(owner_user_id=user.id)
        restaurants = self.repo.list_restaurants(owner_user_id=user.id)
        guides = self.repo.list_guides(user_id=user.id)
        pairs = self.repo.owned_resource_pairs(owner_user_id=user.id)
        status_counts = self.repo.booking_status_counts(resource_pairs=pairs)
        total = sum(status_counts.values())
        return BusinessSummaryOut(
            hotels_count=len(hotels),
            restaurants_count=len(restaurants),
            guides_count=len(guides),
            bookings_total=total,
            bookings_pending=status_counts.get(BookingStatus.PENDING.value, 0),
            bookings_confirmed=status_counts.get(BookingStatus.CONFIRMED.value, 0),
            bookings_cancelled=status_counts.get(BookingStatus.CANCELLED.value, 0),
            bookings_completed=status_counts.get(BookingStatus.COMPLETED.value, 0),
            revenue_captured_inr=self.repo.captured_revenue_inr(resource_pairs=pairs),
        )

    def list_properties(self, *, user: User) -> list[BusinessPropertyOut]:
        items: list[BusinessPropertyOut] = []
        for hotel in self.repo.list_hotels(owner_user_id=user.id):
            items.append(
                BusinessPropertyOut(
                    id=hotel.id,
                    resource_type="hotel",
                    name=hotel.name,
                    slug=hotel.slug,
                    city_name=hotel.city.name if hotel.city else None,
                    rating_avg=float(hotel.rating_avg) if hotel.rating_avg is not None else None,
                    rating_count=hotel.rating_count or 0,
                    href=f"/hotels/{hotel.id}",
                    is_seed_data=bool(hotel.is_seed_data),
                ),
            )
        for restaurant in self.repo.list_restaurants(owner_user_id=user.id):
            items.append(
                BusinessPropertyOut(
                    id=restaurant.id,
                    resource_type="restaurant",
                    name=restaurant.name,
                    slug=restaurant.slug,
                    city_name=restaurant.city.name if restaurant.city else None,
                    rating_avg=(
                        float(restaurant.rating_avg)
                        if restaurant.rating_avg is not None
                        else None
                    ),
                    rating_count=restaurant.rating_count or 0,
                    href=f"/restaurants/{restaurant.id}",
                    is_seed_data=bool(restaurant.is_seed_data),
                ),
            )
        for guide in self.repo.list_guides(user_id=user.id):
            items.append(
                BusinessPropertyOut(
                    id=guide.id,
                    resource_type="guide",
                    name=guide.display_name,
                    slug=None,
                    city_name=guide.city.name if guide.city else None,
                    rating_avg=float(guide.rating_avg) if guide.rating_avg is not None else None,
                    rating_count=guide.rating_count or 0,
                    href=f"/guides/{guide.id}",
                    is_seed_data=bool(guide.is_seed_data),
                ),
            )
        return items

    def list_bookings(self, *, user: User, limit: int = 50) -> list[BusinessBookingOut]:
        pairs = self.repo.owned_resource_pairs(owner_user_id=user.id)
        titles = self.repo.property_title_map(owner_user_id=user.id)
        bookings = self.repo.list_bookings_for_resources(
            resource_pairs=pairs,
            limit=limit,
        )
        return [self._booking_out(booking, titles) for booking in bookings]

    def _booking_out(
        self,
        booking: Booking,
        titles: dict[tuple[str, uuid.UUID], str],
    ) -> BusinessBookingOut:
        key = (booking.resource_type, booking.resource_id)
        title = (
            titles.get(key)
            or self._title_from_metadata(booking)
            or booking.resource_type.title()
        )
        return BusinessBookingOut(
            id=booking.id,
            booking_number=booking.booking_number,
            resource_type=booking.resource_type,
            resource_id=booking.resource_id,
            resource_title=title,
            status=booking.status,
            amount_inr=booking.amount_inr,
            currency=booking.currency,
            scheduled_at=booking.scheduled_at,
            location_text=booking.location_text,
            created_at=booking.created_at,
            is_mock=True,
        )

    def _title_from_metadata(self, booking: Booking) -> str | None:
        if not booking.metadata_json:
            return None
        try:
            meta = json.loads(booking.metadata_json)
        except json.JSONDecodeError:
            return None
        title = meta.get("title")
        return str(title) if title else None
