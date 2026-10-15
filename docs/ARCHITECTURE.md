# Architecture — Bharat Yatra

## Overview

Bharat Yatra is a modular tourism super app with:

- **Consumer frontend** (React + Vite)
- **Public/private API** (FastAPI)
- **Admin** (Django Admin + FastAPI/React ops dashboard — shared DB)
- **PostgreSQL** for transactional data
- **Redis** for cache, rate limits, and Celery broker
- **AI agent layer** with orchestrator + specialized tools (later phases)

## High-level diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │────▶│  FastAPI API │────▶│ PostgreSQL  │
│  (React)    │     │  /api/v1     │     └─────────────┘
└─────────────┘     │              │────▶┌─────────────┐
                    │  Agents/RAG  │     │    Redis    │
                    └──────────────┘     └─────────────┘
                            │
                    ┌───────▼────────┐
                    │ Django Admin   │
                    │ (same DB)      │
                    └────────────────┘
```

## Backend layering

```
api/           # HTTP routes only — no business logic
schemas/       # Pydantic request/response models
services/      # Business logic
repositories/  # Data access
models/        # SQLAlchemy ORM
agents/        # AI orchestrator + specialized agents
workers/       # Celery tasks
core/          # Config, security, database, exceptions
middleware/    # Request ID, rate limit, security headers
```

## Frontend layering

```
pages/         # Route-level screens
layouts/       # App / auth / onboarding shells
components/    # Shared UI primitives
features/      # Feature-scoped modules
hooks/         # Shared React hooks
services/      # API clients
store/         # Zustand stores
types/         # Shared TypeScript types
constants/     # Design tokens, routes, enums
utils/         # Pure helpers
```

## Provider abstractions

External systems are behind interfaces so mocks can ship in MVP:

- `PaymentProvider` → `MockPaymentProvider` (later Razorpay/Stripe/UPI)
- `MapProvider` → Leaflet/OSM (later Google/Mapbox)
- `AIProvider` → Mock (later LLM vendors)
- `NotificationProvider` → In-app (`InAppNotificationProvider`; later FCM/SMS/Email/WhatsApp)

## Current phase

**Phase 25 — Production hardening:** Auth rate limits, security headers, readiness probe, production secret validation, OTP debug guard, privileged audit logs, frontend error boundary + health readiness UI.

All planned build phases (1–25) are complete for the MVP roadmap.
