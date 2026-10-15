"""Payment provider abstraction (mock now, Razorpay/Stripe later)."""

from __future__ import annotations

import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import get_settings


@dataclass
class ProviderChargeResult:
    ok: bool
    reference: str
    status: str
    message: str


class PaymentProvider(ABC):
    @abstractmethod
    def charge(
        self,
        *,
        amount_inr: int,
        method: str,
        payment_number: str,
    ) -> ProviderChargeResult:
        raise NotImplementedError

    @abstractmethod
    def refund(self, *, provider_reference: str, amount_inr: int) -> ProviderChargeResult:
        raise NotImplementedError


class MockPaymentProvider(PaymentProvider):
    """Instant capture/refund for demo — never moves real money."""

    def charge(
        self,
        *,
        amount_inr: int,
        method: str,
        payment_number: str,
    ) -> ProviderChargeResult:
        if amount_inr <= 0:
            return ProviderChargeResult(
                ok=False,
                reference="",
                status="failed",
                message="Amount must be positive",
            )
        reference = f"MOCK-{payment_number}-{secrets.token_hex(4).upper()}"
        return ProviderChargeResult(
            ok=True,
            reference=reference,
            status="captured",
            message=f"Mock {method} charge captured",
        )

    def refund(self, *, provider_reference: str, amount_inr: int) -> ProviderChargeResult:
        return ProviderChargeResult(
            ok=True,
            reference=f"REF-{provider_reference}",
            status="refunded",
            message=f"Mock refund of ₹{amount_inr}",
        )


def get_payment_provider() -> PaymentProvider:
    settings = get_settings()
    provider = (settings.payment_provider or "mock").lower()
    if provider == "mock":
        return MockPaymentProvider()
    # Future: RazorpayPaymentProvider, StripePaymentProvider
    return MockPaymentProvider()
