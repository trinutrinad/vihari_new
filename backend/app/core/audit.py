"""Lightweight privileged-action audit logging."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("app.audit")


def audit_event(action: str, *, actor: str | None = None, **details: Any) -> None:
    payload = " ".join(f"{key}={value}" for key, value in details.items())
    logger.info("audit action=%s actor=%s %s", action, actor or "-", payload)
