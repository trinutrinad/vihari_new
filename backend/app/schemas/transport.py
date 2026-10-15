"""Transport API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class TransportOptionSummaryOut(BaseModel):
    id: UUID
    code: str
    name: str
    vehicle_type: str
    description: str | None = None
    base_fare_inr: int
    per_km_inr: int
    is_active: bool = True
    is_seed_data: bool = False
    sample_fare_10km_inr: int | None = None
    provenance: str = "seed_demo"


class TransportOptionDetailOut(TransportOptionSummaryOut):
    data_notice: str = (
        "Seed/demo transport fares are mock estimates for discovery UX. "
        "Live ride booking arrives later — real prices vary by city and provider."
    )


class FareEstimateOut(BaseModel):
    option_id: UUID
    code: str
    name: str
    vehicle_type: str
    distance_km: float
    base_fare_inr: int
    per_km_inr: int
    estimated_fare_inr: int | None = None
    currency: str = "INR"
    is_estimate: bool = True
    note: str = Field(
        default=(
            "Mock estimate only. Options without per-km rates may not have a "
            "fixed fare (e.g. bus/train/rental)."
        ),
    )
