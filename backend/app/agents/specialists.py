"""Specialized travel agents — each owns one concern and uses tools only."""

from __future__ import annotations

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.tools import AgentTools

INTEREST_CATEGORY = {
    "nature": "waterfall",
    "waterfall": "waterfall",
    "beach": "beach",
    "temple": "temple",
    "spiritual": "temple",
    "heritage": "historical",
    "historical": "historical",
    "history": "historical",
    "mountain": "mountain",
    "adventure": "adventure",
    "wildlife": "wildlife",
    "food": None,
    "peaceful": "hidden_gem",
}

CITY_TOKENS = (
    "goa",
    "jaipur",
    "manali",
    "hyderabad",
    "varanasi",
    "udaipur",
    "rishikesh",
)


class DestinationAgent(BaseAgent):
    name = "destination"

    def __init__(self, tools: AgentTools) -> None:
        self.tools = tools

    def run(self, ctx: AgentContext) -> AgentResult:
        hint = ctx.destination_hint
        if not hint and ctx.free_text:
            lower = ctx.free_text.lower()
            for token in CITY_TOKENS:
                if token in lower:
                    hint = token
                    break
        if not hint:
            joined = " ".join(ctx.interests).lower()
            if "beach" in joined:
                hint = "goa"
            elif "temple" in joined or "spiritual" in joined:
                hint = "varanasi"
            elif "mountain" in joined or "nature" in joined or "peaceful" in joined:
                hint = "manali"
            elif "heritage" in joined or "history" in joined:
                hint = "jaipur"
            else:
                hint = ctx.origin_city or "hyderabad"

        resolve = self.tools.resolve_city(hint)
        ctx.add_tool(resolve)
        destination = resolve.data if resolve.ok else None
        city_slug = destination.get("slug") if destination else None

        collected: list[dict] = []
        tools_used = [resolve.name]
        categories = []
        for interest in ctx.interests:
            mapped = INTEREST_CATEGORY.get(interest.lower().strip())
            if mapped and mapped not in categories:
                categories.append(mapped)

        if not categories:
            result = self.tools.search_places(city_slug=city_slug, limit=12)
            ctx.add_tool(result)
            tools_used.append(result.name)
            collected.extend(result.data or [])
        else:
            for category in categories[:3]:
                result = self.tools.search_places(
                    city_slug=city_slug,
                    category=category,
                    limit=6,
                )
                ctx.add_tool(result)
                tools_used.append(result.name)
                collected.extend(result.data or [])

        if len(collected) < ctx.days:
            fallback = self.tools.featured_fallback(limit=12)
            ctx.add_tool(fallback)
            tools_used.append(fallback.name)
            collected.extend(fallback.data or [])

        seen: set[str] = set()
        places: list[dict] = []
        for place in collected:
            if place["id"] in seen:
                continue
            seen.add(place["id"])
            places.append(place)

        ctx.workspace["destination"] = destination
        ctx.workspace["places"] = places
        label = destination["name"] if destination else (hint or "India")
        return AgentResult(
            agent=self.name,
            ok=bool(places),
            summary=f"Selected {label} with {len(places)} candidate places",
            data={"destination": destination, "place_count": len(places)},
            tools_used=tools_used,
        )


class HotelAgent(BaseAgent):
    name = "hotel"

    def __init__(self, tools: AgentTools) -> None:
        self.tools = tools

    def run(self, ctx: AgentContext) -> AgentResult:
        destination = ctx.workspace.get("destination") or {}
        city_slug = destination.get("slug")
        if not city_slug:
            result = AgentResult(
                agent=self.name,
                ok=False,
                summary="No destination city for hotel search",
            )
            return result
        tool = self.tools.search_hotels(city_slug=city_slug, limit=3)
        ctx.add_tool(tool)
        hotels = tool.data if tool.ok else []
        ctx.workspace["hotels"] = hotels
        return AgentResult(
            agent=self.name,
            ok=tool.ok,
            summary=tool.message,
            data={"hotels": hotels},
            tools_used=[tool.name],
        )


class FoodAgent(BaseAgent):
    name = "food"

    def __init__(self, tools: AgentTools) -> None:
        self.tools = tools

    def run(self, ctx: AgentContext) -> AgentResult:
        destination = ctx.workspace.get("destination") or {}
        city_slug = destination.get("slug")
        if not city_slug:
            return AgentResult(
                agent=self.name,
                ok=False,
                summary="No destination city for food search",
            )
        tool = self.tools.search_restaurants(city_slug=city_slug, limit=3)
        ctx.add_tool(tool)
        restaurants = tool.data if tool.ok else []
        ctx.workspace["restaurants"] = restaurants
        return AgentResult(
            agent=self.name,
            ok=tool.ok,
            summary=tool.message,
            data={"restaurants": restaurants},
            tools_used=[tool.name],
        )


class GuideAgent(BaseAgent):
    name = "guide"

    def __init__(self, tools: AgentTools) -> None:
        self.tools = tools

    def run(self, ctx: AgentContext) -> AgentResult:
        destination = ctx.workspace.get("destination") or {}
        city_slug = destination.get("slug")
        if not city_slug:
            return AgentResult(
                agent=self.name,
                ok=False,
                summary="No destination city for guide search",
            )
        tool = self.tools.search_guides(city_slug=city_slug, limit=3)
        ctx.add_tool(tool)
        guides = tool.data if tool.ok else []
        ctx.workspace["guides"] = guides
        return AgentResult(
            agent=self.name,
            ok=tool.ok,
            summary=tool.message,
            data={"guides": guides},
            tools_used=[tool.name],
        )


