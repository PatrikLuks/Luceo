# CONTEXT_status.md — Full Codebase Status Report

> Generated 2026-04-06 · Luceo v0.1.0 · 135 tests pass · Session 6

---

## 1. Every File in src/ — Purpose, Key Functions, TODOs/Debt

### src/main.py (99 lines)
**Purpose:** FastAPI application entry point — lifespan, middleware stack, exception handlers, health endpoint.
**Key functions:**
- `lifespan()` — validates production settings, sets up logging, disposes engine on shutdown
- `health()` — `GET /health` → `{"status": "ok", "version": "0.1.0"}`
- Exception handlers: `ValidationError` → 422, `SQLAlchemyError` → 500, `Exception` → 500
**Debt:** None identified.

### src/core/config.py (72 lines)
**Purpose:** Pydantic-settings configuration (env file + env vars).
**Key functions:**
- `Settings` — all config fields with dev defaults
- `database_url` / `database_url_sync` — async/sync URL properties
- `validate_production_settings()` — rejects weak secrets in non-dev envs
**Debt:** None.

### src/core/security.py (136 lines)
**Purpose:** JWT, password hashing (argon2 + bcrypt legacy), refresh tokens, AES-256-GCM encryption.
**Key functions:**
- `hash_password()`, `verify_password()` — argon2 primary, passlib/bcrypt `$2b$` fallback
- `create_access_token()`, `decode_access_token()` — HS256 via python-jose
- `create_refresh_token()`, `verify_refresh_token()`, `revoke_refresh_token()` — SHA-256 hash, DB lookup
- `encrypt_field()`, `decrypt_field()` — AES-256-GCM, hex(nonce + ciphertext)
- `_get_aes_key()` — SHA-256 padding for short dev keys
**Debt:**
- `_get_aes_key()` silently pads short keys — could mask dev misconfigurations
- passlib DeprecationWarning on bcrypt detection (Python 3.13 removes `crypt`)
- Remove passlib dependency once all legacy bcrypt hashes are migrated to argon2

### src/core/crisis.py (194 lines) — SAFETY-CRITICAL
**Purpose:** Pre-LLM crisis detection using regex pattern matching on normalized text.
**Key functions:**
- `normalize_text()` — NFKD, strip zero-width chars, collapse whitespace
- `detect_crisis()` — CRITICAL → HIGH → MEDIUM → NONE tier matching
- `get_crisis_response()` — predefined Czech responses with phone numbers
**Debt:**
- Requires clinical advisor review before production deployment
- Only Czech + basic English patterns — no Slovak, no contextual analysis
- No negation handling ("nechci se zabít" = "I don't want to kill myself" → still triggers CRITICAL)

### src/core/crisis_contacts.py (59 lines)
**Purpose:** Hardcoded Czech crisis phone numbers (zero deps, zero failures).
**Key entities:** `CrisisContact` (Pydantic), `CZECH_CRISIS_CONTACTS` (6 contacts).
**Debt:** Phone numbers need periodic verification (can change).

### src/core/guardrails.py (66 lines) — SAFETY-CRITICAL
**Purpose:** Post-LLM output filter — blocks diagnoses, medication names, dosages.
**Key functions:**
- `_normalize_text()` — NFKD, strip combining marks (Mn category), lowercase
- `check_response_guardrails()` → `(is_safe: bool, reason: str | None)`
- `SAFE_FALLBACK` — safe replacement text
**Debt:**
- Requires clinical advisor review
- Normalization differs from `crisis.py` (uses `unicodedata.category != "Mn"` vs `unicodedata.combining`)
  — functionally equivalent but inconsistent
- No English-language diagnostic patterns (only Czech + medication names)

### src/core/prompts.py (34 lines)
**Purpose:** System prompt, AI disclaimer, periodic disclaimer reminder.
**Key entities:** `LUCEO_SYSTEM_PROMPT` (7 rules), `AI_DISCLAIMER`, `DISCLAIMER_REMINDER`.
**Debt:**
- `{rag_context}` and `{user_context}` placeholders use string `.replace()` — could break if RAG content
  contains these exact strings (unlikely but not impossible)

