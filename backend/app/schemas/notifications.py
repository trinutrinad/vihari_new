"""Notification API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationOut(BaseModel):
    id: UUID
    title: str
    body: str
    category: str | None = None
    channel: str
    is_read: bool
    read_at: datetime | None = None
    payload: dict[str, Any] | None = None
    created_at: datetime | None = None
    data_notice: str = (
        "In-app notifications only for now. Push/SMS/email channels arrive later."
    )


class UnreadCountOut(BaseModel):
    unread_count: int


class DemoNotificationCreate(BaseModel):
    title: str = Field(default="Welcome to Bharat Yatra", max_length=200)
    body: str = Field(
        default="Demo notification — bookings, payments, and safety alerts appear here.",
        max_length=1000,
    )
    category: str | None = Field(default="system", max_length=64)
