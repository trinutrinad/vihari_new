# Django Admin — Bharat Yatra (Phase 22)

Shares the same PostgreSQL database as the FastAPI backend. Schema ownership
stays with Alembic (`backend/`). Catalog models here are `managed = False`.

## What this provides

- Classic Django Admin CRUD/browse for users, places, hotels, restaurants,
  bookings, payments, and support tickets
- Separate Django staff login (`auth_user` table) — not the FastAPI JWT users

The React/FastAPI **Admin dashboard** (`/admin` in the consumer app) is the
ops overview used day-to-day; this Django app is for deeper catalog edits.

## Setup

```bash
cd admin
python -m venv .venv
# Windows
.\.venv\Scripts\activate
pip install -r requirements.txt

# Ensure Postgres is up and backend migrations/seed have run.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
```

Open http://127.0.0.1:8001/

## Notes

- Never run `makemigrations` for `catalog` models.
- `DATABASE_URL` is read from the repo-root `.env` (SQLAlchemy-style URLs are OK).
- FastAPI demo admin for the React UI: `demo.admin@example.com` / `DemoAdmin1!`
