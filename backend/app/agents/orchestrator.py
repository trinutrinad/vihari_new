"""Travel orchestrator — multi-agent fan-out then final planner assembly."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.agents.base import AgentContext, BaseAgent
from app.agents.provider import get_ai_provider
from app.agents.specialists import (
    BookingAgent,
    BudgetAgent,
    DestinationAgent,
    FoodAgent,
    GuideAgent,
    HotelAgent,
    SafetyAgent,
    TransportAgent,
    WeatherAgent,
)
from app.agents.tools import AgentTools
from app.agents.travel_planner import TravelPlannerAgent

AGENT_CATALOG = [
    {
        "name": "destination",
        "role": "Pick destination and candidate places",
        "status": "live",
    },
    {"name": "hotel", "role": "Suggest demo stays", "status": "live"},
    {"name": "food", "role": "Suggest demo restaurants", "status": "live"},
    {"name": "guide", "role": "Suggest local guides", "status": "live"},
    {"name": "transport", "role": "List transport options + distance", "status": "live"},
    {"name": "weather", "role": "Mock weather outlook", "status": "live"},
    {"name": "safety", "role": "General safety guidance", "status": "live"},
    {"name": "budget", "role": "Estimate trip cost", "status": "live"},
    {"name": "booking", "role": "Mock bookings ledger", "status": "live"},
    {"name": "planner", "role": "Assemble final itinerary", "status": "live"},
]


class TravelOrchestrator:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.tools = AgentTools(db)
        self.provider = get_ai_provider()
        self.planner = TravelPlannerAgent(self.tools, self.provider)
        self.specialists: list[BaseAgent] = [
            DestinationAgent(self.tools),
            HotelAgent(self.tools),
            FoodAgent(self.tools),
            GuideAgent(self.tools),
            TransportAgent(self.tools),
            WeatherAgent(self.tools),
            SafetyAgent(self.tools),
            BudgetAgent(self.tools),
            BookingAgent(),
        ]

    def list_agents(self) -> list[dict]:
        return list(AGENT_CATALOG)

    def plan_trip(self, ctx: AgentContext) -> dict:
        for agent in self.specialists:
            ctx.add_agent(agent.run(ctx))
        plan = self.planner.plan(ctx)
        plan["agent_trace"] = [
            *plan.get("agent_trace", []),
            {
                "agent": "planner",
                "ok": True,
                "summary": f"Assembled {ctx.days}-day itinerary",
                "tools_used": [],
            },
        ]
        return plan

    def chat(self, *, message: str) -> dict:
        completion = self.provider.complete(
            system=(
                "You are a helpful Indian travel assistant for Bharat Yatra. "
                "Specialized agents handle destinations, hotels, food, guides, "
                "transport, weather, safety, and budget."
            ),
            user=message,
        )
        return {
            "reply": completion.content,
            "provider": completion.provider,
            "model": completion.model,
            "prompt_tokens": completion.prompt_tokens,
            "completion_tokens": completion.completion_tokens,
            "notice": "Mock AI response — not a live LLM.",
            "agents": [item["name"] for item in AGENT_CATALOG if item["status"] == "live"],
        }
