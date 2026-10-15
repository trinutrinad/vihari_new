"""Notifications API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.notifications import (
    DemoNotificationCreate,
    NotificationOut,
    UnreadCountOut,
)
from app.services.notifications import NotificationService

router = APIRouter(prefix="/notifications")


@router.get("", response_model=ApiResponse[list[NotificationOut]])
def list_notifications(
    db: DbSession,
    current_user: CurrentUser,
    unread_only: bool = False,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ApiResponse[list[NotificationOut]]:
    data = NotificationService(db).list_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/unread-count", response_model=ApiResponse[UnreadCountOut])
def unread_count(
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[UnreadCountOut]:
    data = NotificationService(db).unread_count(user_id=current_user.id)
    return ApiResponse(success=True, message="OK", data=data)


@router.post(
    "/demo",
    response_model=ApiResponse[NotificationOut],
    status_code=status.HTTP_201_CREATED,
)
def create_demo_notification(
    payload: DemoNotificationCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[NotificationOut]:
    data = NotificationService(db).create_demo(
        user_id=current_user.id,
        payload=payload,
    )
    return ApiResponse(success=True, message="Demo notification created", data=data)


@router.post("/read-all", response_model=ApiResponse[UnreadCountOut])
def mark_all_read(
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[UnreadCountOut]:
    data = NotificationService(db).mark_all_read(user_id=current_user.id)
    return ApiResponse(success=True, message="All marked read", data=data)


@router.get("/{notification_id}", response_model=ApiResponse[NotificationOut])
def get_notification(
    notification_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[NotificationOut]:
    data = NotificationService(db).get_notification(
        notification_id=notification_id,
        user_id=current_user.id,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.post("/{notification_id}/read", response_model=ApiResponse[NotificationOut])
def mark_read(
    notification_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[NotificationOut]:
    data = NotificationService(db).mark_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )
    return ApiResponse(success=True, message="Marked read", data=data)
