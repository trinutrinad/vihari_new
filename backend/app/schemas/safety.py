"""Safety API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class SafetyHintOut(BaseModel):
    kind: str
    name: str
    note: str


class EmergencyNumberOut(BaseModel):
    label: str
    number: str
    notes: str | None = None


class SafetyTipsOut(BaseModel):
    city: str | None = None
    tips: list[str] = Field(default_factory=list)
    nearby_hints: list[SafetyHintOut] = Field(default_factory=list)
    emergency_numbers: list[EmergencyNumberOut] = Field(default_factory=list)
    disclaimer: str = (
        "General travel-safety guidance only. Nearby hints are unverified placeholders — "
        "confirm on a live map and official sources. In an emergency dial 112."
    )


class EmergencyContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=5, max_length=20)
    relationship_label: str | None = Field(default=None, max_length=80)
    is_primary: bool = False


class EmergencyContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    phone: str | None = Field(default=None, min_length=5, max_length=20)
    relationship_label: str | None = Field(default=None, max_length=80)
    is_primary: bool | None = None


class EmergencyContactOut(BaseModel):
    id: UUID
    name: str
    phone: str
    relationship_label: str | None = None
    is_primary: bool = False


class SosRequest(BaseModel):
    message: str | None = Field(default=None, max_length=500)
    latitude: float | None = None
    longitude: float | None = None
    city: str | None = Field(default=None, max_length=120)


class SosOut(BaseModel):
    ticket_id: UUID
    ticket_number: str
    status: str
    message: str
    is_mock: bool = True
    data_notice: str = (
        "Mock SOS creates a support ticket for demo UX only. "
        "It does not contact emergency services — dial 112 in a real emergency."
    )