class TransportAgent(BaseAgent):
    name = "transport"

    def __init__(self, tools: AgentTools) -> None:
        self.tools = tools

    def run(self, ctx: AgentContext) -> AgentResult:
        tool = self.tools.search_transport(limit=6)
        ctx.add_tool(tool)
        options = tool.data if tool.ok else []
        distance = None
        places = ctx.workspace.get("places") or []
        coords = [
            (p.get("latitude"), p.get("longitude"))
            for p in places
            if p.get("latitude") is not None and p.get("longitude") is not None
        ]
        if len(coords) >= 2:
            dist_tool = self.tools.calculate_distance(
                lat1=float(coords[0][0]),
                lng1=float(coords[0][1]),
                lat2=float(coords[1][0]),
                lng2=float(coords[1][1]),
            )
            ctx.add_tool(dist_tool)
            distance = dist_tool.data if dist_tool.ok else None
            tools = [tool.name, dist_tool.name]
        else:
            tools = [tool.name]
        ctx.workspace["transport"] = options
        ctx.workspace["sample_distance"] = distance
        return AgentResult(
            agent=self.name,
            ok=tool.ok,
            summary=tool.message,
            data={"transport": options, "sample_distance": distance},
            tools_used=tools,
        )


class WeatherAgent(BaseAgent):
    name = "weather"

    def __init__(self, tools: AgentTools) -> None:
        self.tools = tools

    def run(self, ctx: AgentContext) -> AgentResult:
        destination = ctx.workspace.get("destination") or {}
        city_name = destination.get("name") or ctx.destination_hint or ctx.origin_city
        tool = self.tools.get_weather(city_name=city_name, days=ctx.days)
        ctx.add_tool(tool)
        weather = tool.data if tool.ok else None
        ctx.workspace["weather"] = weather
        return AgentResult(
            agent=self.name,
            ok=tool.ok,
            summary=tool.message,
            data={"weather": weather},
            tools_used=[tool.name],
        )


class SafetyAgent(BaseAgent):
    name = "safety"

    def __init__(self, tools: AgentTools) -> None:
        self.tools = tools

    def run(self, ctx: AgentContext) -> AgentResult:
        destination = ctx.workspace.get("destination") or {}
        city_name = destination.get("name") or ctx.origin_city
        tool = self.tools.find_nearby_safety(city_name=city_name)
        ctx.add_tool(tool)
        safety = tool.data if tool.ok else None
        ctx.workspace["safety"] = safety
        return AgentResult(
            agent=self.name,
            ok=tool.ok,
            summary=tool.message,
            data={"safety": safety},
            tools_used=[tool.name],
        )


class BudgetAgent(BaseAgent):
    name = "budget"

    def __init__(self, tools: AgentTools) -> None:
        self.tools = tools

    def run(self, ctx: AgentContext) -> AgentResult:
        places = ctx.workspace.get("places") or []
        hotels = ctx.workspace.get("hotels") or []
        guides = ctx.workspace.get("guides") or []
        place_costs = [int(item.get("estimated_cost_inr") or 0) for item in places[: ctx.days * 2]]
        hotel_rate = hotels[0].get("starting_price_inr") if hotels else 2500
        guide_day = guides[0].get("price_per_day_inr") if guides else 0
        transport_buffer = 1500
        sample = ctx.workspace.get("sample_distance") or {}
        if sample.get("distance_km"):
            transport_buffer = max(1500, int(float(sample["distance_km"]) * 20))

        tool = self.tools.calculate_trip_cost(
            place_costs=place_costs,
            hotel_per_night=int(hotel_rate or 2500),
            days=ctx.days,
            transport_buffer=transport_buffer,
        )
        ctx.add_tool(tool)
        cost = dict(tool.data or {})
        if guide_day:
            cost["guide_buffer_inr"] = int(guide_day) * ctx.days
            cost["estimated_total_inr"] = int(cost.get("estimated_total_inr") or 0) + cost[
                "guide_buffer_inr"
            ]
        budget_note = None
        estimated = cost.get("estimated_total_inr")
        if ctx.budget_inr and estimated and estimated > ctx.budget_inr:
            budget_note = (
                f"Estimated ₹{estimated:,} exceeds your ₹{ctx.budget_inr:,} budget. "
                "Consider fewer paid activities or shorter stays."
            )
        ctx.workspace["cost"] = cost
        ctx.workspace["budget_note"] = budget_note
        return AgentResult(
            agent=self.name,
            ok=tool.ok,
            summary=tool.message,
            data={"cost": cost, "budget_note": budget_note},
            tools_used=[tool.name],
        )


class BookingAgent(BaseAgent):
    """Mock booking status for the planner — live create/cancel via /bookings."""

    name = "booking"

    def run(self, ctx: AgentContext) -> AgentResult:
        status = {
            "available": True,
            "message": (
                "Mock bookings are available for hotels, guides, activities, "
                "transport, and restaurants via /api/v1/bookings. "
                "Mock payments via /api/v1/payments."
            ),
            "suggested_next": ["hotels", "guides", "transport", "activities"],
        }
        ctx.workspace["booking"] = status
        return AgentResult(
            agent=self.name,
            ok=True,
            summary="Mock bookings and payments available",
            data=status,
            tools_used=[],
        )
