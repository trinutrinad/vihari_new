"""AI trip planner service — orchestrator + conversation persistence."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.agents.base import AgentContext
from app.agents.orchestrator import TravelOrchestrator
from app.core.exceptions import NotFoundError, ValidationAppError
from app.models import AIConversation, AIMessage
from app.models.enums import TripStatus
from app.schemas.ai import (
    AgentInfoOut,
    AgentTraceOut,
    BookingStatusOut,
    ChatData,
    ChatRequest,
    PlannedDayOut,
    PlannedStopOut,
    PlanSuggestionOut,
    PlanTripData,
    PlanTripRequest,
    SafetyOut,
    ToolTraceOut,
    WeatherOut,
)
from app.schemas.trips import TripCreate, TripDayCreate, TripPlaceCreate
from app.services.trips import TripService


class AIPlannerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.orchestrator = TravelOrchestrator(db)
        self.trips = TripService(db)

    def list_agents(self) -> list[AgentInfoOut]:
        return [AgentInfoOut(**item) for item in self.orchestrator.list_agents()]

    def plan_trip(
        self,
        *,
        user_id: uuid.UUID | None,
        payload: PlanTripRequest,
    ) -> PlanTripData:
        interests = [item.strip() for item in payload.interests if item.strip()]
        ctx = AgentContext(
            origin_city=payload.origin_city.strip(),
            days=payload.days,
            budget_inr=payload.budget_inr,
            interests=interests,
            travelers=payload.travelers,
            destination_hint=(payload.destination_hint or "").strip() or None,
            free_text=(payload.prompt or "").strip() or None,
        )
        raw = self.orchestrator.plan_trip(ctx)
        prompt_text = payload.prompt or (
            f"{payload.days} days from {payload.origin_city}"
            f" budget={payload.budget_inr} interests={','.join(interests)}"
        )

        conversation = AIConversation(
            user_id=user_id,
            title=raw["title"][:200],
            purpose="plan_trip",
        )
        self.db.add(conversation)
        self.db.flush()
        self.db.add(
            AIMessage(
                conversation_id=conversation.id,
                role="user",
                content=prompt_text,
                model=None,
            ),
        )
        self.db.add(
            AIMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=raw["summary"],
                model=raw["model"],
                prompt_tokens=raw["prompt_tokens"],
                completion_tokens=raw["completion_tokens"],
            ),
        )
        self.db.commit()
        self.db.refresh(conversation)

        trip = None
        if payload.save:
            if user_id is None:
                raise ValidationAppError("Sign in required to save an AI trip")
            trip = self.trips.create_trip(
                user_id=user_id,
                payload=TripCreate(
                    title=raw["title"],
                    summary=raw["summary"],
                    origin_city=raw["origin_city"],
                    destination_summary=raw["destination_summary"],
                    budget_inr=payload.budget_inr,
                    status=TripStatus.DRAFT,
                    is_ai_generated=True,
                    ai_prompt=prompt_text,
                    days=[
                        TripDayCreate(
                            day_number=day["day_number"],
                            title=day["title"],
                            notes=day.get("notes"),
                            places=[
                                TripPlaceCreate(
                                    place_id=uuid.UUID(stop["place_id"])
                                    if stop.get("place_id")
                                    else None,
                                    custom_title=None if stop.get("place_id") else stop["title"],
                                    time_slot=stop.get("time_slot"),
                                    estimated_cost_inr=stop.get("estimated_cost_inr"),
                                    sort_order=index,
                                )
                                for index, stop in enumerate(day.get("places") or [])
                            ],
                        )
                        for day in raw["days"]
                    ],
                ),
            )

        return PlanTripData(
            title=raw["title"],
            summary=raw["summary"],
            origin_city=raw["origin_city"],
            destination_summary=raw["destination_summary"],
            days=[
                PlannedDayOut(
                    day_number=day["day_number"],
                    title=day["title"],
                    notes=day.get("notes"),
                    places=[
                        PlannedStopOut(
                            place_id=stop.get("place_id"),
                            title=stop["title"],
                            time_slot=stop.get("time_slot"),
                            estimated_cost_inr=stop.get("estimated_cost_inr"),
                            city=stop.get("city"),
                            is_seed_data=bool(stop.get("is_seed_data", True)),
                        )
                        for stop in day.get("places") or []
                    ],
                )
                for day in raw["days"]
            ],
            hotels=[
                PlanSuggestionOut(
                    id=item["id"],
                    name=item["name"],
                    starting_price_inr=item.get("starting_price_inr"),
                    rating_avg=item.get("rating_avg"),
                    is_seed_data=bool(item.get("is_seed_data", True)),
                )
                for item in raw.get("hotels") or []
            ],
            restaurants=[
                PlanSuggestionOut(
                    id=item["id"],
                    name=item["name"],
                    cuisine_tags=item.get("cuisine_tags"),
                    rating_avg=item.get("rating_avg"),
                    is_seed_data=bool(item.get("is_seed_data", True)),
                )
                for item in raw.get("restaurants") or []
            ],
            guides=[
                PlanSuggestionOut(
                    id=item["id"],
                    name=item["name"],
                    languages=item.get("languages"),
                    specialization=item.get("specialization"),
                    price_per_day_inr=item.get("price_per_day_inr"),
                    rating_avg=item.get("rating_avg"),
                    is_seed_data=bool(item.get("is_seed_data", True)),
                )
                for item in raw.get("guides") or []
            ],
            transport=[
                PlanSuggestionOut(
                    id=item["id"],
                    name=item["name"],
                    code=item.get("code"),
                    vehicle_type=item.get("vehicle_type"),
                    base_fare_inr=item.get("base_fare_inr"),
                    per_km_inr=item.get("per_km_inr"),
                    is_seed_data=bool(item.get("is_seed_data", True)),
                )
                for item in raw.get("transport") or []
            ],
            weather=WeatherOut(**raw["weather"]) if raw.get("weather") else None,
            safety=SafetyOut(**raw["safety"]) if raw.get("safety") else None,
            booking=BookingStatusOut(**raw["booking"]) if raw.get("booking") else None,
            budget_inr=raw.get("budget_inr"),
            estimated_cost_inr=raw.get("estimated_cost_inr"),
            budget_note=raw.get("budget_note"),
            cost_breakdown=raw.get("cost_breakdown"),
            provider=raw["provider"],
            model=raw["model"],
            prompt_tokens=raw["prompt_tokens"],
            completion_tokens=raw["completion_tokens"],
            tool_trace=[ToolTraceOut(**item) for item in raw.get("tool_trace") or []],
            agent_trace=[AgentTraceOut(**item) for item in raw.get("agent_trace") or []],
            notice=raw["notice"],
            conversation_id=conversation.id,
            trip=trip,
        )

    def chat(self, *, user_id: uuid.UUID | None, payload: ChatRequest) -> ChatData:
        conversation: AIConversation | None = None
        if payload.conversation_id is not None:
            conversation = self.db.get(AIConversation, payload.conversation_id)
            if conversation is None:
                raise NotFoundError("Conversation not found")
            if (
                conversation.user_id is not None
                and user_id is not None
                and conversation.user_id != user_id
            ):
                raise NotFoundError("Conversation not found")
        else:
            conversation = AIConversation(
                user_id=user_id,
                title=payload.message[:80],
                purpose="chat",
            )
            self.db.add(conversation)
            self.db.flush()

        result = self.orchestrator.chat(message=payload.message.strip())
        self.db.add(
            AIMessage(
                conversation_id=conversation.id,
                role="user",
                content=payload.message.strip(),
            ),
        )
        self.db.add(
            AIMessage(
                conversation_id=conversation.id,
                role="assistant",
                content=result["reply"],
                model=result["model"],
                prompt_tokens=result["prompt_tokens"],
                completion_tokens=result["completion_tokens"],
            ),
        )
        self.db.commit()
        self.db.refresh(conversation)

        return ChatData(
            conversation_id=conversation.id,
            reply=result["reply"],
            provider=result["provider"],
            model=result["model"],
            prompt_tokens=result["prompt_tokens"],
            completion_tokens=result["completion_tokens"],
            notice=result["notice"],
        )