### src/core/audit.py (33 lines)
**Purpose:** GDPR/AI Act audit trail — logs events with hashed IP.
**Key functions:** `log_audit_event()` — SHA-256 hashes IP, adds AuditLog, caller commits.
**Debt:** None.

### src/core/database.py (16 lines)
**Purpose:** AsyncEngine + session factory creation.
**Key entities:** `engine`, `async_session_maker`, `get_db()` dependency.
**Debt:** None.

### src/core/deps.py (40 lines)
**Purpose:** `get_current_user` FastAPI dependency — JWT → user lookup.
**Debt:** None.

### src/core/middleware.py (48 lines)
**Purpose:** Request logging (no body for GDPR) + security headers (CSP, HSTS, X-Frame-Options).
**Debt:** None.

### src/core/rate_limit.py (26 lines)
**Purpose:** Slowapi rate limiter with JWT user_id or IP fallback key function.
**Debt:** In-memory storage — will lose state on restart. Need Redis for production.

### src/services/chat.py (159 lines) — CORE PRODUCT LOGIC
**Purpose:** Chat orchestration — crisis → RAG → LLM → guardrails → store.
**Key functions:** `process_message()` — 10-step pipeline.
**Debt:**
- `user_context` is hardcoded `""` — TODO: inject sobriety streak, mood data into prompt
- Uses `.replace()` for template substitution (see prompts.py note)
- Decryption failures silently replaced with `"[encrypted message]"` — no alerting

### src/services/anthropic_client.py (51 lines)
**Purpose:** Thin Claude API wrapper with lazy singleton and error fallback.
**Key functions:** `_get_client()`, `generate_response()`.
**Debt:**
- Model hardcoded as `"claude-sonnet-4-20250514"` — should be configurable
- Error fallback is a Czech string — no i18n
- No retry logic for transient API failures

### src/services/rag.py (54 lines)
**Purpose:** Knowledge base retrieval — MVP keyword search with pgvector placeholder.
**Key functions:** `retrieve_context()`, `format_context()`.
**Debt:**
- **Major:** No embedding-based search — using ilike keyword fallback (MVP)
- TODO in code: "Replace with proper embedding-based search when embedding service is ready"
- Fallback returns most recent docs regardless of relevance

### src/services/screening.py (191 lines)
**Purpose:** WHO AUDIT questionnaire (10 questions, 4 risk levels, CS/EN bilingual).
**Key functions:** `score_audit()`, `AUDIT_QUESTIONS` data.
**Debt:**
- `score_audit()` doesn't validate per-answer values (validation is in API layer)
- Long translated strings trigger ruff line-length warnings

### src/services/tracking.py (107 lines)
**Purpose:** Sobriety streak calculation (backward from today), aggregate summary (SQL).
**Key functions:** `get_sobriety_streak()`, `get_tracking_summary()`.
**Debt:** None significant.

### src/models/base.py (25 lines)
**Purpose:** Abstract base — UUID PK, created_at, updated_at with server_default.
**Debt:** None.

### src/models/user.py (27 lines)
**Purpose:** User model — optional email, GDPR consent tracking, soft delete.
**Debt:** None.

### src/models/conversation.py (44 lines)
**Purpose:** Conversation + Message models with encrypted content.
**Debt:** None.

### src/models/tracking.py (59 lines)
**Purpose:** SobrietyCheckin + CravingEvent with check constraints.
**Debt:** None.

### src/models/screening.py (24 lines)
**Purpose:** ScreeningResult model (JSON answers, score, risk level).
**Debt:** None.

### src/models/knowledge_base.py (32 lines)
**Purpose:** KnowledgeDocument with optional pgvector embedding.
**Debt:** Optional `Vector` import — conditional column definition (works for SQLite tests).

