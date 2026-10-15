"""Payment and wallet API schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

PaymentMethodLiteral = Literal["mock", "upi", "card", "net_banking", "wallet", "cash"]


class PaymentCreate(BaseModel):
    booking_id: UUID
    method: PaymentMethodLiteral = "mock"
    coupon_code: str | None = Field(default=None, max_length=40)


class WalletTopUp(BaseModel):
    amount_inr: int = Field(ge=1, le=50000)


class PaymentSummaryOut(BaseModel):
    id: UUID
    payment_number: str
    booking_id: UUID | None = None
    booking_number: str | None = None
    amount_inr: int
    currency: str = "INR"
    method: str
    status: str
    provider: str
    provider_reference: str | None = None
    coupon_code: str | None = None
    paid_at: datetime | None = None
    is_mock: bool = True
    created_at: datetime | None = None


class PaymentDetailOut(PaymentSummaryOut):
    failure_reason: str | None = None
    data_notice: str = (
        "Mock payments capture instantly for demo UX. "
        "No real money is charged. Live gateways arrive later."
    )


class WalletOut(BaseModel):
    id: UUID
    balance_inr: Decimal
    currency: str = "INR"
    is_active: bool = True
    data_notice: str = (
        "Demo wallet balance is fictional. Top-ups are mock credits only."
    )


class CouponOut(BaseModel):
    code: str
    description: str | None = None
    discount_percent: int | None = None
    discount_amount_inr: int | None = None
    is_active: bool = True
    is_seed_data: bool = False
