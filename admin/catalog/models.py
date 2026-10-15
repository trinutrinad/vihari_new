"""Unmanaged mirrors of FastAPI/SQLAlchemy tables (Phase 22).

Schema ownership stays with Alembic in `backend/`. These models are read/write
helpers for Django Admin only — never run `makemigrations` for them.
"""

from __future__ import annotations

import uuid

from django.db import models


class AppUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    full_name = models.CharField(max_length=160)
    primary_role = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    is_seed_data = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "users"
        verbose_name = "App user"
        verbose_name_plural = "App users"

    def __str__(self) -> str:
        return self.full_name


class TouristPlace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=220)
    is_featured = models.BooleanField(default=False)
    is_seed_data = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "tourist_places"
        verbose_name = "Tourist place"
        verbose_name_plural = "Tourist places"

    def __str__(self) -> str:
        return self.name


class Hotel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=220)
    starting_price_inr = models.IntegerField(null=True, blank=True)
    is_seed_data = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "hotels"

    def __str__(self) -> str:
        return self.name


class Restaurant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=220)
    is_seed_data = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "restaurants"

    def __str__(self) -> str:
        return self.name


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_number = models.CharField(max_length=40)
    resource_type = models.CharField(max_length=40)
    resource_id = models.UUIDField()
    status = models.CharField(max_length=32)
    amount_inr = models.IntegerField()
    currency = models.CharField(max_length=3, default="INR")
    user_id = models.UUIDField()
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "bookings"

    def __str__(self) -> str:
        return self.booking_number


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_number = models.CharField(max_length=40)
    amount_inr = models.IntegerField()
    status = models.CharField(max_length=32)
    method = models.CharField(max_length=32)
    user_id = models.UUIDField()
    booking_id = models.UUIDField(null=True, blank=True)
    is_mock = models.BooleanField(default=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "payments"

    def __str__(self) -> str:
        return self.payment_number


class SupportTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=40)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    status = models.CharField(max_length=32)
    priority = models.CharField(max_length=16)
    user_id = models.UUIDField()
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "support_tickets"

    def __str__(self) -> str:
        return self.ticket_number