### src/models/audit_log.py (21 lines)
**Purpose:** Audit trail — FK to users with ON DELETE SET NULL (preserves log after user deletion).
**Debt:** None.

### src/models/refresh_token.py (24 lines)
**Purpose:** Refresh token model — SHA-256 hash, expiry, soft revocation.
**Debt:** None.

### src/api/router.py (11 lines)
**Purpose:** Aggregates all 6 routers into `all_routers` list.

### src/api/auth.py (194 lines)
**Purpose:** Auth endpoints — register, login, me, delete-me (GDPR), refresh, logout.
**Debt:**
- Register: 2 commits (user creation + audit log) instead of atomic single commit
- Login timing attack mitigation: uses a dummy bcrypt hash (`$2b$12$LJ3m4ys...`) — this may fail
  with argon2 if the dummy hash is always a bcrypt hash (timing could differ between hash types)
- Anonymous users cannot re-authenticate after token loss (no recovery mechanism)

### src/api/chat.py (95 lines)
**Purpose:** Chat endpoints — create conversation, send message, list conversations.
**Debt:** None.

### src/api/screening.py (97 lines)
**Purpose:** AUDIT questionnaire — get questions (public), submit (auth), results history.
**Debt:** None.

### src/api/tracking.py (171 lines)
**Purpose:** Tracking endpoints — checkin (upsert), today's status, cravings CRUD, summary, streak.
**Debt:** None.

### src/api/crisis.py (13 lines)
**Purpose:** Crisis contacts endpoint — public, no auth required.
**Debt:** None.

### src/api/admin.py (122 lines)
**Purpose:** GDPR Article 15 data export — decrypts all user data to JSON.
**Debt:** None.

### src/api/schemas/ (6 files, ~300 lines total)
**Purpose:** Pydantic request/response models for all endpoints.
- `auth.py` — RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
- `chat.py` — SendMessageRequest, ChatResponse, ConversationResponse, ConversationListItem
- `crisis.py` — CrisisContactsResponse
- `screening.py` — AuditSubmission, AuditResultResponse, AuditQuestionsResponse, ScreeningResultItem
- `tracking.py` — CheckinRequest/Response, CravingRequest/Response, TrackingSummary, StreakResponse
- `admin.py` — GDPRExportResponse and sub-models
**Debt:** `PaginatedResponse` in tracking.py is defined but unused.

---

## 2. Test Coverage

### Summary: 135 tests, 135 passed, 0 skipped, 1 warning
- **Test runner:** pytest 8.x + pytest-asyncio (auto mode)
- **DB backend:** SQLite in-memory (aiosqlite)
- **Warning:** passlib DeprecationWarning on `crypt` module (Python 3.13)

### Test Files and What They Cover

| File | Tests | What's Covered |
|------|-------|----------------|
| `test_crisis.py` | 25 | Crisis detection: normalize_text (5), CRITICAL (10), HIGH (3), MEDIUM (5), NONE (5), response text (4), zero-width bypass |
| `test_guardrails.py` | 15 | ICD-10 codes, medication names, dosages, diagnostic language, case insensitivity, diacritics, feminine forms, safe fallback, reason string |
| `test_security.py` | 14 | AES-256-GCM round-trip (7), password hashing (4 incl. bcrypt compat), JWT create/decode (3), production validation (3) |
| `test_screening.py` | 12 | AUDIT scoring boundaries (8), recommendation text, wrong count, Q9/Q10 valid values (3) |
| `test_auth.py` | 7 | Refresh token CRUD: create, verify valid/wrong/expired/revoked, rotation, hash_token determinism |
| `test_rate_limit.py` | 3 | Key function: JWT extraction, IP fallback, invalid JWT fallback |
| `test_middleware.py` | 7 | Security headers: CSP, Permissions-Policy, HSTS (prod/dev), basic headers, XSS-Protection, Referrer-Policy |
| `test_tracking_service.py` | 10 | Sobriety streak (7 scenarios), tracking summary (3 incl. top trigger) |
| `test_integration.py` | 31 | Full HTTP flows: auth (7), tracking (5), screening (5), crisis (1), GDPR (3), chat (4), security (4) |
| `conftest.py` | — | Fixtures: db_session, mock_user_id, mock_anthropic |

