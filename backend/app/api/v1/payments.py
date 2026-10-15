"""Payments and wallet API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.payments import (
    CouponOut,
    PaymentCreate,
    PaymentDetailOut,
    PaymentSummaryOut,
    WalletOut,
    WalletTopUp,
)
from app.services.payments import PaymentService

router = APIRouter()


@router.get("/payments", response_model=ApiResponse[list[PaymentSummaryOut]])
def list_payments(
    db: DbSession,
    current_user: CurrentUser,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    booking_id: UUID | None = None,
) -> ApiResponse[list[PaymentSummaryOut]]:
    data = PaymentService(db).list_payments(
        user_id=current_user.id,
        status=status_filter,
        booking_id=booking_id,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.post(
    "/payments",
    response_model=ApiResponse[PaymentDetailOut],
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payload: PaymentCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[PaymentDetailOut]:
    data = PaymentService(db).create_payment(user_id=current_user.id, payload=payload)
    return ApiResponse(success=True, message="Payment captured (mock)", data=data)


@router.get("/payments/{payment_id}", response_model=ApiResponse[PaymentDetailOut])
def get_payment(
    payment_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[PaymentDetailOut]:
    data = PaymentService(db).get_payment(
        payment_id=payment_id,
        user_id=current_user.id,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.post(
    "/payments/{payment_id}/refund",
    response_model=ApiResponse[PaymentDetailOut],
)
def refund_payment(
    payment_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[PaymentDetailOut]:
    data = PaymentService(db).refund_payment(
        payment_id=payment_id,
        user_id=current_user.id,
    )
    return ApiResponse(success=True, message="Payment refunded (mock)", data=data)


@router.get("/wallet", response_model=ApiResponse[WalletOut])
def get_wallet(db: DbSession, current_user: CurrentUser) -> ApiResponse[WalletOut]:
    data = PaymentService(db).get_wallet(user_id=current_user.id)
    return ApiResponse(success=True, message="OK", data=data)


@router.post("/wallet/topup", response_model=ApiResponse[WalletOut])
def top_up_wallet(
    payload: WalletTopUp,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[WalletOut]:
    data = PaymentService(db).top_up_wallet(user_id=current_user.id, payload=payload)
    return ApiResponse(success=True, message="Wallet topped up (mock)", data=data)


@router.get("/coupons/{code}", response_model=ApiResponse[CouponOut])
def get_coupon(code: str, db: DbSession) -> ApiResponse[CouponOut]:
    data = PaymentService(db).get_coupon(code=code)
    return ApiResponse(success=True, message="OK", data=data)
