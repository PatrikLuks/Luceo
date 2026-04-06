# CONTEXT_architecture.md — As-Built Architecture Reference

> Generated 2026-04-06 · Luceo v0.1.0 · Session 6

---

## 1. Request Flow (as-built)

```
Client (React Native / httpx)
  │
  ▼
┌──────────────────────────── FastAPI app (src/main.py) ────────────────────────────┐
│  Middleware stack (outermost → innermost):                                         │
│    SecurityHeadersMiddleware → RequestLoggingMiddleware → SlowAPIMiddleware → CORS │
│                                                                                    │
│  Exception handlers:                                                               │
│    ValidationError → 422   SQLAlchemyError → 500   Exception → 500                │
│                                                                                    │
│  ┌─────────────────────── Router dispatch ──────────────────────┐                  │
│  │  /health                          → health()                 │                  │
│  │  /api/v1/auth/*                   → auth.router              │                  │
│  │  /api/v1/chat/*                   → chat.router              │                  │
│  │  /api/v1/screening/*              → screening.router         │                  │
│  │  /api/v1/tracking/*               → tracking.router          │                  │
│  │  /api/v1/crisis/*                 → crisis.router            │                  │
│  │  /api/v1/admin/*                  → admin.router             │                  │
│  └──────────────────────────────────────────────────────────────┘                  │
└───────────────────────────────────────────────────────────────────────────────────┘
  │
  ▼
┌─ Dependencies ─┐
│ get_db()        │ → AsyncSession (pool_size=5, max_overflow=10, pool_pre_ping=True)
│ get_current_user│ → Bearer JWT → decode → DB lookup → User (is_active check)
│ limiter         │ → _key_func: JWT sub or IP fallback
└─────────────────┘
```

### Actual function call chain for each endpoint family

**POST /api/v1/auth/register**
```
register()
  → hash_password(req.password)           # argon2-cffi
  → db.add(User) → db.commit()
  → create_access_token({"sub": user.id}) # jose HS256
  → create_refresh_token(user.id, db)     # secrets.token_urlsafe(64) → SHA-256 hash stored
  → log_audit_event(db, "user_register")
  → db.commit()
  → TokenResponse
```

**POST /api/v1/auth/login**
```
login()
  → select(User).where(email, is_active)
  → verify_password(req.password, hash)   # argon2 primary, bcrypt $2b$ fallback
  → create_access_token + create_refresh_token
  → log_audit_event(db, "user_login")
  → TokenResponse
```

**POST /api/v1/auth/refresh**
```
refresh_tokens()
  → verify_refresh_token(body.refresh_token, db)  # SHA-256 lookup, check revoked_at/expires_at
  → revoke_refresh_token(old_entry)                # soft-delete: set revoked_at
  → create_access_token + create_refresh_token     # rotation: new pair
  → TokenResponse
```

**POST /api/v1/chat/conversations/{id}/messages**
```
send_message()
  → verify conversation ownership (user_id check)
  → process_message(user_id, conversation_id, content, db)
      ├─ 1. detect_crisis(content)                 # normalize → regex tiers
      │     → normalize_text(msg)                   # NFKD, strip zero-width, collapse WS
      │     → check _COMPILED_CRITICAL patterns
      │     → check _COMPILED_HIGH patterns
      │     → check _COMPILED_MEDIUM patterns
      │     → CrisisResult(level, keywords, action, contacts)
      │
      ├─ 2. Store user message (encrypt_field → AES-256-GCM)
      │
      ├─ [if CRITICAL/HIGH] → get_crisis_response() (predefined, NO LLM) → return
      │
      ├─ 3. Load conversation history (last 20 messages, decrypted)
      │
      ├─ 4. RAG: retrieve_context(content, db)
      │     → ilike keyword search (MVP fallback)
      │     → fallback: most recent docs
      │     → format_context(docs) → "KONTEXT Z KLINICKÉ DATABÁZE: ..."
      │
      ├─ 5. Build system prompt (LUCEO_SYSTEM_PROMPT + rag_context + user_context)
      │
      ├─ 6. generate_response(system_prompt, messages)
      │     → AsyncAnthropic.messages.create(model="claude-sonnet-4-20250514")
      │     → returns (text, token_count)
      │     → on error: Czech fallback with crisis number
      │
      ├─ 7. check_response_guardrails(response_text)
      │     → _normalize_text() (NFKD, strip combining marks)
      │     → check _COMPILED_DIAGNOSTIC (ICD-10, diagnostic language)
      │     → check _COMPILED_MEDICATION (drug names, dosages)
      │     → if unsafe: replace with SAFE_FALLBACK
      │
      ├─ 8. [if MEDIUM] → append crisis resources to response
      │
      ├─ 9. Disclaimer reminder every 10 messages
      │
      └─ 10. Store assistant message (encrypted), audit log → commit
  → ChatResponse
```

