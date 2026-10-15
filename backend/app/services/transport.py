"""Transport business logic."""

from __future__ import annotations

import math
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import TransportOption
from app.repositories.transport import TransportRepository
from app.schemas.pagination import PageMeta, PaginatedData
from app.schemas.transport import (
    FareEstimateOut,
    TransportOptionDetailOut,
    TransportOptionSummaryOut,
)


class TransportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = TransportRepository(db)

    def list_options(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        vehicle_type: str | None = None,
        max_base_fare: int | None = None,
    ) -> PaginatedData[TransportOptionSummaryOut]:
        rows, total = self.repo.list_options(
            page=page,
            page_size=page_size,
            q=q,
            vehicle_type=vehicle_type,
            max_base_fare=max_base_fare,
        )
        items = [self._to_summary(row) for row in rows]
        total_pages = math.ceil(total / page_size) if page_size else 0
        return PaginatedData(
            items=items,
            meta=PageMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    def get_option(self, *, option_id: uuid.UUID) -> TransportOptionDetailOut:
        option = self.repo.get_by_id(option_id)
        if option is None:
            raise NotFoundError("Transport option not found")
        return TransportOptionDetailOut(**self._to_summary(option).model_dump())

    def get_by_code(self, *, code: str) -> TransportOptionDetailOut:
        option = self.repo.get_by_code(code)
        if option is None:
            raise NotFoundError("Transport option not found")
        return TransportOptionDetailOut(**self._to_summary(option).model_dump())

    def estimate_fare(
        self,
        *,
        code: str | None = None,
        option_id: uuid.UUID | None = None,
        distance_km: float,
    ) -> FareEstimateOut:
        option: TransportOption | None = None
        if option_id is not None:
            option = self.repo.get_by_id(option_id)
        elif code:
            option = self.repo.get_by_code(code)
        if option is None:
            raise NotFoundError("Transport option not found")

        estimated = _estimate_fare(option, distance_km)
        return FareEstimateOut(
            option_id=option.id,
            code=option.code,
            name=option.name,
            vehicle_type=option.vehicle_type,
            distance_km=round(distance_km, 2),
            base_fare_inr=option.base_fare_inr,
            per_km_inr=option.per_km_inr,
            estimated_fare_inr=estimated,
        )

    def _to_summary(self, option: TransportOption) -> TransportOptionSummaryOut:
        sample = _estimate_fare(option, 10.0)
        return TransportOptionSummaryOut(
            id=option.id,
            code=option.code,
            name=option.name,
            vehicle_type=option.vehicle_type,
            description=option.description,
            base_fare_inr=option.base_fare_inr,
            per_km_inr=option.per_km_inr,
            is_active=option.is_active,
            is_seed_data=option.is_seed_data,
            sample_fare_10km_inr=sample,
            provenance="seed_demo" if option.is_seed_data else "user_generated",
        )


def _estimate_fare(option: TransportOption, distance_km: float) -> int | None:
    if option.base_fare_inr <= 0 and option.per_km_inr <= 0:
        return None
    distance = max(0.0, float(distance_km))
    return int(round(option.base_fare_inr + option.per_km_inr * distance))
