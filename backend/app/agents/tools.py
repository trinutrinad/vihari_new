"""Controlled tools for AI agents — wrap repositories/services only."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.agents.base import ToolResult
from app.models import City, Guide, Hotel, Restaurant, TransportOption
from app.repositories.places import PlaceRepository, haversine_km


class AgentTools:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.places = PlaceRepository(db)

    def search_places(
        self,
        *,
        q: str | None = None,
        city_slug: str | None = None,
        category: str | None = None,
        limit: int = 12,
    ) -> ToolResult:
        rows, _ = self.places.list_places(
            page=1,
            page_size=limit,
            category=category,
            city_slug=city_slug,
            q=q,
            featured=None,
            hidden_gem=None,
            family_friendly=None,
        )
        data = [
            {
                "id": str(place.id),
                "name": place.name,
                "slug": place.slug,
                "city": place.city.name if place.city else None,
                "city_slug": place.city.slug if place.city else None,
                "category": place.category.slug if place.category else None,
                "estimated_cost_inr": place.estimated_cost_inr,
                "rating_avg": float(place.rating_avg),
                "is_seed_data": place.is_seed_data,
                "latitude": float(place.latitude) if place.latitude is not None else None,
                "longitude": float(place.longitude) if place.longitude is not None else None,
            }
            for place in rows
        ]
        return ToolResult(
            name="search_places",
            ok=True,
            data=data,
            message=f"Found {len(data)} places",
            provenance="seed_demo",
        )

    def search_hotels(self, *, city_slug: str, limit: int = 3) -> ToolResult:
        city = self.db.scalar(select(City).where(City.slug == city_slug.lower()))
        if city is None:
            return ToolResult(
                name="search_hotels",
                ok=False,
                message="City not found",
                provenance="seed_demo",
            )
        rows = list(
            self.db.scalars(
                select(Hotel)
                .where(Hotel.city_id == city.id, Hotel.is_deleted.is_(False))
                .order_by(Hotel.rating_avg.desc())
                .limit(limit),
            ).all(),
        )
        data = [
            {
                "id": str(hotel.id),
                "name": hotel.name,
                "starting_price_inr": hotel.starting_price_inr,
                "rating_avg": float(hotel.rating_avg),
                "is_seed_data": hotel.is_seed_data,
            }
            for hotel in rows
        ]
        return ToolResult(
            name="search_hotels",
            ok=True,
            data=data,
            message=f"Found {len(data)} hotels",
            provenance="seed_demo",
        )

    def search_restaurants(self, *, city_slug: str, limit: int = 3) -> ToolResult:
        city = self.db.scalar(select(City).where(City.slug == city_slug.lower()))
        if city is None:
            return ToolResult(
                name="search_restaurants",
                ok=False,
                message="City not found",
                provenance="seed_demo",
            )
        rows = list(
            self.db.scalars(
                select(Restaurant)
                .where(Restaurant.city_id == city.id, Restaurant.is_deleted.is_(False))
                .order_by(Restaurant.rating_avg.desc())
                .limit(limit),
            ).all(),
        )
        data = [
            {
                "id": str(row.id),
                "name": row.name,
                "cuisine_tags": row.cuisine_tags,
                "rating_avg": float(row.rating_avg),
                "is_seed_data": row.is_seed_data,
            }
            for row in rows
        ]
        return ToolResult(
            name="search_restaurants",
            ok=True,
            data=data,
            message=f"Found {len(data)} restaurants",
            provenance="seed_demo",
        )

    def resolve_city(self, hint: str | None) -> ToolResult:
        if not hint:
            return ToolResult(name="resolve_city", ok=False, message="No city hint")
        like = f"%{hint.strip()}%"
        city = self.db.scalar(
            select(City)
            .options(selectinload(City.state))
            .where(or_(City.name.ilike(like), City.slug.ilike(like)))
            .order_by(City.is_popular.desc())
            .limit(1),
        )
        if city is None:
            return ToolResult(name="resolve_city", ok=False, message="City not found")
        return ToolResult(
            name="resolve_city",
            ok=True,
            data={
                "id": str(city.id),
                "name": city.name,
                "slug": city.slug,
                "state_code": city.state.code if city.state else None,
            },
            provenance="seed_demo",
        )

    def calculate_trip_cost(
        self,
        *,
        place_costs: list[int],
        hotel_per_night: int | None,
        days: int,
        meal_buffer_per_day: int = 800,
        transport_buffer: int = 1500,
    ) -> ToolResult:
        sights = sum(place_costs)
        stay = (hotel_per_night or 0) * max(days - 1, 0)
        food = meal_buffer_per_day * days
        total = sights + stay + food + transport_buffer
        return ToolResult(
            name="calculate_trip_cost",
            ok=True,
            data={
                "sights_inr": sights,
                "stay_inr": stay,
                "food_buffer_inr": food,
                "transport_buffer_inr": transport_buffer,
                "estimated_total_inr": total,
            },
            message="Budget estimate from seed prices + buffers",
            provenance="estimated",
        )

    def featured_fallback(self, *, limit: int = 12) -> ToolResult:
        rows, _ = self.places.list_places(
            page=1,
            page_size=limit,
            featured=True,
            category=None,
            city_slug=None,
            q=None,
            hidden_gem=None,
            family_friendly=None,
        )
        if not rows:
            rows, _ = self.places.list_places(
                page=1,
                page_size=limit,
                category=None,
                city_slug=None,
                featured=None,
                hidden_gem=None,
                q=None,
                family_friendly=None,
            )
        data = [
            {
                "id": str(place.id),
                "name": place.name,
                "slug": place.slug,
                "city": place.city.name if place.city else None,
                "city_slug": place.city.slug if place.city else None,
                "category": place.category.slug if place.category else None,
                "estimated_cost_inr": place.estimated_cost_inr,
                "rating_avg": float(place.rating_avg),
                "is_seed_data": place.is_seed_data,
            }
            for place in rows
        ]
        return ToolResult(
            name="search_places",
            ok=True,
            data=data,
            message="Fallback featured/popular places",
            provenance="seed_demo",
        )

    def search_guides(self, *, city_slug: str, limit: int = 3) -> ToolResult:
        city = self.db.scalar(select(City).where(City.slug == city_slug.lower()))
        if city is None:
            return ToolResult(
                name="search_guides",
                ok=False,
                message="City not found",
                provenance="seed_demo",
            )
        rows = list(
            self.db.scalars(
                select(Guide)
                .where(Guide.city_id == city.id, Guide.is_active.is_(True))
                .order_by(Guide.rating_avg.desc())
                .limit(limit),
            ).all(),
        )
        data = [
            {
                "id": str(guide.id),
                "name": guide.display_name,
                "languages": guide.languages,
                "specialization": guide.specialization,
                "price_per_day_inr": guide.price_per_day_inr,
                "rating_avg": float(guide.rating_avg),
                "is_seed_data": guide.is_seed_data,
            }
            for guide in rows
        ]
        return ToolResult(
            name="search_guides",
            ok=True,
            data=data,
            message=f"Found {len(data)} guides",
            provenance="seed_demo",
        )

    def search_transport(self, *, limit: int = 6) -> ToolResult:
        rows = list(
            self.db.scalars(
                select(TransportOption)
                .where(TransportOption.is_active.is_(True))
                .order_by(TransportOption.base_fare_inr.asc())
                .limit(limit),
            ).all(),
        )
        data = [
            {
                "id": str(option.id),
                "code": option.code,
                "name": option.name,
                "vehicle_type": option.vehicle_type,
                "base_fare_inr": option.base_fare_inr,
                "per_km_inr": option.per_km_inr,
                "is_seed_data": option.is_seed_data,
            }
            for option in rows
        ]
        return ToolResult(
            name="search_transport",
            ok=True,
            data=data,
            message=f"Found {len(data)} transport options",
            provenance="seed_demo",
        )

    def calculate_distance(
        self,
        *,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float,
    ) -> ToolResult:
        km = haversine_km(lat1, lng1, lat2, lng2)
        return ToolResult(
            name="calculate_distance",
            ok=True,
            data={"distance_km": round(km, 1)},
            message=f"Approx {km:.1f} km",
            provenance="estimated",
        )

    def get_weather(self, *, city_name: str, days: int) -> ToolResult:
        # Deterministic mock — not live weather. Never claim official forecast.
        outlook = [
            {"day": 1, "summary": "Partly cloudy", "temp_c_high": 31, "temp_c_low": 23},
            {"day": 2, "summary": "Warm and clear", "temp_c_high": 33, "temp_c_low": 24},
            {"day": 3, "summary": "Chance of light showers", "temp_c_high": 30, "temp_c_low": 22},
        ]
        while len(outlook) < days:
            template = outlook[len(outlook) % 3]
            outlook.append(
                {
                    "day": len(outlook) + 1,
                    "summary": template["summary"],
                    "temp_c_high": template["temp_c_high"],
                    "temp_c_low": template["temp_c_low"],
                },
            )
        data = {
            "city": city_name,
            "days": outlook[:days],
            "disclaimer": (
                f"Mock weather for {city_name}. Not an official forecast — "
                "verify with a live weather service before travel."
            ),
        }
        return ToolResult(
            name="get_weather",
            ok=True,
            data=data,
            message="Mock weather outlook generated",
            provenance="unverified",
        )

    def find_nearby_safety(self, *, city_name: str) -> ToolResult:
        from app.services.safety import SafetyService

        tips = SafetyService(self.db).get_tips(city=city_name)
        data = {
            "city": tips.city or city_name,
            "tips": tips.tips,
            "nearby_hints": [hint.model_dump() for hint in tips.nearby_hints],
            "disclaimer": tips.disclaimer,
        }
        return ToolResult(
            name="find_nearby_safety",
            ok=True,
            data=data,
            message="Safety guidance prepared",
            provenance="unverified",
        )

    def search_knowledge(self, *, question: str, top_k: int = 3) -> ToolResult:
        from app.schemas.rag import RagQueryRequest
        from app.services.rag import RagService

        result = RagService(self.db).query(
            RagQueryRequest(question=question, top_k=top_k),
        )
        return ToolResult(
            name="search_knowledge",
            ok=result.verified,
            data=result.model_dump(),
            message="Grounded answer" if result.verified else "No verified sources",
            provenance="curated" if result.verified else "unverified",
        )