### What's NOT Covered (gaps)

**Missing test scenarios:**
- **Chat service:** No unit tests for `process_message()` directly (only integration test with mock)
- **RAG service:** No tests for `retrieve_context()` or `format_context()` at all
- **Admin/GDPR export:** No test for decryption errors in export (only happy path)
- **Anthropic client:** No unit tests for `generate_response()` error fallback path
- **Audit logging:** No tests for `log_audit_event()` (tested implicitly via integration)
- **Config:** No test for `database_url` property generation
- **Rate limiting:** No integration test for actual rate limit enforcement
- **Concurrent access:** No tests for race conditions (e.g., double-submit checkin)
- **Edge cases:**
  - Message content at exactly 5000 chars (boundary)
  - Unicode edge cases in crisis detection beyond zero-width
  - Conversation history exactly at MAX_HISTORY_MESSAGES boundary
  - Summary with data outside the time window
  - Multiple simultaneous refresh token rotations
  - GDPR deletion when user has no data

---

## 3. Open Architectural Decisions & Blockers

### Decisions Needed

| # | Decision | Impact | Blocker? |
|---|----------|--------|----------|
| 1 | **Clinical advisor hire** | Cannot deploy crisis detection or guardrails to production without clinical review | YES |
| 2 | **Legal advisor hire** | GDPR Article 9 special category data, EU MDR classification | YES |
| 3 | **Embedding model selection** for RAG | Blocked on pgvector + embedding pipeline; current ilike search is MVP-only | For quality |
| 4 | **Redis for rate limiting** | In-memory limiter loses state on restart | For production |
| 5 | **Anonymous user recovery** | Users without email cannot recover lost tokens | Design decision |
| 6 | **i18n strategy** | System prompts, crisis responses, error messages are Czech-only | For internationalization |
| 7 | **Frontend stack confirmation** | React Native planned but not started | For Phase 2 |
| 8 | **Claude model configuration** | Model `claude-sonnet-4-20250514` is hardcoded in anthropic_client.py | Minor |

### Current Blockers

1. **No PostgreSQL instance** — Alembic migrations are initialized but cannot run without a live DB
2. **No clinical advisor** — crisis.py and guardrails.py cannot be validated for clinical accuracy
3. **No embedding service** — RAG is keyword-only (ilike search)
4. **No frontend** — API-only, no user-facing application

---

## 4. What Changed in Session 5 (Last Session)

Session 5 (commit `523cb84`) added:
- **Response models** on all 21 endpoints (Pydantic schemas for every response)
- **Pagination** on 3 list endpoints (conversations, cravings, screening results) with `skip`/`limit` params
- **SQL aggregation** in `get_tracking_summary()` — replaced Python-side loops with `func.count`, `func.avg`, `GROUP BY`
- **CheckConstraints** on `mood` (1-5), `energy_level` (1-5), `intensity` (1-10) in ORM models
- **Audit logging** on chat/tracking/craving endpoints
- **Global exception handler** for ValidationError, SQLAlchemyError, and generic Exception
- **GDPR export rate limit** (5/minute)
- **argon2-cffi migration** from bcrypt with backward compatibility for `$2b$` hashes
- Test count: 103 → 135

---

## 5. Opus Observations — Security Concerns & Architectural Smells

### Security Concerns

1. **Timing oracle in login** — The dummy hash used for constant-time comparison (`_dummy_hash = "$2b$12$..."`) is a bcrypt hash, but if the real user has an argon2 hash, `verify_password` takes a different code path with different timing. An attacker could detect whether an email exists based on response time differences between argon2 verification and bcrypt dummy verification.

