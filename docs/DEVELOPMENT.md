# Development — Bharat Yatra

## Phase order

1. Project setup
2. Database + models
3. Authentication
4. Home UI
5. Tourist places
6. Search
7. Maps
8. Trip management
9. AI trip planner
10. AI agent architecture
11. Hotels
12. Restaurants
13. Guides
14. Transport
15. Activities
16. Bookings
17. Payments
18. Reviews
19. Safety
20. Notifications
21. Business dashboard
22. Admin dashboard
23. RAG
24. AI evaluation
25. Production hardening ← **current (complete)**

## Workflow per module

1. Inspect existing code
2. Reuse components/services
3. Implement one module completely
4. Run backend tests, frontend tests, lint, typecheck, build
5. Fix errors before continuing

## Commands

### Backend

```bash
cd backend
.\.venv\Scripts\activate   # Windows
pytest
ruff check app tests
alembic upgrade head
python -m app.scripts.seed
```

### Frontend

```bash
cd frontend
npm run lint
npm run test
npm run typecheck
npm run build
```

## Seed data

Realistic Indian tourism seed data is available from Phase 2 via `python -m app.scripts.seed`.
All demo entities are clearly marked `[SEED/DEMO]` / `is_seed_data=True` — not real businesses.
Official temple timings and fees are intentionally not fabricated.

Demo business owner (Phase 21): `demo.owner@example.com` / `DemoOwner1!`
Demo platform admin (Phase 22): `demo.admin@example.com` / `DemoAdmin1!`

Django Admin (deep CRUD) lives in `/admin` — see [admin/README.md](../admin/README.md).
