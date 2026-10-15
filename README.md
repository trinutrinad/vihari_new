# Bharat Yatra

**Discover. Plan. Travel. Experience India.**

AI-powered Indian tourism super app — discover places, plan trips, find transport, hotels, food, guides, book experiences, and get AI assistance.

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Zustand |
| Backend API | Python, FastAPI, SQLAlchemy, Alembic, Pydantic |
| Admin | Django Admin + FastAPI/React ops UI (same PostgreSQL; Phase 22) |
| Data | PostgreSQL, Redis |
| Jobs | Celery (when background work is required) |
| Maps | Leaflet + OpenStreetMap (provider-abstracted) |

## Repository layout

```
vihari/
├── frontend/          # React + Vite consumer app
├── backend/           # FastAPI API
├── admin/             # Django Admin (shared DB)
├── docs/              # Architecture & ops docs
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick start (local)

### Prerequisites

- Node.js 20+
- Python 3.12+
- Docker Desktop (for Postgres + Redis, or full stack)

### 1. Environment

```bash
cp .env.example .env
```

### 2. Infrastructure

```bash
docker compose up -d postgres redis
```

### 3. Backend

```bash
cd backend
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
python -m app.scripts.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs  
Health: http://localhost:8000/api/v1/health

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### Full stack with Docker

```bash
docker compose up --build
```

## Development phases

This project is built incrementally. **Current: Phase 25 — Production hardening complete.** MVP phase roadmap (1–25) finished.

See [DEVELOPMENT.md](./docs/DEVELOPMENT.md) for the full phase order.

## Documentation

- [ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- [API.md](./docs/API.md)
- [DATABASE.md](./docs/DATABASE.md)
- [AI_ARCHITECTURE.md](./docs/AI_ARCHITECTURE.md)
- [DEPLOYMENT.md](./docs/DEPLOYMENT.md)
- [DEVELOPMENT.md](./docs/DEVELOPMENT.md)
- [SECURITY.md](./docs/SECURITY.md)
- [ENVIRONMENT.md](./docs/ENVIRONMENT.md)

## License

Proprietary — All rights reserved.
