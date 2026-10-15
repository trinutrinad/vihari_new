"""Fire-and-forget in-app notification helper."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def notify_user(
    db: Session,
    *,
    user_id: uuid.UUID,
    title: str,
    body: str,
    category: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    try:
        from app.services.notifications import NotificationService

        NotificationService(db).notify(
            user_id=user_id,
            title=title,
            body=body,
            category=category,
            payload=payload,
            commit=True,
        )
    except Exception:
        logger.exception("Failed to create in-app notification for user=%s", user_id)
