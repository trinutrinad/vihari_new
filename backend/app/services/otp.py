"""OTP provider abstraction — mock implementation for local development."""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OtpDispatchResult:
    provider: str
    is_mock: bool
    debug_code: str | None = None


class OtpProvider(ABC):
    @abstractmethod
    def send_otp(self, *, phone: str, code: str, purpose: str) -> OtpDispatchResult:
        raise NotImplementedError


class MockOtpProvider(OtpProvider):
    """Logs OTP instead of sending SMS. Architecture allows real SMS later."""

    def send_otp(self, *, phone: str, code: str, purpose: str) -> OtpDispatchResult:
        logger.info(
            "MOCK OTP dispatched phone=%s purpose=%s code=%s",
            phone,
            purpose,
            code,
        )
        return OtpDispatchResult(provider="mock", is_mock=True, debug_code=code)


def get_otp_provider() -> OtpProvider:
    settings = get_settings()
    provider = settings.otp_provider.lower()
    if provider == "mock":
        return MockOtpProvider()
    # Future: TwilioOtpProvider, Msg91OtpProvider, etc.
    return MockOtpProvider()


def generate_otp_code(*, length: int = 6) -> str:
    upper = 10**length
    return f"{secrets.randbelow(upper):0{length}d}"


def hash_otp(code: str) -> str:
    settings = get_settings()
    digest = hmac.new(
        settings.secret_key.encode("utf-8"),
        code.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest


def verify_otp_hash(code: str, code_hash: str) -> bool:
    return hmac.compare_digest(hash_otp(code), code_hash)
