"""Database seed helpers for demo Indian tourism data.

All seeded rows are marked `is_seed_data=True` (or equivalent) and must not be
treated as verified official business or religious information.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import (
    Activity,
    City,
    Coupon,
    DataProvenance,
    Guide,
    GuideAvailability,
    Hotel,
    HotelRoom,
    PlaceCategory,
    PlaceCategoryCode,
    Restaurant,
    RestaurantMenuItem,
    Role,
    State,
    Temple,
    TouristPlace,
    TransportOption,
    User,
    UserProfile,
    UserRole,
    UserRoleLink,
    VehicleType,
)

logger = logging.getLogger(__name__)

SEED_MARKER = "[SEED/DEMO]"
DEMO_OWNER_EMAIL = "demo.owner@example.com"
DEMO_OWNER_PASSWORD = "DemoOwner1!"
DEMO_ADMIN_EMAIL = "demo.admin@example.com"
DEMO_ADMIN_PASSWORD = "DemoAdmin1!"


def seed_all(session: Session, *, force: bool = False) -> dict[str, int]:
    """Idempotent seed. Returns counts of rows created."""
    counts = {
        "roles": _seed_roles(session),
        "states": 0,
        "cities": 0,
        "categories": 0,
        "places": 0,
        "temples": 0,
        "hotels": 0,
        "restaurants": 0,
        "guides": 0,
        "activities": 0,
        "transport_options": 0,
        "users": 0,
        "coupons": 0,
        "knowledge": 0,
    }

    if not force and session.scalar(select(State.id).where(State.is_seed_data.is_(True)).limit(1)):
        logger.info("Seed data already present; skipping (use force=True to re-check children)")
        counts["coupons"] = _seed_coupons(session)
        counts["users"] = (
            _seed_demo_user(session)
            + _seed_business_owner(session)
            + _seed_admin_user(session)
        )
        counts["knowledge"] = _seed_knowledge(session)
        session.commit()
        return counts

    counts["states"], state_map = _seed_states(session)
    counts["cities"], city_map = _seed_cities(session, state_map)
    counts["categories"], category_map = _seed_categories(session)
    counts["places"], place_map = _seed_places(session, city_map, category_map)
    counts["temples"] = _seed_temples(session, place_map)
    counts["hotels"] = _seed_hotels(session, city_map)
    counts["restaurants"] = _seed_restaurants(session, city_map)
    counts["guides"] = _seed_guides(session, city_map)
    counts["activities"] = _seed_activities(session, city_map)
    counts["transport_options"] = _seed_transport_options(session)
    counts["users"] = (
        _seed_demo_user(session)
        + _seed_business_owner(session)
        + _seed_admin_user(session)
    )
    counts["coupons"] = _seed_coupons(session)
    counts["knowledge"] = _seed_knowledge(session)
    session.commit()
    logger.info("Seed complete: %s", counts)
    return counts


def _seed_roles(session: Session) -> int:
    created = 0
    for role in UserRole:
        exists = session.scalar(select(Role.id).where(Role.name == role.value))
        if exists:
            continue
        session.add(Role(name=role.value, description=f"{SEED_MARKER} Role {role.value}"))
        created += 1
    session.flush()
    return created


def _seed_states(session: Session) -> tuple[int, dict[str, State]]:
    specs = [
        ("Andhra Pradesh", "AP", False),
        ("Telangana", "TG", False),
        ("Karnataka", "KA", False),
        ("Tamil Nadu", "TN", False),
        ("Kerala", "KL", False),
        ("Goa", "GA", False),
        ("Maharashtra", "MH", False),
        ("Rajasthan", "RJ", False),
        ("Delhi", "DL", True),
        ("Uttar Pradesh", "UP", False),
        ("Himachal Pradesh", "HP", False),
        ("Uttarakhand", "UK", False),
        ("Odisha", "OD", False),
        ("West Bengal", "WB", False),
    ]
    created = 0
    mapping: dict[str, State] = {}
    for name, code, is_ut in specs:
        existing = session.scalar(select(State).where(State.code == code))
        if existing:
            mapping[code] = existing
            continue
        state = State(
            name=name,
            code=code,
            is_union_territory=is_ut,
            is_seed_data=True,
        )
        session.add(state)
        mapping[code] = state
        created += 1
    session.flush()
    return created, mapping


def _seed_cities(
    session: Session,
    state_map: dict[str, State],
) -> tuple[int, dict[str, City]]:
    specs = [
        ("Hyderabad", "hyderabad", "TG", "17.3850440", "78.4866710", True),
        ("Visakhapatnam", "visakhapatnam", "AP", "17.6868150", "83.2184820", True),
        ("Bengaluru", "bengaluru", "KA", "12.9715990", "77.5945660", True),
        ("Mysuru", "mysuru", "KA", "12.2958100", "76.6393810", False),
        ("Chennai", "chennai", "TN", "13.0826800", "80.2707180", True),
        ("Madurai", "madurai", "TN", "9.9252010", "78.1197740", False),
        ("Kochi", "kochi", "KL", "9.9312330", "76.2673030", True),
        ("Thiruvananthapuram", "thiruvananthapuram", "KL", "8.5241390", "76.9366380", False),
        ("Panaji", "panaji", "GA", "15.4909300", "73.8278500", True),
        ("Mumbai", "mumbai", "MH", "19.0760900", "72.8774260", True),
        ("Pune", "pune", "MH", "18.5204300", "73.8567440", True),
        ("Jaipur", "jaipur", "RJ", "26.9124340", "75.7872710", True),
        ("Udaipur", "udaipur", "RJ", "24.5854450", "73.7124790", True),
        ("New Delhi", "new-delhi", "DL", "28.6139390", "77.2090230", True),
        ("Varanasi", "varanasi", "UP", "25.3176450", "82.9739140", True),
        ("Agra", "agra", "UP", "27.1766700", "78.0080750", True),
        ("Manali", "manali", "HP", "32.2396320", "77.1887130", True),
        ("Shimla", "shimla", "HP", "31.1046050", "77.1734240", True),
        ("Rishikesh", "rishikesh", "UK", "30.0869280", "78.2676090", True),
        ("Puri", "puri", "OD", "19.8134550", "85.8312360", True),
        ("Kolkata", "kolkata", "WB", "22.5726460", "88.3638950", True),
        ("Darjeeling", "darjeeling", "WB", "27.0360070", "88.2626750", True),
        ("Hampi", "hampi", "KA", "15.3350130", "76.4600250", True),
        ("Tirupati", "tirupati", "AP", "13.6287560", "79.4191790", True),
    ]
    created = 0
    mapping: dict[str, City] = {}
    for name, slug, state_code, lat, lng, popular in specs:
        state = state_map[state_code]
        existing = session.scalar(
            select(City).where(City.state_id == state.id, City.slug == slug),
        )
        if existing:
            mapping[slug] = existing
            continue
        city = City(
            state_id=state.id,
            name=name,
            slug=slug,
            latitude=Decimal(lat),
            longitude=Decimal(lng),
            is_popular=popular,
            is_seed_data=True,
        )
        session.add(city)
        mapping[slug] = city
        created += 1
    session.flush()
    return created, mapping


def _seed_categories(session: Session) -> tuple[int, dict[str, PlaceCategory]]:
    specs = [
        (PlaceCategoryCode.TEMPLE, "Temples", "landmark", 10),
        (PlaceCategoryCode.BEACH, "Beaches", "waves", 20),
        (PlaceCategoryCode.MOUNTAIN, "Mountains", "mountain", 30),
        (PlaceCategoryCode.WATERFALL, "Waterfalls", "droplets", 40),
        (PlaceCategoryCode.HISTORICAL, "Historical", "landmark", 50),
        (PlaceCategoryCode.WILDLIFE, "Wildlife", "paw-print", 60),
        (PlaceCategoryCode.ADVENTURE, "Adventure", "compass", 70),
        (PlaceCategoryCode.FOOD, "Food experiences", "utensils", 80),
        (PlaceCategoryCode.HIDDEN_GEM, "Hidden gems", "sparkles", 90),
        (PlaceCategoryCode.NATURE, "Nature", "leaf", 100),
        (PlaceCategoryCode.CITY, "City highlights", "building", 110),
    ]
    created = 0
    mapping: dict[str, PlaceCategory] = {}
    for code, name, icon, order in specs:
        existing = session.scalar(select(PlaceCategory).where(PlaceCategory.slug == code.value))
        if existing:
            mapping[code.value] = existing
            continue
        category = PlaceCategory(
            name=name,
            slug=code.value,
            description=f"{SEED_MARKER} Category for {name}",
            icon=icon,
            sort_order=order,
            is_seed_data=True,
        )
        session.add(category)
        mapping[code.value] = category
        created += 1
    session.flush()
    return created, mapping


def _seed_places(
    session: Session,
    city_map: dict[str, City],
    category_map: dict[str, PlaceCategory],
) -> tuple[int, dict[str, TouristPlace]]:
    specs = [
        {
            "slug": "charminar-hyderabad-demo",
            "name": f"{SEED_MARKER} Charminar Heritage Walk Area",
            "city": "hyderabad",
            "category": PlaceCategoryCode.HISTORICAL.value,
            "lat": "17.3616000",
            "lng": "78.4747000",
            "cost": 500,
            "short": "Demo destination near Hyderabad's historic old city area.",
            "featured": True,
        },
        {
            "slug": "rk-beach-vizag-demo",
            "name": f"{SEED_MARKER} RK Beach Promenade",
            "city": "visakhapatnam",
            "category": PlaceCategoryCode.BEACH.value,
            "lat": "17.7140000",
            "lng": "83.3230000",
            "cost": 300,
            "short": "Demo beachside walk destination for Vizag weekend trips.",
            "featured": True,
        },
        {
            "slug": "hampi-ruins-demo",
            "name": f"{SEED_MARKER} Hampi Monument Circuit",
            "city": "hampi",
            "category": PlaceCategoryCode.HISTORICAL.value,
            "lat": "15.3350000",
            "lng": "76.4600000",
            "cost": 1200,
            "short": "Demo heritage circuit inspired by the Hampi landscape.",
            "featured": True,
        },
        {
            "slug": "meenakshi-area-madurai-demo",
            "name": f"{SEED_MARKER} Madurai Temple Town Walk",
            "city": "madurai",
            "category": PlaceCategoryCode.TEMPLE.value,
            "lat": "9.9195000",
            "lng": "78.1193000",
            "cost": 400,
            "short": "Demo pilgrimage-friendly city walk. Timings not verified.",
            "featured": True,
        },
        {
            "slug": "fort-kochi-demo",
            "name": f"{SEED_MARKER} Fort Kochi Waterfront",
            "city": "kochi",
            "category": PlaceCategoryCode.CITY.value,
            "lat": "9.9650000",
            "lng": "76.2420000",
            "cost": 800,
            "short": "Demo coastal heritage neighbourhood for slow travel.",
            "featured": True,
        },
        {
            "slug": "baga-beach-goa-demo",
            "name": f"{SEED_MARKER} Baga Beach Stretch",
            "city": "panaji",
            "category": PlaceCategoryCode.BEACH.value,
            "lat": "15.5570000",
            "lng": "73.7520000",
            "cost": 1000,
            "short": "Demo Goa beach destination for couples and friends.",
            "featured": True,
        },
        {
            "slug": "gateway-mumbai-demo",
            "name": f"{SEED_MARKER} Colaba Waterfront Walk",
            "city": "mumbai",
            "category": PlaceCategoryCode.CITY.value,
            "lat": "18.9220000",
            "lng": "72.8347000",
            "cost": 700,
            "short": "Demo Mumbai sightseeing starter itinerary node.",
            "featured": False,
        },
        {
            "slug": "amber-fort-area-jaipur-demo",
            "name": f"{SEED_MARKER} Amer Fort Viewpoint Circuit",
            "city": "jaipur",
            "category": PlaceCategoryCode.HISTORICAL.value,
            "lat": "26.9855000",
            "lng": "75.8513000",
            "cost": 900,
            "short": "Demo Jaipur fort-and-viewpoints circuit.",
            "featured": True,
        },
        {
            "slug": "india-gate-delhi-demo",
            "name": f"{SEED_MARKER} Central Vista Evening Walk",
            "city": "new-delhi",
            "category": PlaceCategoryCode.CITY.value,
            "lat": "28.6129000",
            "lng": "77.2295000",
            "cost": 200,
            "short": "Demo Delhi evening walk destination.",
            "featured": False,
        },
        {
            "slug": "ghats-varanasi-demo",
            "name": f"{SEED_MARKER} Varanasi Ghat Experience Trail",
            "city": "varanasi",
            "category": PlaceCategoryCode.TEMPLE.value,
            "lat": "25.3109000",
            "lng": "83.0107000",
            "cost": 600,
            "short": "Demo spiritual city trail. Ritual timings not verified.",
            "featured": True,
        },
        {
            "slug": "taj-agra-demo",
            "name": f"{SEED_MARKER} Agra Monument Sunrise Circuit",
            "city": "agra",
            "category": PlaceCategoryCode.HISTORICAL.value,
            "lat": "27.1751000",
            "lng": "78.0421000",
            "cost": 1500,
            "short": "Demo Agra heritage day plan node.",
            "featured": True,
        },
        {
            "slug": "solang-manali-demo",
            "name": f"{SEED_MARKER} Solang Valley Meadow Trail",
            "city": "manali",
            "category": PlaceCategoryCode.MOUNTAIN.value,
            "lat": "32.3160000",
            "lng": "77.1570000",
            "cost": 1800,
            "short": "Demo Himachal nature/adventure destination.",
            "featured": True,
            "hidden": False,
            "adventure": True,
        },
        {
            "slug": "rishikesh-ganges-demo",
            "name": f"{SEED_MARKER} Rishikesh Riverside Trails",
            "city": "rishikesh",
            "category": PlaceCategoryCode.NATURE.value,
            "lat": "30.0869000",
            "lng": "78.2676000",
            "cost": 1100,
            "short": "Demo Uttarakhand peaceful nature getaway.",
            "featured": True,
        },
        {
            "slug": "puri-beach-demo",
            "name": f"{SEED_MARKER} Puri Seafront Promenade",
            "city": "puri",
            "category": PlaceCategoryCode.BEACH.value,
            "lat": "19.7980000",
            "lng": "85.8250000",
            "cost": 500,
            "short": "Demo Odisha beach destination near pilgrimage circuits.",
            "featured": False,
        },
        {
            "slug": "victoria-kolkata-demo",
            "name": f"{SEED_MARKER} Kolkata Colonial Park Circuit",
            "city": "kolkata",
            "category": PlaceCategoryCode.CITY.value,
            "lat": "22.5448000",
            "lng": "88.3426000",
            "cost": 400,
            "short": "Demo Kolkata city highlights walk.",
            "featured": False,
        },
        {
            "slug": "darjeeling-tea-demo",
            "name": f"{SEED_MARKER} Darjeeling Tea Estate Viewpoints",
            "city": "darjeeling",
            "category": PlaceCategoryCode.MOUNTAIN.value,
            "lat": "27.0360000",
            "lng": "88.2627000",
            "cost": 1400,
            "short": "Demo hill-station viewpoints and tea landscape.",
            "featured": True,
            "hidden": True,
        },
        {
            "slug": "tirumala-area-demo",
            "name": f"{SEED_MARKER} Tirupati Pilgrim Precinct Walk",
            "city": "tirupati",
            "category": PlaceCategoryCode.TEMPLE.value,
            "lat": "13.6830000",
            "lng": "79.3470000",
            "cost": 700,
            "short": "Demo pilgrimage area listing. Darshan timings not verified.",
            "featured": True,
        },
        {
            "slug": "udaipur-lake-demo",
            "name": f"{SEED_MARKER} Udaipur Lake Circumference Walk",
            "city": "udaipur",
            "category": PlaceCategoryCode.CITY.value,
            "lat": "24.5760000",
            "lng": "73.6800000",
            "cost": 900,
            "short": "Demo romantic lake-city evening plan.",
            "featured": True,
        },
    ]

    created = 0
    mapping: dict[str, TouristPlace] = {}
    for item in specs:
        existing = session.scalar(select(TouristPlace).where(TouristPlace.slug == item["slug"]))
        if existing:
            mapping[item["slug"]] = existing
            continue
        city = city_map[item["city"]]
        category = category_map[item["category"]]
        place = TouristPlace(
            city_id=city.id,
            category_id=category.id,
            name=item["name"],
            slug=item["slug"],
            short_description=item["short"],
            description=(
                f"{item['short']} {SEED_MARKER} content for development and demos. "
                "Opening hours and fees are not official."
            ),
            latitude=Decimal(item["lat"]),
            longitude=Decimal(item["lng"]),
            rating_avg=Decimal("4.40"),
            rating_count=12,
            estimated_cost_inr=item["cost"],
            best_time_to_visit="October–March (general guidance, unverified)",
            entry_fee_notes="Entry fees vary; verify on-site or via official sources.",
            opening_hours=None,
            facilities=(
                f"{SEED_MARKER} Common visitor facilities vary by site "
                "(restrooms, drinking water, shaded seating). Confirm locally."
            ),
            how_to_reach=(
                f"{SEED_MARKER} Reach via local transport from {item['city']}. "
                "Exact routes and schedules are not verified in this dataset."
            ),
            is_featured=bool(item.get("featured", False)),
            is_hidden_gem=bool(item.get("hidden", False)),
            provenance=DataProvenance.SEED_DEMO.value,
            is_seed_data=True,
        )
        session.add(place)
        mapping[item["slug"]] = place
        created += 1
    session.flush()
    return created, mapping


def _seed_temples(session: Session, place_map: dict[str, TouristPlace]) -> int:
    links = [
        ("meenakshi-area-madurai-demo", "Madurai Temple Town (Demo)", "Community listing"),
        ("ghats-varanasi-demo", "Varanasi Ghat Circuit (Demo)", "Community listing"),
        ("tirumala-area-demo", "Tirupati Precinct (Demo)", "Community listing"),
    ]
    created = 0
    for slug, name, note in links:
        place = place_map.get(slug)
        if not place:
            continue
        existing = session.scalar(select(Temple).where(Temple.place_id == place.id))
        if existing:
            continue
        session.add(
            Temple(
                place_id=place.id,
                name=name,
                history=f"{SEED_MARKER} Historical narrative placeholder.",
                entry_information=(
                    f"{note}. {SEED_MARKER} Do not treat as official darshan guidance."
                ),
                provenance=DataProvenance.UNVERIFIED.value,
                is_seed_data=True,
            ),
        )
        created += 1
    session.flush()
    return created


def _seed_hotels(session: Session, city_map: dict[str, City]) -> int:
    specs = [
        ("hyderabad", "golconda-inn-demo", f"{SEED_MARKER} Golconda Inn", 2200),
        ("jaipur", "pink-courtyard-demo", f"{SEED_MARKER} Pink Courtyard Stay", 2800),
        ("kochi", "harbour-leaf-demo", f"{SEED_MARKER} Harbour Leaf Homestay", 2500),
        ("manali", "cedar-nest-demo", f"{SEED_MARKER} Cedar Nest Lodge", 3200),
        ("panaji", "palm-breeze-demo", f"{SEED_MARKER} Palm Breeze Rooms", 3500),
    ]

    created = 0
    for city_slug, slug, name, price in specs:
        city = city_map[city_slug]
        existing = session.scalar(select(Hotel).where(Hotel.slug == slug))
        if existing:
            continue
        hotel = Hotel(
            city_id=city.id,
            name=name,
            slug=slug,
            description=f"{SEED_MARKER} Fictional hotel for booking-flow demos.",
            address=f"{SEED_MARKER} Near city centre, {city.name}",
            latitude=city.latitude,
            longitude=city.longitude,
            starting_price_inr=price,
            rating_avg=Decimal("4.20"),
            rating_count=8,
            has_wifi=True,
            has_ac=True,
            has_breakfast=True,
            has_parking=True,
            is_seed_data=True,
        )
        session.add(hotel)
        session.flush()
        session.add(
            HotelRoom(
                hotel_id=hotel.id,
                name="Standard Twin",
                max_guests=2,
                price_per_night_inr=price,
                total_rooms=5,
            ),
        )
        created += 1
    session.flush()
    return created


def _seed_restaurants(session: Session, city_map: dict[str, City]) -> int:
    specs = [
        (
            "hyderabad",
            "pearl-biryani-demo",
            f"{SEED_MARKER} Pearl Biryani House",
            "Hyderabadi",
            True,
        ),
        (
            "chennai",
            "filter-cafe-demo",
            f"{SEED_MARKER} Filter Cafe",
            "South Indian",
            True,
        ),
        (
            "jaipur",
            "spice-baithak-demo",
            f"{SEED_MARKER} Spice Baithak",
            "Rajasthani",
            True,
        ),
        (
            "kolkata",
            "river-mishti-demo",
            f"{SEED_MARKER} River Mishti Corner",
            "Bengali sweets",
            True,
        ),
        (
            "mumbai",
            "coastal-thali-demo",
            f"{SEED_MARKER} Coastal Thali Kitchen",
            "Maharashtrian",
            False,
        ),
    ]
    created = 0
    for city_slug, slug, name, cuisine, veg in specs:
        city = city_map[city_slug]
        existing = session.scalar(select(Restaurant).where(Restaurant.slug == slug))
        if existing:
            continue
        restaurant = Restaurant(
            city_id=city.id,
            name=name,
            slug=slug,
            description=f"{SEED_MARKER} Fictional restaurant for food discovery demos.",
            cuisine_tags=cuisine,
            address=f"{SEED_MARKER} Food street area, {city.name}",
            latitude=city.latitude,
            longitude=city.longitude,
            is_vegetarian=veg,
            price_level=2,
            rating_avg=Decimal("4.30"),
            rating_count=15,
            opening_hours="Hours vary — confirm locally (demo)",
            is_seed_data=True,
        )
        session.add(restaurant)
        session.flush()
        session.add(
            RestaurantMenuItem(
                restaurant_id=restaurant.id,
                name="Demo Special Thali",
                description="Sample menu item for checkout flows.",
                price_inr=249,
                is_veg=veg,
            ),
        )
        created += 1
    session.flush()
    return created


def _seed_guides(session: Session, city_map: dict[str, City]) -> int:
    specs = [
        ("hampi", "Asha Rao", "English, Kannada, Hindi", "Heritage walks", 8, 2500),
        ("jaipur", "Imran Khan", "English, Hindi", "Forts & culture", 10, 3000),
        ("varanasi", "Meera Tripathi", "English, Hindi", "Spiritual city trails", 12, 2800),
        ("kochi", "Joseph D'Souza", "English, Malayalam", "Food & harbour walks", 6, 2200),
    ]
    created = 0
    today = date.today()
    for city_slug, name, languages, spec, years, price in specs:
        city = city_map[city_slug]
        guide = session.scalar(
            select(Guide).where(Guide.display_name == f"{SEED_MARKER} {name}"),
        )
        if guide is None:
            guide = Guide(
                city_id=city.id,
                display_name=f"{SEED_MARKER} {name}",
                bio=f"{SEED_MARKER} Fictional local guide profile.",
                languages=languages,
                specialization=spec,
                experience_years=years,
                price_per_day_inr=price,
                rating_avg=Decimal("4.70"),
                rating_count=20,
                is_seed_data=True,
            )
            session.add(guide)
            session.flush()
            created += 1
        for offset in range(1, 8):
            available_date = today + timedelta(days=offset)
            exists = session.scalar(
                select(GuideAvailability.id).where(
                    GuideAvailability.guide_id == guide.id,
                    GuideAvailability.available_date == available_date,
                ),
            )
            if exists:
                continue
            session.add(
                GuideAvailability(
                    guide_id=guide.id,
                    available_date=available_date,
                    is_available=True,
                ),
            )
    session.flush()
    return created


def _seed_activities(session: Session, city_map: dict[str, City]) -> int:
    specs = [
        (
            "rishikesh",
            "ganges-raft-demo",
            f"{SEED_MARKER} Gentle Ganges Raft Intro",
            "adventure",
            1800,
        ),
        (
            "manali",
            "meadow-trek-demo",
            f"{SEED_MARKER} Meadow Half-Day Trek",
            "trekking",
            1500,
        ),
        (
            "panaji",
            "sunset-sail-demo",
            f"{SEED_MARKER} Sunset Sail Demo",
            "boating",
            2200,
        ),
        (
            "jaipur",
            "old-city-photo-demo",
            f"{SEED_MARKER} Old City Photo Walk",
            "photography",
            1200,
        ),
    ]
    created = 0
    for city_slug, slug, name, category, price in specs:
        city = city_map[city_slug]
        existing = session.scalar(select(Activity).where(Activity.slug == slug))
        if existing:
            # Backfill coords for nearby demos if missing
            if existing.latitude is None and city.latitude is not None:
                existing.latitude = city.latitude
                existing.longitude = city.longitude
            continue
        session.add(
            Activity(
                city_id=city.id,
                name=name,
                slug=slug,
                category=category,
                description=f"{SEED_MARKER} Fictional activity for booking demos.",
                duration_hours=Decimal("3.00"),
                price_inr=price,
                safety_information="Follow operator safety briefing. Demo only.",
                latitude=city.latitude,
                longitude=city.longitude,
                rating_avg=Decimal("4.60"),
                rating_count=18,
                is_seed_data=True,
            ),
        )
        created += 1
    session.flush()
    return created


def _seed_transport_options(session: Session) -> int:
    specs = [
        (VehicleType.AUTO, "Auto rickshaw", 40, 12),
        (VehicleType.TAXI, "City taxi", 80, 18),
        (VehicleType.BIKE, "Bike taxi", 30, 10),
        (VehicleType.SCOOTER, "Scooter rental", 0, 0),
        (VehicleType.RENTAL_CAR, "Self-drive car", 0, 0),
        (VehicleType.BUS, "Intercity bus", 0, 0),
        (VehicleType.TRAIN, "Train", 0, 0),
        (VehicleType.AIRPORT_TRANSFER, "Airport transfer", 300, 20),
        (VehicleType.OUTSTATION_CAB, "Outstation cab", 500, 16),
    ]
    created = 0
    for vehicle, name, base, per_km in specs:
        existing = session.scalar(
            select(TransportOption).where(TransportOption.code == vehicle.value),
        )
        if existing:
            continue
        session.add(
            TransportOption(
                code=vehicle.value,
                name=name,
                vehicle_type=vehicle.value,
                description=f"{SEED_MARKER} Fare estimates are mock values.",
                base_fare_inr=base,
                per_km_inr=per_km,
                is_seed_data=True,
            ),
        )
        created += 1
    session.flush()
    return created


def _seed_coupons(session: Session) -> int:
    specs = [
        ("BYDEMO10", f"{SEED_MARKER} 10% off mock bookings", 10, None),
        ("BYFLAT100", f"{SEED_MARKER} Flat ₹100 off mock bookings", None, 100),
    ]
    created = 0
    for code, description, percent, flat in specs:
        existing = session.scalar(select(Coupon).where(Coupon.code == code))
        if existing:
            continue
        session.add(
            Coupon(
                code=code,
                description=description,
                discount_percent=percent,
                discount_amount_inr=flat,
                max_redemptions=1000,
                redeemed_count=0,
                is_active=True,
                is_seed_data=True,
            ),
        )
        created += 1
    session.flush()
    return created


def _seed_demo_user(session: Session) -> int:
    email = "demo.traveller@bharatyatra.local"
    existing = session.scalar(select(User).where(User.email == email))
    if existing:
        return 0
    user = User(
        email=email,
        full_name="Demo Traveller",
        primary_role=UserRole.USER.value,
        is_email_verified=True,
        is_seed_data=True,
        password_hash=None,
    )
    session.add(user)
    session.flush()
    session.add(
        UserProfile(
            user_id=user.id,
            preferred_language="en",
            home_city="Hyderabad",
            travel_preferences='["family","nature","food"]',
            bio=f"{SEED_MARKER} Demo profile for local development.",
        ),
    )
    session.flush()
    return 1


def _ensure_role_link(session: Session, *, user_id, role_name: str) -> None:
    role = session.scalar(select(Role).where(Role.name == role_name))
    if role is None:
        role = Role(name=role_name, description=f"{SEED_MARKER} Role {role_name}")
        session.add(role)
        session.flush()
    exists = session.scalar(
        select(UserRoleLink).where(
            UserRoleLink.user_id == user_id,
            UserRoleLink.role_id == role.id,
        ),
    )
    if not exists:
        session.add(UserRoleLink(user_id=user_id, role_id=role.id))


def _seed_business_owner(session: Session) -> int:
    """Seed a demo owner with linked hotels, restaurants, and a guide profile."""
    created = 0
    existing = session.scalar(select(User).where(User.email == DEMO_OWNER_EMAIL))
    if existing is None:
        user = User(
            email=DEMO_OWNER_EMAIL,
            full_name="Demo Business Owner",
            primary_role=UserRole.HOTEL_OWNER.value,
            is_email_verified=True,
            is_seed_data=True,
            password_hash=hash_password(DEMO_OWNER_PASSWORD),
        )
        session.add(user)
        session.flush()
        session.add(
            UserProfile(
                user_id=user.id,
                preferred_language="en",
                home_city="Hyderabad",
                travel_preferences='["hospitality","guides"]',
                bio=(
                    f"{SEED_MARKER} Demo business owner for Phase 21 dashboard. "
                    f"Login: {DEMO_OWNER_EMAIL} / {DEMO_OWNER_PASSWORD}"
                ),
            ),
        )
        created = 1
    else:
        user = existing
        if not user.password_hash:
            user.password_hash = hash_password(DEMO_OWNER_PASSWORD)
        if user.primary_role == UserRole.USER.value:
            user.primary_role = UserRole.HOTEL_OWNER.value

    for role_name in (
        UserRole.HOTEL_OWNER.value,
        UserRole.RESTAURANT_OWNER.value,
        UserRole.GUIDE.value,
    ):
        _ensure_role_link(session, user_id=user.id, role_name=role_name)

    hotels = list(
        session.scalars(
            select(Hotel)
            .where(Hotel.is_seed_data.is_(True))
            .order_by(Hotel.slug.asc())
            .limit(2),
        ).all(),
    )
    for hotel in hotels:
        if hotel.owner_user_id is None:
            hotel.owner_user_id = user.id

    restaurants = list(
        session.scalars(
            select(Restaurant)
            .where(Restaurant.is_seed_data.is_(True))
            .order_by(Restaurant.slug.asc())
            .limit(2),
        ).all(),
    )
    for restaurant in restaurants:
        if restaurant.owner_user_id is None:
            restaurant.owner_user_id = user.id

    guide = session.scalar(
        select(Guide)
        .where(Guide.is_seed_data.is_(True), Guide.user_id.is_(None))
        .order_by(Guide.display_name.asc())
        .limit(1),
    )
    if guide is not None:
        guide.user_id = user.id

    session.flush()
    return created


def _seed_admin_user(session: Session) -> int:
    """Seed a demo platform admin for Phase 22 dashboard."""
    existing = session.scalar(select(User).where(User.email == DEMO_ADMIN_EMAIL))
    if existing is None:
        user = User(
            email=DEMO_ADMIN_EMAIL,
            full_name="Demo Platform Admin",
            primary_role=UserRole.ADMIN.value,
            is_email_verified=True,
            is_seed_data=True,
            password_hash=hash_password(DEMO_ADMIN_PASSWORD),
        )
        session.add(user)
        session.flush()
        session.add(
            UserProfile(
                user_id=user.id,
                preferred_language="en",
                home_city="New Delhi",
                travel_preferences='["ops","moderation"]',
                bio=(
                    f"{SEED_MARKER} Demo admin for Phase 22 dashboard. "
                    f"Login: {DEMO_ADMIN_EMAIL} / {DEMO_ADMIN_PASSWORD}"
                ),
            ),
        )
        created = 1
    else:
        user = existing
        created = 0
        if not user.password_hash:
            user.password_hash = hash_password(DEMO_ADMIN_PASSWORD)
        if user.primary_role not in {
            UserRole.ADMIN.value,
            UserRole.SUPER_ADMIN.value,
        }:
            user.primary_role = UserRole.ADMIN.value

    _ensure_role_link(session, user_id=user.id, role_name=UserRole.ADMIN.value)
    session.flush()
    return created


def _seed_knowledge(session: Session) -> int:
    """Seed curated RAG documents (idempotent via source_uri)."""
    from app.services.rag import RagService

    before = len(RagService(session).list_documents(limit=100))
    RagService(session).seed_demo_corpus()
    after = len(RagService(session).list_documents(limit=100))
    return max(after - before, 0)