**POST /api/v1/tracking/checkin**
```
daily_checkin()
  → select existing checkin for today (upsert logic)
  → encrypt_field(body.notes) if present
  → update existing OR create new SobrietyCheckin
  → log_audit_event("checkin_logged")
  → get_sobriety_streak() → count consecutive sober days backward
  → CheckinResponse
```

**POST /api/v1/screening/questionnaires/audit**
```
submit_audit()
  → validate each answer against AUDIT_QUESTIONS[i].options valid values
  → score_audit(body.answers)  # sum + risk bracket lookup
  → store ScreeningResult
  → log_audit_event("audit_completed")
  → AuditResultResponse
```

**DELETE /api/v1/auth/me** (GDPR erasure)
```
delete_me()
  → delete Messages → Conversations → ScreeningResults
  → delete SobrietyCheckins → CravingEvents → AuditLogs → RefreshTokens
  → log_audit_event("gdpr_deletion")
  → wipe User PII: email=None, display_name=None, password_hash="!"
  → is_active=False, deleted_at=now
```

---

## 2. Database Schema

### Table: `users`
| Column                | Type              | Constraints                       |
|-----------------------|-------------------|-----------------------------------|
| id                    | UUID(PK)          | default uuid4                     |
| created_at            | DateTime(tz)      | server_default now()              |
| updated_at            | DateTime(tz)      | server_default now(), onupdate    |
| email                 | String(255)       | UNIQUE, nullable, indexed         |
| password_hash         | String(255)       | NOT NULL                          |
| gdpr_consent_at       | DateTime(tz)      | nullable                          |
| gdpr_consent_version  | String(20)        | nullable                          |
| data_region           | String(20)        | default "eu-central"              |
| display_name          | String(100)       | nullable                          |
| is_active             | Boolean           | default True                      |
| deleted_at            | DateTime(tz)      | nullable                          |

### Table: `conversations`
| Column              | Type            | Constraints                              |
|---------------------|-----------------|------------------------------------------|
| id                  | UUID(PK)        | default uuid4                            |
| created_at          | DateTime(tz)    | server_default now()                     |
| updated_at          | DateTime(tz)    | server_default now(), onupdate           |
| user_id             | UUID(FK→users)  | NOT NULL, indexed, ON DELETE CASCADE     |
| started_at          | DateTime(tz)    | server_default now()                     |
| ended_at            | DateTime(tz)    | nullable                                 |
| disclaimer_shown    | Boolean         | default False                            |

**Relationships:** `messages` → Message (cascade all, delete-orphan, passive_deletes)

### Table: `messages`
| Column              | Type              | Constraints                                |
|---------------------|-------------------|--------------------------------------------|
| id                  | UUID(PK)          | default uuid4                              |
| created_at          | DateTime(tz)      | server_default now()                       |
| updated_at          | DateTime(tz)      | server_default now(), onupdate             |
| conversation_id     | UUID(FK→conversations) | NOT NULL, indexed, ON DELETE CASCADE  |
| role                | String(20)        | "user", "assistant", "system"              |
| content_encrypted   | Text              | AES-256-GCM encrypted                     |
| crisis_level        | String(20)        | nullable                                   |
| token_count         | Integer           | nullable                                   |

### Table: `sobriety_checkins`
| Column              | Type            | Constraints                              |
|---------------------|-----------------|------------------------------------------|
| id                  | UUID(PK)        | default uuid4                            |
| created_at          | DateTime(tz)    | server_default now()                     |
| updated_at          | DateTime(tz)    | server_default now(), onupdate           |
| user_id             | UUID(FK→users)  | NOT NULL, indexed, ON DELETE CASCADE     |
| date                | Date            | NOT NULL                                 |
| is_sober            | Boolean         | NOT NULL                                 |
| mood                | Integer         | nullable, CHECK(1-5)                     |
| energy_level        | Integer         | nullable, CHECK(1-5)                     |
| notes_encrypted     | Text            | nullable, AES-256-GCM                   |

