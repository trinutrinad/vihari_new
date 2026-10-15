"""Mock payments, wallet, and coupon business logic."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationAppError
from app.models import Payment
from app.models.enums import BookingStatus, PaymentMethod, PaymentStatus
from app.repositories.payments import PaymentRepository
from app.schemas.payments import (
    CouponOut,
    PaymentCreate,
    PaymentDetailOut,
    PaymentSummaryOut,
    WalletOut,
    WalletTopUp,
)
from app.services.payment_provider import PaymentProvider, get_payment_provider


class PaymentService:
    def __init__(
        self,
        db: Session,
        provider: PaymentProvider | None = None,
    ) -> None:
        self.db = db
        self.repo = PaymentRepository(db)
        self.provider = provider or get_payment_provider()

    def list_payments(
        self,
        *,
        user_id: uuid.UUID,
        status: str | None = None,
        booking_id: uuid.UUID | None = None,
    ) -> list[PaymentSummaryOut]:
        rows = self.repo.list_for_user(
            user_id=user_id,
            status=status,
            booking_id=booking_id,
        )
        return [self._to_summary(row) for row in rows]

    def get_payment(self, *, payment_id: uuid.UUID, user_id: uuid.UUID) -> PaymentDetailOut:
        payment = self.repo.get_for_user(payment_id=payment_id, user_id=user_id)
        if payment is None:
            raise NotFoundError("Payment not found")
        return self._to_detail(payment)

    def create_payment(
        self,
        *,
        user_id: uuid.UUID,
        payload: PaymentCreate,
    ) -> PaymentDetailOut:
        booking = self.repo.get_booking_for_user(
            booking_id=payload.booking_id,
            user_id=user_id,
        )
        if booking is None:
            raise NotFoundError("Booking not found")
        if booking.status == BookingStatus.CANCELLED.value:
            raise ValidationAppError("Cannot pay for a cancelled booking")

        existing = self.repo.find_captured_for_booking(booking.id)
        if existing is not None:
            raise ConflictError("Booking already has a captured payment")

        amount = booking.amount_inr
        coupon = None
        if payload.coupon_code:
            coupon = self.repo.get_coupon_by_code(payload.coupon_code)
            if coupon is None or not coupon.is_active:
                raise ValidationAppError("Invalid or inactive coupon")
            if coupon.valid_until and coupon.valid_until < datetime.now(UTC):
                raise ValidationAppError("Coupon has expired")
            if (
                coupon.max_redemptions is not None
                and coupon.redeemed_count >= coupon.max_redemptions
            ):
                raise ValidationAppError("Coupon redemption limit reached")
            amount = _apply_coupon(amount, coupon)

        method = payload.method
        if method not in {item.value for item in PaymentMethod}:
            raise ValidationAppError("Unsupported payment method")

        wallet = None
        if method == PaymentMethod.WALLET.value:
            wallet = self.repo.get_or_create_wallet(user_id)
            if not wallet.is_active:
                raise ValidationAppError("Wallet is inactive")
            if Decimal(wallet.balance_inr) < Decimal(amount):
                raise ValidationAppError("Insufficient wallet balance")

        payment_number = _payment_number()
        result = self.provider.charge(
            amount_inr=amount,
            method=method,
            payment_number=payment_number,
        )
        if not result.ok:
            payment = Payment(
                user_id=user_id,
                booking_id=booking.id,
                payment_number=payment_number,
                amount_inr=amount,
                method=method,
                status=PaymentStatus.FAILED.value,
                provider="mock",
                failure_reason=result.message,
                coupon_id=coupon.id if coupon else None,
                is_mock=True,
            )
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)
            return self._to_detail(payment)

        if wallet is not None:
            wallet.balance_inr = Decimal(wallet.balance_inr) - Decimal(amount)

        if coupon is not None:
            coupon.redeemed_count += 1

        payment = Payment(
            user_id=user_id,
            booking_id=booking.id,
            payment_number=payment_number,
            amount_inr=amount,
            method=method,
            status=PaymentStatus.CAPTURED.value,
            provider="mock",
            provider_reference=result.reference,
            coupon_id=coupon.id if coupon else None,
            paid_at=datetime.now(UTC),
            is_mock=True,
        )
        self.db.add(payment)
        self.db.commit()
        refreshed = self.repo.get_for_user(payment_id=payment.id, user_id=user_id)
        assert refreshed is not None
        from app.services.notify import notify_user

        notify_user(
            self.db,
            user_id=user_id,
            title="Payment captured (mock)",
            body=f"{refreshed.payment_number} · ₹{refreshed.amount_inr} via {refreshed.method}",
            category="payment",
            payload={
                "payment_id": str(refreshed.id),
                "booking_id": str(refreshed.booking_id) if refreshed.booking_id else None,
                "href": f"/payments/{refreshed.id}",
            },
        )
        return self._to_detail(refreshed)

    def refund_payment(
        self,
        *,
        payment_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> PaymentDetailOut:
        payment = self.repo.get_for_user(payment_id=payment_id, user_id=user_id)
        if payment is None:
            raise NotFoundError("Payment not found")
        if payment.status != PaymentStatus.CAPTURED.value:
            raise ValidationAppError("Only captured payments can be refunded")

        result = self.provider.refund(
            provider_reference=payment.provider_reference or payment.payment_number,
            amount_inr=payment.amount_inr,
        )
        if not result.ok:
            raise ValidationAppError(result.message or "Refund failed")

        if payment.method == PaymentMethod.WALLET.value:
            wallet = self.repo.get_or_create_wallet(user_id)
            wallet.balance_inr = Decimal(wallet.balance_inr) + Decimal(payment.amount_inr)

        payment.status = PaymentStatus.REFUNDED.value
        payment.provider_reference = result.reference
        self.db.commit()
        self.db.refresh(payment)
        return self._to_detail(payment)

    def get_wallet(self, *, user_id: uuid.UUID) -> WalletOut:
        wallet = self.repo.get_or_create_wallet(user_id)
        self.db.commit()
        self.db.refresh(wallet)
        return WalletOut(
            id=wallet.id,
            balance_inr=wallet.balance_inr,
            currency=wallet.currency,
            is_active=wallet.is_active,
        )

    def top_up_wallet(self, *, user_id: uuid.UUID, payload: WalletTopUp) -> WalletOut:
        wallet = self.repo.get_or_create_wallet(user_id)
        if not wallet.is_active:
            raise ValidationAppError("Wallet is inactive")
        wallet.balance_inr = Decimal(wallet.balance_inr) + Decimal(payload.amount_inr)
        self.db.commit()
        self.db.refresh(wallet)
        return WalletOut(
            id=wallet.id,
            balance_inr=wallet.balance_inr,
            currency=wallet.currency,
            is_active=wallet.is_active,
        )

    def get_coupon(self, *, code: str) -> CouponOut:
        coupon = self.repo.get_coupon_by_code(code)
        if coupon is None or not coupon.is_active:
            raise NotFoundError("Coupon not found")
        return CouponOut(
            code=coupon.code,
            description=coupon.description,
            discount_percent=coupon.discount_percent,
            discount_amount_inr=coupon.discount_amount_inr,
            is_active=coupon.is_active,
            is_seed_data=coupon.is_seed_data,
        )

    def _to_summary(self, payment: Payment) -> PaymentSummaryOut:
        return PaymentSummaryOut(
            id=payment.id,
            payment_number=payment.payment_number,
            booking_id=payment.booking_id,
            booking_number=payment.booking.booking_number if payment.booking else None,
            amount_inr=payment.amount_inr,
            currency=payment.currency,
            method=payment.method,
            status=payment.status,
            provider=payment.provider,
            provider_reference=payment.provider_reference,
            coupon_code=payment.coupon.code if payment.coupon else None,
            paid_at=payment.paid_at,
            is_mock=payment.is_mock,
            created_at=payment.created_at,
        )

    def _to_detail(self, payment: Payment) -> PaymentDetailOut:
        summary = self._to_summary(payment)
        return PaymentDetailOut(
            **summary.model_dump(),
            failure_reason=payment.failure_reason,
        )


def _payment_number() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d")
    return f"PAY-{stamp}-{secrets.token_hex(3).upper()}"


def _apply_coupon(amount: int, coupon) -> int:
    if coupon.discount_percent:
        return max(0, int(round(amount * (100 - coupon.discount_percent) / 100)))
    if coupon.discount_amount_inr:
        return max(0, amount - coupon.discount_amount_inr)
    return amount
