"""PostgreSQL-backed multi-entity search (OpenSearch-ready later)."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Activity,
    City,
    Guide,
    Hotel,
    Restaurant,
    State,
    Temple,
    TouristPlace,
    TransportOption,
)
from app.repositories.places import haversine_km
from app.schemas.search import (
    AutocompleteSuggestion,
    SearchResponseData,
    SearchResultItem,
    TrendingSearchesData,
)

TRENDING_QUERIES = [
    "Goa beaches",
    "weekend from Hyderabad",
    "temples near Vizag",
    "Manali mountains",
    "Jaipur heritage",
    "Kerala backwaters",
    "budget trips Rajasthan",
    "Hampi ruins",
]


class SearchService:
    """Unified search across tourism entities using SQL ILIKE.

    Architecture note: swap this service's repository calls for OpenSearch later
    without changing API contracts.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def search(
        self,
        *,
        query: str,
        types: list[str] | None = None,
        category: str | None = None,
        state: str | None = None,
        min_rating: float | None = None,
        max_cost: int | None = None,
        lat: float | None = None,
        lng: float | None = None,
        radius_km: float | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> SearchResponseData:
        q = query.strip()
        selected = set(types or _default_types())
        items: list[SearchResultItem] = []

        if "places" in selected or "temples" in selected:
            items.extend(
                self._search_places(
                    q=q,
                    category=category,
                    state=state,
                    min_rating=min_rating,
                    max_cost=max_cost,
                    include_temple_only="temples" in selected and "places" not in selected,
                ),
            )
        if "hotels" in selected:
            items.extend(
                self._search_hotels(
                    q=q, state=state, min_rating=min_rating, max_cost=max_cost
                )
            )
        if "restaurants" in selected:
            items.extend(
                self._search_restaurants(q=q, state=state, min_rating=min_rating)
            )
        if "guides" in selected:
            items.extend(
                self._search_guides(
                    q=q, state=state, min_rating=min_rating, max_cost=max_cost
                )
            )
        if "transport" in selected:
            items.extend(self._search_transport(q=q, max_cost=max_cost))
        if "activities" in selected:
            items.extend(self._search_activities(q=q, state=state, max_cost=max_cost))
        if "cities" in selected:
            items.extend(self._search_cities(q=q, state=state))
        if "states" in selected:
            items.extend(self._search_states(q=q))

        if lat is not None and lng is not None:
            enriched: list[SearchResultItem] = []
            for item in items:
                if item.latitude is None or item.longitude is None:
                    if radius_km is not None:
                        continue
                    enriched.append(item)
                    continue
                distance = haversine_km(
                    lat,
                    lng,
                    float(item.latitude),
                    float(item.longitude),
                )
                if radius_km is not None and distance > radius_km:
                    continue
                enriched.append(item.model_copy(update={"distance_km": round(distance, 1)}))
            items = enriched
            items.sort(
                key=lambda row: (
                    row.distance_km if row.distance_km is not None else 1e9,
                    -(float(row.rating_avg) if row.rating_avg is not None else 0),
                ),
            )
        else:
            items.sort(
                key=lambda row: (
                    -(float(row.rating_avg) if row.rating_avg is not None else 0),
                    row.title.lower(),
                ),
            )

        facets: dict[str, int] = {}
        for item in items:
            facets[item.entity_type] = facets.get(item.entity_type, 0) + 1

        total = len(items)
        start = (page - 1) * page_size
        page_items = items[start : start + page_size]
        return SearchResponseData(
            query=q,
            total=total,
            items=page_items,
            facets=facets,
            page=page,
            page_size=page_size,
        )

    def autocomplete(self, *, query: str, limit: int = 8) -> list[AutocompleteSuggestion]:
        q = query.strip()
        if len(q) < 2:
            return []
        like = f"%{q}%"
        suggestions: list[AutocompleteSuggestion] = []

        places = self.db.scalars(
            select(TouristPlace)
            .where(
                TouristPlace.is_deleted.is_(False),
                or_(TouristPlace.name.ilike(like), TouristPlace.slug.ilike(like)),
            )
            .order_by(TouristPlace.rating_avg.desc())
            .limit(limit),
        ).all()
        for place in places:
            suggestions.append(
                AutocompleteSuggestion(
                    label=place.name,
                    entity_type="place",
                    id=place.id,
                    slug=place.slug,
                    href=f"/places/{place.id}",
                ),
            )

        cities = self.db.scalars(
            select(City)
            .options(selectinload(City.state))
            .where(or_(City.name.ilike(like), City.slug.ilike(like)))
            .limit(max(2, limit // 3)),
        ).all()
        for city in cities:
            suggestions.append(
                AutocompleteSuggestion(
                    label=f"{city.name}, {city.state.name}",
                    entity_type="city",
                    id=city.id,
                    slug=city.slug,
                    href=f"/search?q={city.name}&types=places,hotels,restaurants",
                ),
            )

        hotels = self.db.scalars(
            select(Hotel)
            .where(Hotel.is_deleted.is_(False), Hotel.name.ilike(like))
            .limit(max(2, limit // 3)),
        ).all()
        for hotel in hotels:
            suggestions.append(
                AutocompleteSuggestion(
                    label=hotel.name,
                    entity_type="hotel",
                    id=hotel.id,
                    slug=hotel.slug,
                    href=f"/hotels/{hotel.id}",
                ),
            )

        # de-dupe by label while preserving order
        seen: set[str] = set()
        unique: list[AutocompleteSuggestion] = []
        for item in suggestions:
            key = item.label.lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
            if len(unique) >= limit:
                break
        return unique

    def trending(self) -> TrendingSearchesData:
        featured = self.db.scalars(
            select(TouristPlace)
            .where(TouristPlace.is_deleted.is_(False), TouristPlace.is_featured.is_(True))
            .options(
                selectinload(TouristPlace.city).selectinload(City.state),
                selectinload(TouristPlace.category),
            )
            .order_by(TouristPlace.rating_avg.desc())
            .limit(6),
        ).all()
        place_items = [_place_item(place) for place in featured]
        return TrendingSearchesData(queries=list(TRENDING_QUERIES), places=place_items)

    def _search_places(
        self,
        *,
        q: str,
        category: str | None,
        state: str | None,
        min_rating: float | None,
        max_cost: int | None,
        include_temple_only: bool,
    ) -> list[SearchResultItem]:
        stmt = (
            select(TouristPlace)
            .where(TouristPlace.is_deleted.is_(False))
            .options(
                selectinload(TouristPlace.city).selectinload(City.state),
                selectinload(TouristPlace.category),
            )
        )
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                or_(
                    TouristPlace.name.ilike(like),
                    TouristPlace.short_description.ilike(like),
                    TouristPlace.description.ilike(like),
                    TouristPlace.slug.ilike(like),
                ),
            )
        places = list(self.db.scalars(stmt.limit(100)).all())
        results: list[SearchResultItem] = []
        for place in places:
            if category:
                slug = (place.category.slug if place.category else "").lower()
                name = (place.category.name if place.category else "").lower()
                if category.lower() not in {slug, name}:
                    continue
            if state and place.city.state.code.upper() != state.upper():
                continue
            if min_rating is not None and float(place.rating_avg) < min_rating:
                continue
            if max_cost is not None and (
                place.estimated_cost_inr is None or place.estimated_cost_inr > max_cost
            ):
                continue
            if include_temple_only:
                cat = (place.category.slug if place.category else "").lower()
                if cat != "temple":
                    temple = self.db.scalar(
                        select(Temple.id).where(Temple.place_id == place.id).limit(1),
                    )
                    if temple is None:
                        continue
            results.append(_place_item(place))
        return results

    def _search_hotels(
        self,
        *,
        q: str,
        state: str | None,
        min_rating: float | None,
        max_cost: int | None,
    ) -> list[SearchResultItem]:
        stmt = (
            select(Hotel)
            .where(Hotel.is_deleted.is_(False))
            .options(selectinload(Hotel.city).selectinload(City.state))
        )
        if q:
            like = f"%{q}%"
            stmt = stmt.where(or_(Hotel.name.ilike(like), Hotel.description.ilike(like)))
        hotels = list(self.db.scalars(stmt.limit(50)).all())
        items: list[SearchResultItem] = []
        for hotel in hotels:
            if state and hotel.city.state.code.upper() != state.upper():
                continue
            if min_rating is not None and float(hotel.rating_avg) < min_rating:
                continue
            if max_cost is not None and (
                hotel.starting_price_inr is None or hotel.starting_price_inr > max_cost
            ):
                continue
            items.append(
                SearchResultItem(
                    id=hotel.id,
                    entity_type="hotel",
                    title=hotel.name,
                    subtitle=hotel.description,
                    slug=hotel.slug,
                    category="Hotel",
                    location_label=f"{hotel.city.name}, {hotel.city.state.name}",
                    rating_avg=hotel.rating_avg,
                    estimated_cost_inr=hotel.starting_price_inr,
                    latitude=hotel.latitude,
                    longitude=hotel.longitude,
                    is_seed_data=hotel.is_seed_data,
                    href=f"/hotels/{hotel.id}",
                ),
            )
        return items

    def _search_restaurants(
        self,
        *,
        q: str,
        state: str | None,
        min_rating: float | None,
    ) -> list[SearchResultItem]:
        stmt = (
            select(Restaurant)
            .where(Restaurant.is_deleted.is_(False))
            .options(selectinload(Restaurant.city).selectinload(City.state))
        )
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Restaurant.name.ilike(like),
                    Restaurant.cuisine_tags.ilike(like),
                    Restaurant.description.ilike(like),
                ),
            )
        restaurants = list(self.db.scalars(stmt.limit(50)).all())
        items: list[SearchResultItem] = []
        for restaurant in restaurants:
            if state and restaurant.city.state.code.upper() != state.upper():
                continue
            if min_rating is not None and float(restaurant.rating_avg) < min_rating:
                continue
            items.append(
                SearchResultItem(
                    id=restaurant.id,
                    entity_type="restaurant",
                    title=restaurant.name,
                    subtitle=restaurant.cuisine_tags,
                    slug=restaurant.slug,
                    category="Restaurant",
                    location_label=f"{restaurant.city.name}, {restaurant.city.state.name}",
                    rating_avg=restaurant.rating_avg,
                    latitude=restaurant.latitude,
                    longitude=restaurant.longitude,
                    is_seed_data=restaurant.is_seed_data,
                    href=f"/restaurants/{restaurant.id}",
                ),
            )
        return items

    def _search_guides(
        self,
        *,
        q: str,
        state: str | None,
        min_rating: float | None,
        max_cost: int | None,
    ) -> list[SearchResultItem]:
        stmt = select(Guide).options(selectinload(Guide.city).selectinload(City.state))
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Guide.display_name.ilike(like),
                    Guide.specialization.ilike(like),
                    Guide.languages.ilike(like),
                    Guide.bio.ilike(like),
                ),
            )
        guides = list(self.db.scalars(stmt.limit(50)).all())
        items: list[SearchResultItem] = []
        for guide in guides:
            if state and guide.city.state.code.upper() != state.upper():
                continue
            if min_rating is not None and float(guide.rating_avg) < min_rating:
                continue
            if max_cost is not None and guide.price_per_day_inr > max_cost:
                continue
            items.append(
                SearchResultItem(
                    id=guide.id,
                    entity_type="guide",
                    title=guide.display_name,
                    subtitle=guide.specialization,
                    category="Guide",
                    location_label=f"{guide.city.name}, {guide.city.state.name}",
                    rating_avg=guide.rating_avg,
                    estimated_cost_inr=guide.price_per_day_inr,
                    is_seed_data=guide.is_seed_data,
                    href=f"/guides/{guide.id}",
                ),
            )
        return items

    def _search_transport(
        self,
        *,
        q: str,
        max_cost: int | None,
    ) -> list[SearchResultItem]:
        stmt = select(TransportOption).where(TransportOption.is_active.is_(True))
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                or_(
                    TransportOption.name.ilike(like),
                    TransportOption.code.ilike(like),
                    TransportOption.vehicle_type.ilike(like),
                    TransportOption.description.ilike(like),
                ),
            )
        options = list(self.db.scalars(stmt.limit(50)).all())
        items: list[SearchResultItem] = []
        for option in options:
            if max_cost is not None and option.base_fare_inr > max_cost:
                continue
            sample = None
            if option.base_fare_inr > 0 or option.per_km_inr > 0:
                sample = int(round(option.base_fare_inr + option.per_km_inr * 10))
            items.append(
                SearchResultItem(
                    id=option.id,
                    entity_type="transport",
                    title=option.name,
                    subtitle=option.vehicle_type.replace("_", " ").title(),
                    slug=option.code,
                    category="Transport",
                    location_label="India (demo fares)",
                    estimated_cost_inr=sample,
                    is_seed_data=option.is_seed_data,
                    href=f"/transport/{option.id}",
                ),
            )
        return items

    def _search_activities(
        self,
        *,
        q: str,
        state: str | None,
        max_cost: int | None,
    ) -> list[SearchResultItem]:
        stmt = (
            select(Activity)
            .where(Activity.is_deleted.is_(False))
            .options(selectinload(Activity.city).selectinload(City.state))
        )
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Activity.name.ilike(like),
                    Activity.category.ilike(like),
                    Activity.description.ilike(like),
                ),
            )
        activities = list(self.db.scalars(stmt.limit(50)).all())
        items: list[SearchResultItem] = []
        for activity in activities:
            if state and activity.city.state.code.upper() != state.upper():
                continue
            if max_cost is not None and activity.price_inr > max_cost:
                continue
            items.append(
                SearchResultItem(
                    id=activity.id,
                    entity_type="activity",
                    title=activity.name,
                    subtitle=activity.category,
                    slug=activity.slug,
                    category=activity.category,
                    location_label=f"{activity.city.name}, {activity.city.state.name}",
                    rating_avg=activity.rating_avg,
                    estimated_cost_inr=activity.price_inr,
                    latitude=activity.latitude,
                    longitude=activity.longitude,
                    is_seed_data=activity.is_seed_data,
                    href=f"/activities/{activity.id}",
                ),
            )
        return items

    def _search_cities(self, *, q: str, state: str | None) -> list[SearchResultItem]:
        stmt = select(City).options(selectinload(City.state))
        if q:
            like = f"%{q}%"
            stmt = stmt.where(or_(City.name.ilike(like), City.slug.ilike(like)))
        cities = list(self.db.scalars(stmt.limit(30)).all())
        items: list[SearchResultItem] = []
        for city in cities:
            if state and city.state.code.upper() != state.upper():
                continue
            items.append(
                SearchResultItem(
                    id=city.id,
                    entity_type="city",
                    title=city.name,
                    subtitle=city.state.name,
                    slug=city.slug,
                    category="City",
                    location_label=f"{city.name}, {city.state.name}",
                    latitude=city.latitude,
                    longitude=city.longitude,
                    is_seed_data=city.is_seed_data,
                    href=f"/explore?city={city.slug}",
                ),
            )
        return items

    def _search_states(self, *, q: str) -> list[SearchResultItem]:
        stmt = select(State)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(or_(State.name.ilike(like), State.code.ilike(like)))
        states = list(self.db.scalars(stmt.limit(20)).all())
        return [
            SearchResultItem(
                id=state.id,
                entity_type="state",
                title=state.name,
                subtitle=state.code,
                category="State",
                location_label=state.name,
                is_seed_data=state.is_seed_data,
                href=f"/search?q={state.name}&types=places,cities&state={state.code}",
            )
            for state in states
        ]


def _default_types() -> list[str]:
    return [
        "places",
        "hotels",
        "restaurants",
        "temples",
        "guides",
        "transport",
        "activities",
        "cities",
        "states",
    ]


def _place_item(place: TouristPlace) -> SearchResultItem:
    return SearchResultItem(
        id=place.id,
        entity_type="place",
        title=place.name,
        subtitle=place.short_description,
        slug=place.slug,
        category=place.category.name if place.category else None,
        location_label=f"{place.city.name}, {place.city.state.name}",
        rating_avg=place.rating_avg,
        estimated_cost_inr=place.estimated_cost_inr,
        latitude=place.latitude,
        longitude=place.longitude,
        is_seed_data=place.is_seed_data,
        href=f"/places/{place.id}",
    )


def parse_types(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    parts = [part.strip().lower() for part in raw.split(",") if part.strip()]
    allowed = set(_default_types())
    filtered = [part for part in parts if part in allowed]
    return filtered or None
