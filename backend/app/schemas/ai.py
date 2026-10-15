"""AI planner API schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.trips import TripDetailOut


class PlanTripRequest(BaseModel):
    origin_city: str = Field(min_length=2, max_length=120)
    days: int = Field(default=3, ge=1, le=14)
    budget_inr: int | None = Field(default=None, ge=0)
    interests: list[str] = Field(default_factory=list, max_length=8)
    travelers: int = Field(default=2, ge=1, le=20)
    destination_hint: str | None = Field(default=None, max_length=120)
    prompt: str | None = Field(default=None, max_length=1000)
    save: bool = True


class PlannedStopOut(BaseModel):
    place_id: str | None = None
    title: str
    time_slot: str | None = None
    estimated_cost_inr: int | None = None
    city: str | None = None
    is_seed_data: bool = True


class PlannedDayOut(BaseModel):
    day_number: int
    title: str
    notes: str | None = None
    places: list[PlannedStopOut] = Field(default_factory=list)


class PlanSuggestionOut(BaseModel):
    id: str
    name: str
    starting_price_inr: int | None = None
    cuisine_tags: str | None = None
    rating_avg: float | None = None
    languages: str | None = None
    specialization: str | None = None
    price_per_day_inr: int | None = None
    code: str | None = None
    vehicle_type: str | None = None
    base_fare_inr: int | None = None
    per_km_inr: int | None = None
    is_seed_data: bool = True


class ToolTraceOut(BaseModel):
    name: str
    ok: bool
    message: str = ""
    provenance: str = "seed_demo"


class AgentTraceOut(BaseModel):
    agent: str
    ok: bool
    summary: str
    tools_used: list[str] = Field(default_factory=list)


class AgentInfoOut(BaseModel):
    name: str
    role: str
    status: str


class WeatherDayOut(BaseModel):
    day: int
    summary: str
    temp_c_high: int
    temp_c_low: int


class WeatherOut(BaseModel):
    city: str
    days: list[WeatherDayOut] = Field(default_factory=list)
    disclaimer: str


class SafetyHintOut(BaseModel):
    kind: str
    name: str
    note: str


class SafetyOut(BaseModel):
    city: str
    tips: list[str] = Field(default_factory=list)
    nearby_hints: list[SafetyHintOut] = Field(default_factory=list)
    disclaimer: str


class BookingStatusOut(BaseModel):
    available: bool = False
    message: str
    suggested_next: list[str] = Field(default_factory=list)


class PlanTripData(BaseModel):
    title: str
    summary: str
    origin_city: str
    destination_summary: str
    days: list[PlannedDayOut]
    hotels: list[PlanSuggestionOut] = Field(default_factory=list)
    restaurants: list[PlanSuggestionOut] = Field(default_factory=list)
    guides: list[PlanSuggestionOut] = Field(default_factory=list)
    transport: list[PlanSuggestionOut] = Field(default_factory=list)
    weather: WeatherOut | None = None
    safety: SafetyOut | None = None
    booking: BookingStatusOut | None = None
    budget_inr: int | None = None
    estimated_cost_inr: int | None = None
    budget_note: str | None = None
    cost_breakdown: dict | None = None
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    tool_trace: list[ToolTraceOut] = Field(default_factory=list)
    agent_trace: list[AgentTraceOut] = Field(default_factory=list)
    notice: str
    conversation_id: UUID | None = None
    trip: TripDetailOut | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: UUID | None = None


class ChatData(BaseModel):
    conversation_id: UUID
    reply: str
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    notice: str