**Constraints:** UNIQUE(user_id, date), CHECK mood 1-5, CHECK energy_level 1-5

### Table: `craving_events`
| Column                    | Type            | Constraints                          |
|---------------------------|-----------------|--------------------------------------|
| id                        | UUID(PK)        | default uuid4                        |
| created_at                | DateTime(tz)    | server_default now()                 |
| updated_at                | DateTime(tz)    | server_default now(), onupdate       |
| user_id                   | UUID(FK→users)  | NOT NULL, indexed, ON DELETE CASCADE |
| intensity                 | Integer         | NOT NULL, CHECK(1-10)                |
| trigger_category          | String(30)      | enum: stress/social/emotional/habitual/environmental/other |
| trigger_notes_encrypted   | Text            | nullable, AES-256-GCM                |
| coping_strategy_used      | String(200)     | nullable                             |
| outcome                   | String(20)      | nullable: "resisted" / "gave_in"     |

**Constraints:** CHECK intensity 1-10

### Table: `screening_results`
| Column              | Type            | Constraints                              |
|---------------------|-----------------|------------------------------------------|
| id                  | UUID(PK)        | default uuid4                            |
| created_at          | DateTime(tz)    | server_default now()                     |
| updated_at          | DateTime(tz)    | server_default now(), onupdate           |
| user_id             | UUID(FK→users)  | NOT NULL, indexed, ON DELETE CASCADE     |
| questionnaire_type  | String(20)      | default "AUDIT"                          |
| answers             | JSON            | raw answer data                          |
| total_score         | Integer         | NOT NULL                                 |
| risk_level          | String(30)      | NOT NULL                                 |
| completed_at        | DateTime(tz)    | server_default now()                     |

### Table: `knowledge_documents`
| Column              | Type            | Constraints                              |
|---------------------|-----------------|------------------------------------------|
| id                  | UUID(PK)        | default uuid4                            |
| created_at          | DateTime(tz)    | server_default now()                     |
| updated_at          | DateTime(tz)    | server_default now(), onupdate           |
| title               | String(500)     | NOT NULL                                 |
| content             | Text            | NOT NULL                                 |
| source              | String(100)     | NOT NULL                                 |
| category            | String(50)      | indexed                                  |
| embedding           | Vector(1024)    | nullable (pgvector, optional import)     |
| verified_by         | String(200)     | nullable                                 |
| verified_at         | DateTime(tz)    | nullable                                 |

### Table: `audit_logs`
| Column    | Type            | Constraints                                |
|-----------|-----------------|--------------------------------------------|
| id        | UUID(PK)        | default uuid4                              |
| created_at| DateTime(tz)    | server_default now()                       |
| updated_at| DateTime(tz)    | server_default now(), onupdate             |
| user_id   | UUID(FK→users)  | nullable, indexed, ON DELETE SET NULL       |
| action    | String(50)      | indexed (e.g. "chat_message", "login")     |
| details   | JSON            | nullable                                    |
| ip_hash   | String(64)      | nullable, SHA-256 of IP (GDPR)             |

### Table: `refresh_tokens`
| Column     | Type            | Constraints                              |
|------------|-----------------|------------------------------------------|
| id         | UUID(PK)        | default uuid4                            |
| created_at | DateTime(tz)    | server_default now()                     |
| updated_at | DateTime(tz)    | server_default now(), onupdate           |
| user_id    | UUID(FK→users)  | NOT NULL, indexed, ON DELETE CASCADE     |
| token_hash | String(64)      | UNIQUE (SHA-256 of raw token)            |
| expires_at | DateTime(tz)    | NOT NULL                                 |
| revoked_at | DateTime(tz)    | nullable (soft-delete for revocation)    |

### FK Cascade Summary
| Parent → Child                | ON DELETE    |
|-------------------------------|--------------|
| users → conversations         | CASCADE      |
| users → sobriety_checkins     | CASCADE      |
| users → craving_events        | CASCADE      |
| users → screening_results     | CASCADE      |
| users → refresh_tokens        | CASCADE      |
| users → audit_logs            | SET NULL     |
| conversations → messages      | CASCADE      |

---

## 3. Auth Flow — JWT + Refresh Token Lifecycle

