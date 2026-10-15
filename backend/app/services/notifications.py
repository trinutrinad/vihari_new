"""In-app notifications business logic."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Notification
from app.repositories.notifications import NotificationRepository
from app.schemas.notifications import (
    DemoNotificationCreate,
    NotificationOut,
    UnreadCountOut,
)
from app.services.notification_provider import (
    NotificationProvider,
    get_notification_provider,
)


class NotificationService:
    def __init__(
        self,
        db: Session,
        provider: NotificationProvider | None = None,
    ) -> None:
        self.db = db
        self.repo = NotificationRepository(db)
        self.provider = provider or get_notification_provider()

    def list_notifications(
        self,
        *,
        user_id: uuid.UUID,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[NotificationOut]:
        rows = self.repo.list_for_user(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
        )
        return [self._to_out(row) for row in rows]

    def unread_count(self, *, user_id: uuid.UUID) -> UnreadCountOut:
        return UnreadCountOut(unread_count=self.repo.unread_count(user_id=user_id))

    def get_notification(
        self,
        *,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> NotificationOut:
        row = self.repo.get_for_user(notification_id=notification_id, user_id=user_id)
        if row is None:
            raise NotFoundError("Notification not found")
        return self._to_out(row)

    def mark_read(
        self,
        *,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> NotificationOut:
        row = self.repo.get_for_user(notification_id=notification_id, user_id=user_id)
        if row is None:
            raise NotFoundError("Notification not found")
        if not row.is_read:
            row.is_read = True
            row.read_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(row)
        return self._to_out(row)

    def mark_all_read(self, *, user_id: uuid.UUID) -> UnreadCountOut:
        self.repo.mark_all_read(user_id=user_id, read_at=datetime.now(UTC))
        self.db.commit()
        return UnreadCountOut(unread_count=0)

    def create_demo(
        self,
        *,
        user_id: uuid.UUID,
        payload: DemoNotificationCreate,
    ) -> NotificationOut:
        return self.notify(
            user_id=user_id,
            title=payload.title,
            body=payload.body,
            category=payload.category or "system",
            payload={"kind": "demo"},
            commit=True,
        )

    def notify(
        self,
        *,
        user_id: uuid.UUID,
        title: str,
        body: str,
        category: str | None = None,
        payload: dict[str, Any] | None = None,
        commit: bool = False,
    ) -> NotificationOut:
        result = self.provider.send(
            db=self.db,
            user_id=user_id,
            title=title,
            body=body,
            category=category,
            payload=payload,
        )
        if commit:
            self.db.commit()
        if result.notification_id is None:
            raise NotFoundError("Notification was not created")
        row = self.repo.get_for_user(
            notification_id=result.notification_id,
            user_id=user_id,
        )
        if row is None:
            # flush-only path: load from identity map
            row = self.db.get(Notification, result.notification_id)
        assert row is not None
        if commit:
            self.db.refresh(row)
        return self._to_out(row)

    def _to_out(self, row: Notification) -> NotificationOut:
        return NotificationOut(
            id=row.id,
            title=row.title,
            body=row.body,
            category=row.category,
            channel=row.channel,
            is_read=row.is_read,
            read_at=row.read_at,
            payload=_parse_payload(row.payload_json),
            created_at=row.created_at,
        )


def _parse_payload(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None
