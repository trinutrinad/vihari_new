# Environment — Bharat Yatra

Copy `.env.example` → `.env` at the repo root.

| Variable | Purpose | Default (dev) |
|----------|---------|---------------|
| `APP_NAME` | Product name | Bharat Yatra |
| `APP_ENV` | Environment label | development |
| `DEBUG` | Verbose API / docs | true |
| `API_V1_PREFIX` | API mount path | /api/v1 |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | localhost:5173 |
| `SECRET_KEY` | JWT / crypto secret | change-me… |
| `DATABASE_URL` | SQLAlchemy URL | local Postgres |
| `REDIS_URL` | Cache / sessions | redis://localhost:6379/0 |
| `CELERY_BROKER_URL` | Task broker | Redis DB 1 |
| `VITE_API_BASE_URL` | Frontend API base | http://localhost:8000/api/v1 |
| `AI_PROVIDER` | AI backend | mock |
| `PAYMENT_PROVIDER` | Payments | mock |
| `OTP_PROVIDER` | OTP delivery | mock |
| `OTP_EXPIRE_MINUTES` | OTP lifetime | 10 |
| `OTP_DEBUG_EXPOSE_CODE` | Return OTP in API (dev only; forced off when `DEBUG=false`) | true |
| `RATE_LIMIT_ENABLED` | Enable auth endpoint rate limits | true |
| `RATE_LIMIT_AUTH_PER_MINUTE` | Auth requests per IP/path/minute | 30 |
| `SECURITY_HEADERS_ENABLED` | Send API security headers | true |
| `TRUSTED_HOSTS` | Allowed Host headers (`*` disables check) | * |

Frontend Vite vars must be prefixed with `VITE_` to be exposed to the browser.
