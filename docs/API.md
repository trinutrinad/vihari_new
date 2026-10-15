# API — Bharat Yatra

Base URL (local): `http://localhost:8000/api/v1`

All successful responses follow:

```json
{
  "success": true,
  "message": "OK",
  "data": {}
}
```

Error responses follow:

```json
{
  "success": false,
  "error": {
    "code": "not_found",
    "message": "Resource not found",
    "details": null
  }
}
```

## Implemented

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness/health check |
| GET | `/health/ready` | Readiness (DB required; Redis soft) |
| POST | `/auth/register` | Email/phone + password registration |
| POST | `/auth/login` | Password login |
| POST | `/auth/phone/request-otp` | Request phone OTP (mock provider) |
| POST | `/auth/phone/verify-otp` | Verify OTP and issue session |
| POST | `/auth/refresh` | Rotate refresh token |
| POST | `/auth/logout` | Revoke refresh token |
| POST | `/auth/forgot-password` | Start password reset |
| POST | `/auth/reset-password` | Complete password reset |
| GET | `/auth/me` | Current user profile |
| PATCH | `/auth/me/profile` | Update profile |
| GET | `/places` | Paginated place listing + filters |
| GET | `/places/categories` | Place categories |
| GET | `/places/nearby` | Nearby places by lat/lng |
| GET | `/places/saved` | Current user's saved places |
| GET | `/places/{id}` | Place details |
| GET | `/places/by-slug/{slug}` | Place details by slug |
| POST | `/places/{id}/save` | Save place |
| DELETE | `/places/{id}/save` | Unsave place |
| GET | `/search` | Global multi-entity search |
| GET | `/search/autocomplete` | Autocomplete suggestions |
| GET | `/search/trending` | Trending queries + featured places |
| GET | `/maps/pins` | Place pins inside map viewport bounds |
| GET | `/maps/cities` | City centers with coordinates for map jump |
| GET | `/trips` | List current user's trips |
| POST | `/trips` | Create trip (+ optional days/stops) |
| GET | `/trips/{id}` | Trip detail with itinerary + map points |
| PATCH | `/trips/{id}` | Update trip metadata/status |
| DELETE | `/trips/{id}` | Delete trip |
| POST | `/trips/{id}/days` | Add itinerary day |
| PATCH | `/trips/{id}/days/{day_id}` | Update day |
| DELETE | `/trips/{id}/days/{day_id}` | Remove day |
| POST | `/trips/{id}/days/{day_id}/places` | Add stop |
| DELETE | `/trips/{id}/days/{day_id}/places/{stop_id}` | Remove stop |
| POST | `/trips/{id}/share` | Create/return share code |
| GET | `/trips/shared/{share_code}` | Public shared trip (read-only) |
| POST | `/ai/plan-trip` | Mock AI itinerary (optional save as trip) |
| POST | `/ai/chat` | Mock travel assistant chat |
| GET | `/ai/agents` | Agent catalog (roles + status) |
| GET | `/hotels` | Paginated hotels + filters |
| GET | `/hotels/nearby` | Nearby hotels by lat/lng |
| GET | `/hotels/{id}` | Hotel details + rooms |
| GET | `/hotels/by-slug/{slug}` | Hotel details by slug |
| GET | `/restaurants` | Paginated restaurants + filters |
| GET | `/restaurants/nearby` | Nearby restaurants by lat/lng |
| GET | `/restaurants/{id}` | Restaurant details + menu |
| GET | `/restaurants/by-slug/{slug}` | Restaurant details by slug |
| GET | `/guides` | Paginated guides + filters |
| GET | `/guides/nearby` | Nearby guides by city lat/lng |
| GET | `/guides/{id}` | Guide details + upcoming availability |
| GET | `/transport` | Paginated transport options + filters |
| GET | `/transport/estimate` | Mock fare estimate by distance |
| GET | `/transport/by-code/{code}` | Transport option by code |
| GET | `/transport/{id}` | Transport option details |
| GET | `/activities` | Paginated activities + filters |
| GET | `/activities/nearby` | Nearby activities by lat/lng |
| GET | `/activities/{id}` | Activity details + safety notes |
| GET | `/activities/by-slug/{slug}` | Activity details by slug |
| GET | `/bookings` | List current user bookings (auth) |
| POST | `/bookings` | Create mock booking (auth) |
| GET | `/bookings/{id}` | Booking details (auth) |
| POST | `/bookings/{id}/cancel` | Cancel booking (auth) |
| GET | `/payments` | List payments (auth) |
| POST | `/payments` | Capture mock payment for booking (auth) |
| GET | `/payments/{id}` | Payment details (auth) |
| POST | `/payments/{id}/refund` | Mock refund (auth) |
| GET | `/wallet` | Demo wallet balance (auth) |
| POST | `/wallet/topup` | Mock wallet top-up (auth) |
| GET | `/coupons/{code}` | Lookup demo coupon |
| GET | `/reviews` | List visible reviews for a target |
| GET | `/reviews/me` | Current user reviews (auth) |
| POST | `/reviews` | Create/update review (auth, upsert) |
| GET | `/reviews/{id}` | Review details |
| PATCH | `/reviews/{id}` | Update own review (auth) |
| DELETE | `/reviews/{id}` | Hide own review (auth) |
| GET | `/safety/tips` | Safety tips (+ optional city) |
| GET | `/safety/emergency-numbers` | India emergency numbers |
| GET | `/safety/contacts` | Personal emergency contacts (auth) |
| POST | `/safety/contacts` | Add emergency contact (auth) |
| PATCH | `/safety/contacts/{id}` | Update contact (auth) |
| DELETE | `/safety/contacts/{id}` | Delete contact (auth) |
| POST | `/safety/sos` | Mock SOS support ticket (auth) |
| GET | `/notifications` | List in-app notifications (auth) |
| GET | `/notifications/unread-count` | Unread count (auth) |
| POST | `/notifications/demo` | Create demo notification (auth) |
| POST | `/notifications/read-all` | Mark all read (auth) |
| GET | `/notifications/{id}` | Notification details (auth) |
| POST | `/notifications/{id}/read` | Mark one read (auth) |
| GET | `/business/access` | Business access + property counts (auth) |
| GET | `/business/summary` | Owner KPIs (auth, business roles) |
| GET | `/business/properties` | Owned hotels/restaurants/guides (auth, business roles) |
| GET | `/business/bookings` | Bookings for owned resources (auth, business roles) |
| GET | `/admin/access` | Admin access check (auth) |
| GET | `/admin/summary` | Platform KPIs (auth, ADMIN) |
| GET | `/admin/users` | Recent users (auth, ADMIN) |
| GET | `/admin/bookings` | Recent bookings (auth, ADMIN) |
| GET | `/admin/payments` | Recent payments (auth, ADMIN) |
| GET | `/admin/tickets` | Support tickets (auth, ADMIN) |
| POST | `/rag/query` | Grounded RAG Q&A with sources |
| GET | `/rag/documents` | List knowledge documents |
| GET | `/rag/documents/{id}` | Knowledge document details |
| POST | `/rag/ingest` | Ingest/chunk/embed document (auth, ADMIN) |
| POST | `/rag/seed-demo` | Idempotent curated demo corpus |
| GET | `/ai/eval/cases` | List golden AI evaluation cases |
| POST | `/ai/eval/run` | Run eval suite (auth, ADMIN) |

### GET `/health`

Returns service status, environment, and version. Includes `X-Request-ID` header.

### GET `/health/ready`

Dependency readiness. Returns `200` when the database answers `SELECT 1`; `503` otherwise.
Redis is reported in `checks` but does not fail readiness by itself in MVP.

### Auth notes

- Passwords are bcrypt-hashed; never returned in API payloads.
- JWT access + refresh tokens; refresh tokens are hashed at rest and rotatable.
- Phone OTP uses `OtpProvider` abstraction (`MockOtpProvider` by default).
- RBAC via `require_roles(...)` dependency (`SUPER_ADMIN` bypasses checks).

## Planned (later phases)

- Optional: Redis-backed rate limits, live LLM vendors, pgvector

OpenAPI interactive docs (debug): http://localhost:8000/docs
