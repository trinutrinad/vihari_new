# Security — Bharat Yatra

## Implemented

- Secrets via environment variables (`.env` gitignored; `.env.example` provided)
- CORS configuration from settings
- Request ID middleware for audit correlation
- No secrets in source code
- Bcrypt password hashing
- JWT access + refresh tokens (refresh tokens hashed in DB, revocable)
- Password reset tokens (hashed, single-use)
- OTP provider abstraction with mock SMS implementation
- OTP debug codes never exposed when `DEBUG=false`
- RBAC dependency (`require_roles`) for role-gated routes
- Global exception handlers that never leak stack traces
- Auth endpoint rate limiting (in-memory; Redis-backed later)
- Security response headers (`nosniff`, `DENY` frame, `no-store`, HSTS when not debug)
- Optional `TrustedHostMiddleware` via `TRUSTED_HOSTS`
- Production startup validation for weak `SECRET_KEY`
- Audit logging for privileged actions (RAG ingest, AI eval runs)
- Liveness `/health` + readiness `/health/ready` (DB required, Redis soft)

## Planned

- Redis-backed rate limits / token blacklist for access tokens
- Real SMS OTP providers (Twilio / MSG91)
- CSRF where cookie-based sessions are introduced
- WAF / edge rate limits at reverse proxy

## Reporting

Treat any leaked credentials as an incident — rotate immediately.