```
┌─────────── Registration / Login ─────────────┐
│                                                │
│  Client sends credentials                      │
│  Server:                                       │
│    1. Verify password (argon2 / bcrypt legacy) │
│    2. Generate access token (JWT HS256, 1h)    │
│       payload: { sub: user_uuid, exp: +1h }    │
│    3. Generate refresh token:                  │
│       raw = secrets.token_urlsafe(64)          │
│       store SHA-256(raw) in DB                 │
│       expires: now + 30 days                   │
│    4. Return both tokens to client             │
│                                                │
└────────────────────────────────────────────────┘

┌─────────── Token Refresh (Rotation) ──────────┐
│                                                │
│  Client sends: POST /api/v1/auth/refresh       │
│    body: { refresh_token: "<raw_token>" }      │
│  Server:                                       │
│    1. SHA-256(raw) → lookup in DB              │
│    2. Check: not revoked, not expired          │
│    3. Revoke old token (set revoked_at)        │
│    4. Issue NEW access + refresh pair           │
│    5. Return both to client                    │
│                                                │
│  NOTE: Old refresh token is single-use         │
│                                                │
└────────────────────────────────────────────────┘

┌─────────── Protected Request ─────────────────┐
│                                                │
│  Client sends: Authorization: Bearer <jwt>     │
│  get_current_user() dependency:                │
│    1. decode_access_token(jwt)                 │
│    2. Extract sub → UUID                       │
│    3. DB lookup: User where id=uuid            │
│    4. Check is_active == True                  │
│    5. Return User ORM instance                 │
│                                                │
└────────────────────────────────────────────────┘

┌─────────── Logout ────────────────────────────┐
│                                                │
│  POST /api/v1/auth/logout                      │
│    body: { refresh_token: "<raw_token>" }      │
│  Revokes refresh token. Idempotent.            │
│  Access token remains valid until expiry (1h). │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 4. Chat Pipeline

```
User message
  │
  ▼
[1] CRISIS DETECTION (src/core/crisis.py)
  │  normalize_text() → strip diacritics, zero-width chars, lowercase
  │  Check regex tiers: CRITICAL → HIGH → MEDIUM → NONE
  │  Returns CrisisResult(level, matched_keywords, action, contacts)
  │
  ├── CRITICAL / HIGH → Predefined response (get_crisis_response)
  │                      NO LLM call, store encrypted, return immediately
  │
  ▼
[2] STORE USER MESSAGE (AES-256-GCM encrypted)
  │
  ▼
[3] LOAD HISTORY (last 20 messages, decrypt each)
  │
  ▼
[4] RAG RETRIEVAL (src/services/rag.py)
  │  MVP: ilike keyword search on knowledge_documents
  │  Fallback: most recent docs by created_at
  │  format_context() → "KONTEXT Z KLINICKÉ DATABÁZE: ..."
  │  Graceful degradation: on error, continue with empty context
  │
  ▼
[5] BUILD SYSTEM PROMPT
  │  LUCEO_SYSTEM_PROMPT template with {rag_context}, {user_context}
  │  user_context: TODO (sobriety streak, mood data)
  │
  ▼
[6] CLAUDE API CALL (src/services/anthropic_client.py)
  │  Model: claude-sonnet-4-20250514
  │  max_tokens: 1024
  │  Lazy singleton AsyncAnthropic client
  │  On error: Czech fallback message with crisis number
  │
  ▼
[7] OUTPUT GUARDRAILS (src/core/guardrails.py)
  │  _normalize_text() → NFKD, strip combining marks, lowercase
  │  Check: ICD-10 codes, diagnostic language, medication names, dosages
  │  If unsafe → replace with SAFE_FALLBACK
  │
  ▼
[8] APPEND CRISIS RESOURCES (if MEDIUM level)
  │
  ▼
[9] DISCLAIMER REMINDER (every 10 messages)
  │
  ▼
[10] STORE ASSISTANT MESSAGE (encrypted) + AUDIT LOG → commit
  │
  ▼
ChatResponse { message, crisis_detected, crisis_contacts, disclaimer }
```

---

## 5. .env.example

```bash
# Luceo environment variables
# Copy to .env and fill in real values. NEVER commit .env to git.

# === API Keys ===
ANTHROPIC_API_KEY=sk-ant-...

