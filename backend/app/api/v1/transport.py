"""Transport API routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.core.exceptions import ValidationAppError
from app.schemas.common import ApiResponse
from app.schemas.pagination import PaginatedData
from app.schemas.transport import (
    FareEstimateOut,
    TransportOptionDetailOut,
    TransportOptionSummaryOut,
)
from app.services.transport import TransportService

router = APIRouter(prefix="/transport")


@router.get("", response_model=ApiResponse[PaginatedData[TransportOptionSummaryOut]])
def list_transport_options(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
    q: str | None = None,
    vehicle_type: str | None = None,
    max_base_fare: Annotated[int | None, Query(ge=0)] = None,
) -> ApiResponse[PaginatedData[TransportOptionSummaryOut]]:
    data = TransportService(db).list_options(
        page=page,
        page_size=page_size,
        q=q,
        vehicle_type=vehicle_type,
        max_base_fare=max_base_fare,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/estimate", response_model=ApiResponse[FareEstimateOut])
def estimate_fare(
    db: DbSession,
    distance_km: Annotated[float, Query(gt=0, le=2000)],
    code: str | None = None,
    option_id: UUID | None = None,
) -> ApiResponse[FareEstimateOut]:
    if not code and option_id is None:
        raise ValidationAppError("Provide code or option_id")
    data = TransportService(db).estimate_fare(
        code=code,
        option_id=option_id,
        distance_km=distance_km,
    )
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/by-code/{code}", response_model=ApiResponse[TransportOptionDetailOut])
def get_transport_by_code(
    code: str,
    db: DbSession,
) -> ApiResponse[TransportOptionDetailOut]:
    data = TransportService(db).get_by_code(code=code)
    return ApiResponse(success=True, message="OK", data=data)


@router.get("/{option_id}", response_model=ApiResponse[TransportOptionDetailOut])
def get_transport_option(
    option_id: UUID,
    db: DbSession,
) -> ApiResponse[TransportOptionDetailOut]:
    data = TransportService(db).get_option(option_id=option_id)
    return ApiResponse(success=True, message="OK", data=data)
