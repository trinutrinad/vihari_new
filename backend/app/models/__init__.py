"""SQLAlchemy models package.

Importing this package registers all models on Base.metadata for Alembic.
"""

from app.models.activity import Activity, ActivityBooking
from app.models.ai import AIConversation, AIMessage
from app.models.auth import OtpChallenge, PasswordResetToken, RefreshToken
from app.models.booking import Booking
from app.models.enums import (
    BookingStatus,
    DataProvenance,
    KnowledgeSourceType,
    NotificationChannel,
    PaymentMethod,
    PaymentStatus,
    PlaceCategoryCode,
    ReviewTargetType,
    RideStatus,
    TripStatus,
    UserRole,
    VehicleType,
)
from app.models.geo import City, State
from app.models.guide import Guide, GuideAvailability, GuideBooking
from app.models.hotel import Hotel, HotelReview, HotelRoom
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.models.notification import Notification
from app.models.payment import Coupon, Payment, Wallet
from app.models.place import (
    PlaceCategory,
    PlaceImage,
    PlaceReview,
    SavedPlace,
    TouristPlace,
)
from app.models.restaurant import FoodOrder, Restaurant, RestaurantMenuItem
from app.models.review import UserReview
from app.models.support import EmergencyContact, SupportTicket
from app.models.temple import Temple, TempleTiming
from app.models.transport import Driver, Ride, RideLocation, TransportOption, Vehicle
from app.models.trip import Trip, TripDay, TripPlace
from app.models.user import (
    Permission,
    Role,
    RolePermissionLink,
    User,
    UserProfile,
    UserRoleLink,
)

__all__ = [
    "Activity",
    "ActivityBooking",
    "AIConversation",
    "AIMessage",
    "Booking",
    "BookingStatus",
    "City",
    "Coupon",
    "DataProvenance",
    "Driver",
    "EmergencyContact",
    "FoodOrder",
    "Guide",
    "GuideAvailability",
    "GuideBooking",
    "Hotel",
    "HotelReview",
    "HotelRoom",
    "KnowledgeChunk",
    "KnowledgeDocument",
    "KnowledgeSourceType",
    "Notification",
    "NotificationChannel",
    "OtpChallenge",
    "PasswordResetToken",
    "Payment",
    "PaymentMethod",
    "PaymentStatus",
    "Permission",
    "PlaceCategory",
    "PlaceCategoryCode",
    "PlaceImage",
    "PlaceReview",
    "RefreshToken",
    "Restaurant",
    "RestaurantMenuItem",
    "ReviewTargetType",
    "Ride",
    "RideLocation",
    "RideStatus",
    "Role",
    "RolePermissionLink",
    "SavedPlace",
    "State",
    "SupportTicket",
    "Temple",
    "TempleTiming",
    "TouristPlace",
    "TransportOption",
    "Trip",
    "TripDay",
    "TripPlace",
    "TripStatus",
    "User",
    "UserProfile",
    "UserReview",
    "UserRole",
    "UserRoleLink",
    "Vehicle",
    "VehicleType",
    "Wallet",
]
