"""Django Admin registrations for shared-DB catalog models."""

from __future__ import annotations

from django.contrib import admin

from catalog.models import (
    AppUser,
    Booking,
    Hotel,
    Payment,
    Restaurant,
    SupportTicket,
    TouristPlace,
)


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "primary_role", "is_active", "is_seed_data")
    list_filter = ("primary_role", "is_active", "is_seed_data")
    search_fields = ("full_name", "email", "phone")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(TouristPlace)
class TouristPlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_featured", "is_seed_data")
    list_filter = ("is_featured", "is_seed_data")
    search_fields = ("name", "slug")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "starting_price_inr", "is_seed_data")
    list_filter = ("is_seed_data",)
    search_fields = ("name", "slug")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_seed_data")
    list_filter = ("is_seed_data",)
    search_fields = ("name", "slug")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("booking_number", "resource_type", "status", "amount_inr", "user_id")
    list_filter = ("status", "resource_type")
    search_fields = ("booking_number",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_number", "amount_inr", "status", "method", "is_mock")
    list_filter = ("status", "method", "is_mock")
    search_fields = ("payment_number",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("ticket_number", "subject", "status", "priority", "user_id")
    list_filter = ("status", "priority")
    search_fields = ("ticket_number", "subject")
    readonly_fields = ("id", "created_at", "updated_at")
