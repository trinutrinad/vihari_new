"""Domain enumerations persisted as strings."""

from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    GUIDE = "GUIDE"
    DRIVER = "DRIVER"
    HOTEL_OWNER = "HOTEL_OWNER"
    RESTAURANT_OWNER = "RESTAURANT_OWNER"
    TOUR_OPERATOR = "TOUR_OPERATOR"


class PlaceCategoryCode(StrEnum):
    TEMPLE = "temple"
    BEACH = "beach"
    MOUNTAIN = "mountain"
    WATERFALL = "waterfall"
    HISTORICAL = "historical"
    WILDLIFE = "wildlife"
    ADVENTURE = "adventure"
    FOOD = "food"
    HIDDEN_GEM = "hidden_gem"
    NATURE = "nature"
    CITY = "city"
    OTHER = "other"


class DataProvenance(StrEnum):
    """Distinguishes verified vs community vs AI-generated content."""

    OFFICIAL = "official"
    COMMUNITY = "community"
    SEED_DEMO = "seed_demo"
    AI_GENERATED = "ai_generated"
    UNVERIFIED = "unverified"


class BookingStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TripStatus(StrEnum):
    DRAFT = "draft"
    UPCOMING = "upcoming"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(StrEnum):
    UPI = "upi"
    CARD = "card"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    CASH = "cash"
    MOCK = "mock"


class RideStatus(StrEnum):
    SEARCHING = "searching"
    DRIVER_ASSIGNED = "driver_assigned"
    DRIVER_ARRIVING = "driver_arriving"
    STARTED = "started"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VehicleType(StrEnum):
    AUTO = "auto"
    TAXI = "taxi"
    BIKE = "bike"
    SCOOTER = "scooter"
    RENTAL_CAR = "rental_car"
    BUS = "bus"
    TRAIN = "train"
    AIRPORT_TRANSFER = "airport_transfer"
    OUTSTATION_CAB = "outstation_cab"


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"


class ReviewTargetType(StrEnum):
    PLACE = "place"
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    GUIDE = "guide"
    DRIVER = "driver"
    ACTIVITY = "activity"


class KnowledgeSourceType(StrEnum):
    GOVERNMENT = "government"
    OFFICIAL_TOURISM = "official_tourism"
    TEMPLE_OFFICIAL = "temple_official"
    CURATED = "curated"
    COMMUNITY = "community"
