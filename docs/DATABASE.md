# Database — Bharat Yatra

## Engine

- PostgreSQL 16
- SQLAlchemy 2.x ORM
- Alembic migrations
- UUID primary keys (`UUIDPrimaryKeyMixin`)
- Timestamp mixins (`created_at` / `updated_at`)
- Soft-delete mixin on selected catalogs (places, hotels, restaurants, activities)
- PostGIS / pgvector deferred (lat/lng stored as `Numeric` for now; mock embeddings stored as JSON in `knowledge_chunks.embedding_ref`)

## Connection

Configured via `DATABASE_URL` (see [ENVIRONMENT.md](./ENVIRONMENT.md)).

Docker Compose service: `postgres` (healthy-gated before API starts).

## Migrations

```bash
cd backend
alembic upgrade head
```

Initial revision: `alembic/versions/20260812_0001_initial_schema.py` (46 tables).
Auth revision: `alembic/versions/20260812_0002_auth_tables.py` (refresh/OTP/reset tokens).

## Seed data

```bash
cd backend
python -m app.scripts.seed
```

Seed rows are clearly marked with `[SEED/DEMO]` names / `is_seed_data=True`.
Temple-related seed content uses `provenance=unverified` and does **not** invent official darshan timings.

## Tables (Phase 2)

users, user_profiles, roles, permissions, user_roles, role_permissions,
tourist_places, place_categories, place_images, place_reviews, states, cities,
temples, temple_timings, hotels, hotel_rooms, hotel_reviews, restaurants,
restaurant_menus, food_orders, guides, guide_availability, guide_bookings,
drivers, vehicles, rides, ride_locations, transport_options, activities,
activity_bookings, trips, trip_days, trip_places, bookings, payments, wallets,
coupons, notifications, saved_places, user_reviews, support_tickets,
emergency_contacts, ai_conversations, ai_messages, knowledge_documents,
knowledge_chunks

## Phase status

**Phase 2 complete:** models, Alembic bootstrap migration, and demo seed script.
Auth flows arrive in Phase 3.