2. **No AAD (Additional Authenticated Data) in AES-256-GCM** — `encrypt_field()` passes `None` as AAD. This means an encrypted field from one context (e.g., a message) could theoretically be swapped into another context (e.g., checkin notes) without detection. AAD should bind ciphertext to its context (table + column + row ID).

3. **Encryption key derivation via SHA-256 of short strings** — `_get_aes_key()` hashes short dev keys with SHA-256. This silently reduces entropy if someone deploys with a weak key that happens to be 64+ chars but is predictable. The production validator checks length but not entropy.

4. **JWT has no `iss` or `aud` claims** — Tokens have only `sub` and `exp`. Without `iss`/`aud`, tokens could be replayed if multiple services share the same JWT secret. Low risk for single-service MVP but should be addressed before multi-service deployment.

5. **No token blacklist for access tokens** — After GDPR deletion (`DELETE /me`), the access JWT remains valid for up to 1 hour (stateless). A deleted user can still call endpoints until token expiry. The `is_active` check in `get_current_user` mitigates this but relies on DB lookup for every request.

6. **CORS allows credentials with explicit origins in dev** — `allow_credentials=True` with `localhost:3000` and `localhost:8081` is correct for dev but the production CORS should be audited carefully.

7. **Rate limiter key fallback to raw IP** — `_key_func` uses `get_remote_address(request)` which may return a proxy IP or `None` behind load balancers. Should use `X-Forwarded-For` with a trusted proxy configuration.

### Architectural Smells

1. **Two normalization functions** — `crisis.py:normalize_text()` and `guardrails.py:_normalize_text()` implement similar logic differently. `crisis.py` strips with `unicodedata.combining()`, `guardrails.py` strips by checking `unicodedata.category() != "Mn"`. These are functionally equivalent but it's an unnecessary divergence. Should extract to a shared utility.

2. **Template injection surface** — `LUCEO_SYSTEM_PROMPT.replace("{rag_context}", rag_context)` means if a knowledge document contains the literal string `{user_context}`, it would be replaced by the second `.replace()` call. Very unlikely but a latent injection vector.

3. **Lazy singleton pattern for Anthropic client** — The global `_client` variable is not thread-safe. While Python's GIL makes this mostly safe, asyncio task switches during `_get_client()` could theoretically create multiple instances. Not harmful (worst case: extra HTTP pool) but not clean.

4. **Register endpoint commits twice** — First `db.commit()` for user creation, then another for audit log + refresh token. If the second commit fails, the user exists without an audit trail. Should be a single transaction.

5. **No structured logging** — Uses stdlib `logging` with string formatting. Should use structured logging (JSON) for production observability.

6. **`PaginatedResponse` schema defined but unused** — In `src/api/schemas/tracking.py`, a `PaginatedResponse` model is defined but never referenced by any endpoint. Dead code.

7. **No health check for database connectivity** — `GET /health` returns static `{"status": "ok"}` without checking if the database is actually reachable. Production health endpoints should verify dependencies.

8. **28 pre-existing ruff warnings** — Mostly long line warnings in `screening.py` translated strings. Should be suppressed with inline comments or the strings should be broken up.

### Positive Observations

- **Crisis detection architecture is excellent** — Zero-dependency, pre-LLM, deterministic, auditable. Exactly the right design for safety-critical functionality.
- **Defense in depth** — Crisis detection (pre-LLM) + guardrails (post-LLM) + system prompt rules = three layers of safety. Even if one fails, the others catch problems.
- **GDPR compliance is well-thought-out** — Consent tracking, data export, right to erasure, IP hashing, field-level encryption, soft delete with PII wipe, EU-only data region config.
- **Integration tests are comprehensive** — 31 tests covering full HTTP flows with realistic scenarios (auth, CRUD, GDPR, chat with mocked LLM).
- **Foreign key cascades are consistent** — All FKs have explicit `ondelete` (CASCADE or SET NULL for audit_logs). No orphaned records possible.
- **Password migration path** — Argon2 primary with bcrypt backward compatibility. Clean migration strategy.
