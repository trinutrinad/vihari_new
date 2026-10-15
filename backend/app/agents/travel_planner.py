"""Final planner agent — assembles specialist outputs into an itinerary."""

from __future__ import annotations

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.provider import AIProvider, get_ai_provider
from app.agents.tools import AgentTools


class TravelPlannerAgent(BaseAgent):
    name = "planner"

    def __init__(self, tools: AgentTools, provider: AIProvider | None = None) -> None:
        self.tools = tools
        self.provider = provider or get_ai_provider()

    def run(self, ctx: AgentContext) -> AgentResult:
        plan = self.plan(ctx)
        return AgentResult(
            agent=self.name,
            ok=True,
            summary=f"Assembled {ctx.days}-day itinerary",
            data={"title": plan["title"], "day_count": len(plan["days"])},
            tools_used=[],
        )

    def plan(self, ctx: AgentContext) -> dict:
        destination = ctx.workspace.get("destination")
        places = ctx.workspace.get("places") or []
        days = self._build_days(places, ctx.days)
        hotels = ctx.workspace.get("hotels") or []
        restaurants = ctx.workspace.get("restaurants") or []
        guides = ctx.workspace.get("guides") or []
        transport = ctx.workspace.get("transport") or []
        weather = ctx.workspace.get("weather")
        safety = ctx.workspace.get("safety")
        booking = ctx.workspace.get("booking")
        cost = ctx.workspace.get("cost") or {}
        budget_note = ctx.workspace.get("budget_note")

        title = self._title(ctx, destination)
        narrative = self.provider.complete(
            system="You are Bharat Yatra final trip planner.",
            user=(
                f"Plan trip from {ctx.origin_city} for {ctx.days} days. "
                f"Interests: {', '.join(ctx.interests) or 'general'}. "
                f"Budget: {ctx.budget_inr or 'flexible'}."
            ),
        )

        return {
            "title": title,
            "summary": narrative.content,
            "origin_city": ctx.origin_city,
            "destination_summary": (
                destination.get("name")
                if destination
                else (ctx.destination_hint or "Multi-city India")
            ),
            "days": days,
            "hotels": hotels,
            "restaurants": restaurants,
            "guides": guides,
            "transport": transport,
            "weather": weather,
            "safety": safety,
            "booking": booking,
            "budget_inr": ctx.budget_inr,
            "estimated_cost_inr": cost.get("estimated_total_inr"),
            "budget_note": budget_note,
            "cost_breakdown": cost,
            "provider": narrative.provider,
            "model": narrative.model,
            "prompt_tokens": narrative.prompt_tokens,
            "completion_tokens": narrative.completion_tokens,
            "tool_trace": [
                {
                    "name": item.name,
                    "ok": item.ok,
                    "message": item.message,
                    "provenance": item.provenance,
                }
                for item in ctx.tool_trace
            ],
            "agent_trace": [
                {
                    "agent": item.agent,
                    "ok": item.ok,
                    "summary": item.summary,
                    "tools_used": item.tools_used,
                }
                for item in ctx.agent_trace
            ],
            "notice": (
                "Multi-agent mock planner using seed/demo inventory. "
                "Official timings, fees, weather, and live availability are not verified."
            ),
        }

    def _build_days(self, places: list[dict], day_count: int) -> list[dict]:
        if not places:
            return [
                {
                    "day_number": day,
                    "title": f"Day {day}",
                    "notes": "Add destinations after reviewing suggestions.",
                    "places": [],
                }
                for day in range(1, day_count + 1)
            ]

        per_day = max(1, min(3, (len(places) + day_count - 1) // day_count))
        days: list[dict] = []
        cursor = 0
        slots = ["Morning", "Afternoon", "Evening"]
        for day_number in range(1, day_count + 1):
            chunk = places[cursor : cursor + per_day]
            if not chunk and places:
                chunk = [places[(day_number - 1) % len(places)]]
            cursor += per_day
            days.append(
                {
                    "day_number": day_number,
                    "title": f"Day {day_number}",
                    "notes": "Draft schedule — adjust pace to your energy and travel time.",
                    "places": [
                        {
                            "place_id": item["id"],
                            "title": item["name"],
                            "time_slot": slots[index % len(slots)],
                            "estimated_cost_inr": item.get("estimated_cost_inr"),
                            "city": item.get("city"),
                            "is_seed_data": item.get("is_seed_data", True),
                        }
                        for index, item in enumerate(chunk)
                    ],
                },
            )
        return days

    def _title(self, ctx: AgentContext, destination: dict | None) -> str:
        dest = destination.get("name") if destination else (ctx.destination_hint or "India")
        return f"{ctx.days}-day {dest} escape from {ctx.origin_city}"
