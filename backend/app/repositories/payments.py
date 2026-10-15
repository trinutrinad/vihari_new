"""Payment and wallet data-access helpers."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Booking, Coupon, Payment, Wallet


class PaymentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_user(
        self,
        *,
        user_id: uuid.UUID,
        status: str | None = None,
        booking_id: uuid.UUID | None = None,
    ) -> list[Payment]:
        query = (
            select(Payment)
            .where(Payment.user_id == user_id)
            .options(selectinload(Payment.booking), selectinload(Payment.coupon))
        )
        if status:
            query = query.where(Payment.status == status.strip().lower())
        if booking_id is not None:
            query = query.where(Payment.booking_id == booking_id)
        return list(self.db.scalars(query.order_by(Payment.created_at.desc())).all())

    def get_for_user(
        self,
        *,
        payment_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Payment | None:
        return self.db.scalar(
            select(Payment)
            .where(Payment.id == payment_id, Payment.user_id == user_id)
            .options(selectinload(Payment.booking), selectinload(Payment.coupon)),
        )

    def find_captured_for_booking(self, booking_id: uuid.UUID) -> Payment | None:
        return self.db.scalar(
            select(Payment).where(
                Payment.booking_id == booking_id,
                Payment.status.in_(("captured", "authorized")),
            ),
        )

    def get_coupon_by_code(self, code: str) -> Coupon | None:
        return self.db.scalar(
            select(Coupon).where(Coupon.code == code.strip().upper()),
        )

    def get_or_create_wallet(self, user_id: uuid.UUID) -> Wallet:
        wallet = self.db.scalar(select(Wallet).where(Wallet.user_id == user_id))
        if wallet is not None:
            return wallet
        wallet = Wallet(
            user_id=user_id,
            balance_inr=Decimal("0.00"),
            currency="INR",
            is_active=True,
        )
        self.db.add(wallet)
        self.db.flush()
        return wallet

    def get_booking_for_user(
        self,
        *,
        booking_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Booking | None:
        return self.db.scalar(
            select(Booking).where(Booking.id == booking_id, Booking.user_id == user_id),
        )
