"""API v1 router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    activities,
    admin,
    ai,
    ai_eval,
    auth,
    bookings,
    business,
    guides,
    health,
    hotels,
    maps,
    notifications,
    payments,
    places,
    rag,
    restaurants,
    reviews,
    safety,
    search,
    transport,
    trips,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(places.router, tags=["places"])
api_router.include_router(hotels.router, tags=["hotels"])
api_router.include_router(restaurants.router, tags=["restaurants"])
api_router.include_router(guides.router, tags=["guides"])
api_router.include_router(transport.router, tags=["transport"])
api_router.include_router(activities.router, tags=["activities"])
api_router.include_router(bookings.router, tags=["bookings"])
api_router.include_router(payments.router, tags=["payments"])
api_router.include_router(reviews.router, tags=["reviews"])
api_router.include_router(safety.router, tags=["safety"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(business.router, tags=["business"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(rag.router, tags=["rag"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(maps.router, tags=["maps"])
api_router.include_router(trips.router, tags=["trips"])
api_router.include_router(ai.router, tags=["ai"])
api_router.include_router(ai_eval.router, tags=["ai-eval"])
