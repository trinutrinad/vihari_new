"""Notification provider abstraction (in-app now; FCM/SMS/email later)."""

from __future__ import annotations

import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Notification
from app.models.enums import NotificationChannel

logger = logging.getLogger(__name__)


@dataclass
class NotificationDispatchResult:
    ok: bool
    provider: str
    channel: str
    notification_id: uuid.UUID | None = None
    is_mock: bool = True
    message: str = ""


class NotificationProvider(ABC):
    @abstractmethod
    def send(
        self,
        *,
        db: Session,
        user_id: uuid.UUID,
        title: str,
        body: str,
        category: str | None = None,
        payload: dict[str, Any] | None = None,
        channel: str = NotificationChannel.IN_APP.value,
    ) -> NotificationDispatchResult:
        raise NotImplementedError


class InAppNotificationProvider(NotificationProvider):
    """Persists in-app notifications. Push/SMS channels log only for now."""

    def send(
        self,
        *,
        db: Session,
        user_id: uuid.UUID,
        title: str,
        body: str,
        category: str | None = None,
        payload: dict[str, Any] | None = None,
        channel: str = NotificationChannel.IN_APP.value,
    ) -> NotificationDispatchResult:
        if channel != NotificationChannel.IN_APP.value:
            logger.info(
                "MOCK channel=%s notification user=%s title=%s",
                channel,
                user_id,
                title,
            )
        row = Notification(
            user_id=user_id,
            title=title,
            body=body,
            category=category,
            channel=NotificationChannel.IN_APP.value,
            is_read=False,
            payload_json=json.dumps(payload) if payload else None,
        )
        db.add(row)
        db.flush()
        return NotificationDispatchResult(
            ok=True,
            provider="in_app",
            channel=NotificationChannel.IN_APP.value,
            notification_id=row.id,
            is_mock=True,
            message="In-app notification stored",
        )


def get_notification_provider() -> NotificationProvider:
    settings = get_settings()
    provider = getattr(settings, "notification_provider", "in_app")
    provider = str(provider or "in_app").lower()
    if provider in {"in_app", "mock"}:
        return InAppNotificationProvider()
    # Future: FcmNotificationProvider, SmsNotificationProvider, etc.
    return InAppNotificationProvider()
