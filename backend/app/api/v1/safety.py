"""Safety API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.safety import (
    EmergencyContactCreate,
    EmergencyContactOut,
    EmergencyContactUpdate,
    EmergencyNumberOut,
    SafetyTipsOut,
    SosOut,
    SosRequest,
)
from app.services.safety import SafetyService

router = APIRouter(prefix="/safety")


@router.get("/tips", response_model=ApiResponse[SafetyTipsOut])
def get_safety_tips(
    db: DbSession,
    city: str | None = None,
) -> ApiResponse[SafetyTipsOut]:
    data = SafetyService(db).get_tips(city=city)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/emergency-numbers", response_model=ApiResponse[list[EmergencyNumberOut]])
def list_emergency_numbers(db: DbSession) -> ApiResponse[list[EmergencyNumberOut]]:
    data = SafetyService(db).list_emergency_numbers()
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/contacts", response_model=ApiResponse[list[EmergencyContactOut]])
def list_contacts(
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[list[EmergencyContactOut]]:
    data = SafetyService(db).list_contacts(user_id=current_user.id)
    return ApiResponse(success=True, message="OK", data=data)


@router.post(
    "/contacts",
    response_model=ApiResponse[EmergencyContactOut],
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    payload: EmergencyContactCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[EmergencyContactOut]:
    data = SafetyService(db).create_contact(user_id=current_user.id, payload=payload)
    return ApiResponse(success=True, message="Contact saved", data=data)


@router.patch("/contacts/{contact_id}", response_model=ApiResponse[EmergencyContactOut])
def update_contact(
    contact_id: UUID,
    payload: EmergencyContactUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[EmergencyContactOut]:
    data = SafetyService(db).update_contact(
        contact_id=contact_id,
        user_id=current_user.id,
        payload=payload,
    )
    return ApiResponse(success=True, message="Contact updated", data=data)


@router.delete("/contacts/{contact_id}", response_model=ApiResponse[dict])
def delete_contact(
    contact_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[dict]:
    SafetyService(db).delete_contact(contact_id=contact_id, user_id=current_user.id)
    return ApiResponse(success=True, message="Contact deleted", data={"deleted": True})


@router.post(
    "/sos",
    response_model=ApiResponse[SosOut],
    status_code=status.HTTP_201_CREATED,
)
def create_sos(
    payload: SosRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ApiResponse[SosOut]:
    data = SafetyService(db).create_sos(user_id=current_user.id, payload=payload)
    return ApiResponse(success=True, message="Mock SOS recorded", data=data)