# === App Config ===
APP_ENV=development          # development | production
APP_PORT=8000
APP_HOST=0.0.0.0
LOG_LEVEL=info               # debug | info | warning | error

# === Database ===
POSTGRES_USER=luceo
POSTGRES_PASSWORD=changeme   # ⚠ MUST change for production
POSTGRES_DB=luceo
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# === Auth / JWT ===
JWT_SECRET=changeme-generate-a-real-secret   # ⚠ min 32 chars in production
JWT_EXPIRATION_HOURS=1                        # Access token TTL
REFRESH_TOKEN_EXPIRY_DAYS=30                  # Refresh token TTL

# === GDPR / Privacy ===
DATA_REGION=eu-central                        # EU hosting mandatory
ENCRYPTION_KEY=changeme-generate-a-real-key   # ⚠ 64-char hex in production (AES-256)

# === CORS (production only) ===
CORS_ALLOWED_ORIGINS=https://luceo.app        # Comma-separated origins
```

### Production validation (`validate_production_settings()`):
- `jwt_secret`: must NOT start with "changeme", min 32 chars
- `encryption_key`: must NOT start with "changeme", min 64 chars
- `anthropic_api_key`: must be non-empty
- `postgres_password`: must NOT start with "changeme"

---

## 6. Middleware Stack (order matters)

Applied outermost → innermost (last added = first to execute):

1. **SecurityHeadersMiddleware** — CSP, HSTS (prod only), X-Frame-Options, Permissions-Policy
2. **RequestLoggingMiddleware** — method, path, status, duration_ms (no body — GDPR)
3. **SlowAPIMiddleware** — rate limiting enforcement
4. **CORSMiddleware** — dev: localhost:3000/8081, prod: from CORS_ALLOWED_ORIGINS

### Rate Limiting Rules
| Endpoint                            | Limit       |
|-------------------------------------|-------------|
| POST /api/v1/auth/register          | 5/minute    |
| POST /api/v1/auth/login             | 5/minute    |
| POST /api/v1/auth/refresh           | 10/minute   |
| POST /api/v1/chat/…/messages        | 20/minute   |
| POST /api/v1/screening/…/audit      | 60/minute   |
| POST /api/v1/tracking/checkin       | 60/minute   |
| POST /api/v1/tracking/cravings      | 60/minute   |
| GET  /api/v1/admin/export-my-data   | 5/minute    |

Key function: JWT `sub` claim → `user:<uuid>` or IP fallback → `ip:<addr>`

---

## 7. Endpoint Summary (21 total)

| Method | Path | Auth | Rate Limited | Response Model |
|--------|------|------|-------------|----------------|
| GET | /health | No | No | `{"status","version"}` |
| POST | /api/v1/auth/register | No | 5/min | TokenResponse |
| POST | /api/v1/auth/login | No | 5/min | TokenResponse |
| GET | /api/v1/auth/me | Yes | No | UserResponse |
| DELETE | /api/v1/auth/me | Yes | No | 204 |
| POST | /api/v1/auth/refresh | No | 10/min | TokenResponse |
| POST | /api/v1/auth/logout | No | No | 204 |
| POST | /api/v1/chat/conversations | Yes | No | ConversationResponse |
| POST | /api/v1/chat/conversations/{id}/messages | Yes | 20/min | ChatResponse |
| GET | /api/v1/chat/conversations | Yes | No | list[ConversationListItem] |
| GET | /api/v1/screening/questionnaires/audit | No | No | AuditQuestionsResponse |
| POST | /api/v1/screening/questionnaires/audit | Yes | 60/min | AuditResultResponse |
| GET | /api/v1/screening/results | Yes | No | list[ScreeningResultItem] |
| POST | /api/v1/tracking/checkin | Yes | 60/min | CheckinResponse |
| GET | /api/v1/tracking/checkin/today | Yes | No | TodayCheckinResponse |
| POST | /api/v1/tracking/cravings | Yes | 60/min | CravingResponse |
| GET | /api/v1/tracking/cravings | Yes | No | list[CravingListItem] |
| GET | /api/v1/tracking/summary | Yes | No | TrackingSummary |
| GET | /api/v1/tracking/streak | Yes | No | StreakResponse |
| GET | /api/v1/crisis/contacts | No | No | CrisisContactsResponse |
| GET | /api/v1/admin/export-my-data | Yes | 5/min | GDPRExportResponse |
