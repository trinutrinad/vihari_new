"""Admin dashboard business logic."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import (
    Activity,
    Booking,
    Guide,
    Hotel,
    Payment,
    Restaurant,
    SupportTicket,
    TouristPlace,
    User,
)
from app.models.enums import PaymentStatus, UserRole
from app.repositories.admin import AdminRepository
from app.schemas.admin import (
    AdminAccessOut,
    AdminBookingOut,
    AdminPaymentOut,
    AdminSummaryOut,
    AdminTicketOut,
    AdminUserOut,
)

ADMIN_ROLES = frozenset(
    {
        UserRole.ADMIN.value,
        UserRole.SUPER_ADMIN.value,
    },
)


def user_admin_roles(user: User) -> list[str]:
    role_names = {role.name for role in user.roles} | {user.primary_role}
    return sorted(role_names & ADMIN_ROLES)


def has_admin_access(user: User) -> bool:
    role_names = {role.name for role in user.roles} | {user.primary_role}
    return not role_names.isdisjoint(ADMIN_ROLES)


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AdminRepository(db)

    def access(self, *, user: User) -> AdminAccessOut:
        return AdminAccessOut(
            has_access=has_admin_access(user),
            roles=user_admin_roles(user),
        )

    def summary(self) -> AdminSummaryOut:
        return AdminSummaryOut(
            users_total=self.repo.count(User),
            users_active=self.repo.count_where(User, User.is_active.is_(True)),
            places_total=self.repo.count(TouristPlace),
            hotels_total=self.repo.count(Hotel),
            restaurants_total=self.repo.count(Restaurant),
            guides_total=self.repo.count(Guide),
            activities_total=self.repo.count(Activity),
            bookings_total=self.repo.count(Booking),
            bookings_open=self.repo.open_bookings(),
            payments_captured_total=self.repo.count_where(
                Payment,
                Payment.status == PaymentStatus.CAPTURED.value,
            ),
            revenue_captured_inr=self.repo.captured_revenue_inr(),
            support_tickets_open=self.repo.count_where(
                SupportTicket,
                SupportTicket.status == "open",
            ),
            seed_entities_total=self.repo.seed_entity_total(),
        )

    def list_users(self, *, limit: int = 50) -> list[AdminUserOut]:
        return [
            AdminUserOut(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                phone=user.phone,
                primary_role=user.primary_role,
                is_active=user.is_active,
                is_seed_data=bool(user.is_seed_data),
                created_at=user.created_at,
            )
            for user in self.repo.list_users(limit=limit)
        ]

    def list_bookings(self, *, limit: int = 50) -> list[AdminBookingOut]:
        return [
            AdminBookingOut(
                id=booking.id,
                booking_number=booking.booking_number,
                resource_type=booking.resource_type,
                resource_id=booking.resource_id,
                status=booking.status,
                amount_inr=booking.amount_inr,
                currency=booking.currency,
                user_id=booking.user_id,
                created_at=booking.created_at,
            )
            for booking in self.repo.list_bookings(limit=limit)
        ]

    def list_payments(self, *, limit: int = 50) -> list[AdminPaymentOut]:
        return [
            AdminPaymentOut(
                id=payment.id,
                payment_number=payment.payment_number,
                amount_inr=payment.amount_inr,
                status=payment.status,
                method=payment.method,
                user_id=payment.user_id,
                booking_id=payment.booking_id,
                is_mock=bool(payment.is_mock),
                created_at=payment.created_at,
            )
            for payment in self.repo.list_payments(limit=limit)
        ]

    def list_tickets(self, *, limit: int = 50, open_only: bool = False) -> list[AdminTicketOut]:
        return [
            AdminTicketOut(
                id=ticket.id,
                ticket_number=ticket.ticket_number,
                subject=ticket.subject,
                status=ticket.status,
                priority=ticket.priority,
                user_id=ticket.user_id,
                created_at=ticket.created_at,
            )
            for ticket in self.repo.list_tickets(limit=limit, open_only=open_only)
        ]
