"""Seed service unit tests using in-memory SQLite."""

from __future__ import annotations

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, init_models
from app.models import City, PlaceCategory, State, TouristPlace, User
from app.services.seed import SEED_MARKER, seed_all


def test_seed_all_is_idempotent_on_sqlite() -> None:
    init_models()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session: Session = SessionLocal()
    try:
        first = seed_all(session, force=True)
        assert first["states"] == 14
        assert first["cities"] >= 20
        assert first["places"] >= 15
        assert first["users"] == 3

        states = session.scalars(select(State).where(State.is_seed_data.is_(True))).all()
        assert all(state.is_seed_data for state in states)

        places = session.scalars(
            select(TouristPlace).where(TouristPlace.is_seed_data.is_(True)),
        ).all()
        assert places
        assert all(SEED_MARKER in place.name for place in places)
        assert session.scalar(select(User).where(User.email == "demo.traveller@bharatyatra.local"))
        assert session.scalar(select(User).where(User.email == "demo.owner@example.com"))
        assert session.scalar(select(User).where(User.email == "demo.admin@example.com"))
        assert session.scalar(select(City).where(City.slug == "hyderabad"))
        assert session.scalar(select(PlaceCategory).where(PlaceCategory.slug == "temple"))

        second = seed_all(session, force=True)
        assert second["states"] == 0
        assert second["places"] == 0
        assert second["users"] == 0
    finally:
        session.close()
        engine.dispose()
