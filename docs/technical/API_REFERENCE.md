# Luceo API Reference

Base URL: `/api/v1`

## Authentication

All authenticated endpoints require `Authorization: Bearer <token>` header.

Token flow:
1. `POST /register` or `POST /login` returns `access_token` (1h) + `refresh_token` (30d)
2. Use `access_token` in `Authorization: Bearer <token>` header
3. When access token expires, call `POST /auth/refresh` with the refresh token
4. Each refresh rotates both tokens (old refresh token is revoked)

## Rate Limiting

All endpoints are rate-limited. Limits apply per user (JWT) or per IP (unauthenticated).

| Endpoint | Limit |
|---|---|
| `POST /auth/register`, `/login` | 5/minute |
| `POST /auth/refresh` | 10/minute |
| `POST /chat/.../messages` | 20/minute |
| `PUT /auth/password` | 5/minute |
| `DELETE /chat/.../conversations` | 20/minute |
| `POST /admin/cleanup-tokens` | 1/minute |
| Tracking, screening write endpoints | 60/minute |

Exceeding returns `429 Too Many Requests`.

---

## Auth (`/api/v1/auth`)

### POST /register
Create a new user account. Email is optional (anonymity feature).

**Auth:** None
**Body:**
```json
{
  "email": "user@example.com",  // optional
  "password": "min8chars",
  "display_name": "Karel",      // optional
  "gdpr_consent": true          // required
}
```

**Response (201):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "abc123...",
  "token_type": "bearer",
  "ai_disclaimer": "Luceo is an AI-powered wellness tool..."
}
```

**Errors:** 400 (no GDPR consent), 409 (email already registered)

### POST /login
**Auth:** None
**Body:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response (200):** Same as register.
**Errors:** 401 (invalid credentials)

### POST /refresh
Exchange a valid refresh token for new access + refresh tokens (rotation).

**Auth:** None
**Body:**
```json
{
  "refresh_token": "abc123..."
}
```

**Response (200):** Same as register.
**Errors:** 401 (invalid refresh token)

### POST /logout
Revoke a refresh token. Idempotent.

**Auth:** None
**Body:**
```json
{
  "refresh_token": "abc123..."
}
```

**Response:** 204 No Content

### GET /me
**Auth:** Required
**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "Karel",
  "created_at": "2026-04-05T10:00:00Z",
  "data_region": "eu-central"
}
```

### DELETE /me
GDPR Article 17 — right to erasure. Soft-deletes user and wipes PII.

**Auth:** Required
**Response:** 204 No Content

### PUT /password
Change password. Requires current password. Revokes all refresh tokens (forces re-login).

