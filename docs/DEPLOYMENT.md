# Deployment — Bharat Yatra

## Local (recommended for development)

```bash
cp .env.example .env
docker compose up --build
```

Services:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs (debug only) |
| Postgres | localhost:5432 |
| Redis | localhost:6379 |
| Django Admin | http://127.0.0.1:8001 (optional; see `admin/`) |

## Production checklist

- Set `DEBUG=false`, `APP_ENV=production`
- Strong `SECRET_KEY` (32+ chars; never the example value)
- Restricted `CORS_ORIGINS`
- Set `OTP_DEBUG_EXPOSE_CODE=false`
- Set `TRUSTED_HOSTS` to your API hostnames (not `*`)
- Terminate TLS at reverse proxy (Nginx / Traefik / cloud LB)
- Managed PostgreSQL + Redis
- Probe **liveness** `GET /api/v1/health` and **readiness** `GET /api/v1/health/ready`
- Separate Celery workers when background jobs are enabled
- Secrets via vault / cloud secret manager — never bake into images
- OpenAPI `/docs` is disabled when `DEBUG=false`

## Health checks

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/health` | Liveness — process up |
| `GET /api/v1/health/ready` | Readiness — DB required; Redis soft/degraded OK |
