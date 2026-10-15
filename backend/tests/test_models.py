"""Model metadata and schema structure tests (no live Postgres required)."""

from __future__ import annotations

from sqlalchemy import create_engine

from app.core.database import Base, init_models
from app.models.enums import UserRole

EXPECTED_TABLES = {
    "users",
    "user_profiles",
    "roles",
    "permissions",
    "user_roles",
    "role_permissions",
    "refresh_tokens",
    "password_reset_tokens",
    "otp_challenges",
    "tourist_places",
    "place_categories",
    "place_images",
    "place_reviews",
    "states",
    "cities",
    "temples",
    "temple_timings",
    "hotels",
    "hotel_rooms",
    "hotel_reviews",
    "restaurants",
    "restaurant_menus",
    "food_orders",
    "guides",
    "guide_availability",
    "guide_bookings",
    "drivers",
    "vehicles",
    "rides",
    "ride_locations",
    "transport_options",
    "activities",
    "activity_bookings",
    "trips",
    "trip_days",
    "trip_places",
    "bookings",
    "payments",
    "wallets",
    "coupons",
    "notifications",
    "saved_places",
    "user_reviews",
    "support_tickets",
    "emergency_contacts",
    "ai_conversations",
    "ai_messages",
    "knowledge_documents",
    "knowledge_chunks",
}


def test_all_expected_tables_are_registered() -> None:
    init_models()
    assert EXPECTED_TABLES.issubset(set(Base.metadata.tables))
    assert len(Base.metadata.tables) >= len(EXPECTED_TABLES)


def test_user_roles_enum_covers_required_roles() -> None:
    names = {role.value for role in UserRole}
    assert names == {
        "USER",
        "ADMIN",
        "SUPER_ADMIN",
        "GUIDE",
        "DRIVER",
        "HOTEL_OWNER",
        "RESTAURANT_OWNER",
        "TOUR_OPERATOR",
    }


def test_metadata_create_all_on_sqlite() -> None:
    """Structural smoke test — SQLite approximates Postgres DDL."""
    init_models()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    assert "tourist_places" in Base.metadata.tables
    with engine.connect() as conn:
        result = conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='states'",
        )
        assert result.fetchone() is not None
    engine.dispose()
