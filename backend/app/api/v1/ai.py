"""AI chat and trip planner routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, get_current_user_optional
from app.models import User
from app.schemas.ai import (
    AgentInfoOut,
    ChatData,
    ChatRequest,
    PlanTripData,
    PlanTripRequest,
)
from app.schemas.common import ApiResponse
from app.services.ai_planner import AIPlannerService

router = APIRouter(prefix="/ai")


@router.get("/agents", response_model=ApiResponse[list[AgentInfoOut]])
def list_agents(db: DbSession) -> ApiResponse[list[AgentInfoOut]]:
    data = AIPlannerService(db).list_agents()
    return ApiResponse(success=True, message="OK", data=data)


@router.post("/plan-trip", response_model=ApiResponse[PlanTripData])
def plan_trip(
    payload: PlanTripRequest,
    db: DbSession,
    current_user: Annotated[User | None, Depends(get_current_user_optional)] = None,
) -> ApiResponse[PlanTripData]:
    # Allow preview without auth when save=false; saving requires login
    save = payload.save
    if save and current_user is None:
        payload = payload.model_copy(update={"save": False})
        data = AIPlannerService(db).plan_trip(user_id=None, payload=payload)
        data_dump = data.model_dump()
        data_dump["notice"] = (
            data.notice
            + " Sign in and set save=true to store this itinerary as a trip."
        )
        return ApiResponse(
            success=True,
            message="Plan generated (not saved — sign in to save)",
            data=PlanTripData(**data_dump),
        )

    data = AIPlannerService(db).plan_trip(
        user_id=current_user.id if current_user else None,
        payload=payload.model_copy(update={"save": save and current_user is not None}),
    )
    return ApiResponse(success=True, message="Plan generated", data=data)


@router.post("/chat", response_model=ApiResponse[ChatData])
def ai_chat(
    payload: ChatRequest,
    db: DbSession,
    current_user: Annotated[User | None, Depends(get_current_user_optional)] = None,
) -> ApiResponse[ChatData]:
    data = AIPlannerService(db).chat(
        user_id=current_user.id if current_user else None,
        payload=payload,
    )
    return ApiResponse(success=True, message="OK", data=data)