**Auth:** Required
**Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword8+"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully."
}
```

**Errors:** 401 (wrong current password), 400 (same password)

---

## Chat (`/api/v1/chat`)

### POST /conversations
Create a new conversation. Returns AI Act disclaimer.

**Auth:** Required
**Response (201):**
```json
{
  "id": "uuid",
  "started_at": "2026-04-05T10:00:00Z",
  "disclaimer": "Komunikuješ s AI asistentem Luceo..."
}
```

### POST /conversations/{conversation_id}/messages
Send a message and get AI response.

**Auth:** Required
**Body:**
```json
{
  "content": "Ahoj, dnes je to tezke..."
}
```

**Response (200):**
```json
{
  "message": "Slyším tě. Pověz mi víc...",
  "crisis_detected": false,
  "crisis_contacts": null,
  "disclaimer": null
}
```

**Crisis response (HIGH/CRITICAL):**
```json
{
  "message": "Rozumím, že procházíš velmi těžkým obdobím...",
  "crisis_detected": true,
  "crisis_contacts": [
    {"name": "Krizová pomoc", "phone": "116 123", ...}
  ],
  "disclaimer": null
}
```

### GET /conversations
List user's conversations (most recent first). Supports pagination.

**Auth:** Required
**Query:** `?skip=0&limit=50`
**Response (200):**
```json
[
  {"id": "uuid", "started_at": "2026-04-05T10:00:00Z"}
]
```

### DELETE /conversations/{conversation_id}
Delete a conversation and all its messages. Audit logged.

**Auth:** Required
**Response:** 204 No Content
**Errors:** 404 (not found or not owned)

---

## Screening (`/api/v1/screening`)

### GET /questionnaires/audit
Return the WHO AUDIT questionnaire (10 questions). No auth required (preview).

**Auth:** None
**Response (200):**
```json
{
  "questions": [
    {
      "number": 1,
      "text_cs": "Jak často piješ alkoholické nápoje?",
      "text_en": "How often do you have a drink containing alcohol?",
      "options": [
        {"text_cs": "Nikdy", "text_en": "Never", "value": 0},
        ...
      ]
    },
    ...
  ]
}
```

### POST /questionnaires/audit
Submit AUDIT answers (10 integers).

**Auth:** Required
**Body:**
```json
{
  "answers": [2, 1, 1, 0, 0, 0, 0, 0, 0, 0]
}
```

**Response (200):**
```json
{
  "total_score": 4,
  "risk_level": "low_risk",
  "recommendation": "Tvé odpovědi naznačují nízké riziko..."
}
```

**Risk levels:** `low_risk` (0-7), `hazardous` (8-15), `harmful` (16-19), `possible_dependence` (20-40)

### GET /results
Get screening history.

**Auth:** Required

---

## Tracking (`/api/v1/tracking`)

### POST /checkin
Daily sobriety check-in. Upserts for today's date.

**Auth:** Required
**Body:**
```json
{
  "is_sober": true,
  "mood": 4,           // 1-5, optional
  "energy_level": 3,   // 1-5, optional
  "notes": "Dobrý den" // optional, encrypted at rest
}
```

**Response (201):**
```json
{
  "date": "2026-04-05",
  "is_sober": true,
  "mood": 4,
  "streak": 7
}
```

### GET /checkin/today
Check if today has been logged.

**Auth:** Required

### POST /cravings
Log a craving event.

**Auth:** Required
**Body:**
```json
{
  "intensity": 7,
  "trigger_category": "stress",
  "trigger_notes": "Stresový den v práci",
  "coping_strategy_used": "procházka",
  "outcome": "resisted"
}
```

**trigger_category values:** `stress`, `social`, `emotional`, `habitual`, `environmental`, `other`
**outcome values:** `resisted`, `gave_in` (optional)

### GET /cravings
List craving history (last 100).

### GET /summary
Tracking summary for last N days.

**Auth:** Required
**Query:** `?days=30`
**Response (200):**
```json
{
  "sober_days": 25,
  "total_days": 30,
  "average_mood": 3.5,
  "total_cravings": 8,
  "top_trigger": "stress",
  "current_streak": 7
}
```

### GET /streak
Current sobriety streak (days).

---

## Crisis (`/api/v1/crisis`)

### GET /contacts
Public endpoint — no auth. Returns Czech crisis phone numbers.

**Auth:** None
**Response (200):**
```json
{
  "contacts": [
    {
      "name": "Krizová pomoc",
      "phone": "116 123",
      "description": "Linka první psychické pomoci",
      "available": "24/7",
      "url": "https://www.csspraha.cz"
    },
    ...
  ]
}
```

---

## Admin (`/api/v1/admin`)

### GET /export-my-data
GDPR Article 15 — right of access. Exports all user data as JSON.

**Auth:** Required
**Rate limit:** 5/minute
**Response:** Full JSON export of user profile, checkins, cravings, screenings, conversations (decrypted). Data is ordered chronologically.

### POST /cleanup-tokens
Remove expired and revoked refresh tokens from the database.

**Auth:** Required
**Rate limit:** 1/minute
**Response (200):**
```json
{
  "message": "Cleaned up 5 expired/revoked tokens."
}
```

---

## Health

### GET /health
**Auth:** None
**Response:**
```json
{
  "status": "ok",
  "version": "0.2.0",
  "database": "connected"
}
```

Status is `"degraded"` and database `"unavailable"` when DB is unreachable.
