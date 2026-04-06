# Luceo — Project File Map

Complete listing of every file and its purpose. Use this as the entry point when navigating the codebase.

## Root

| File | Purpose |
|---|---|
| `CLAUDE.md` | Instructions for AI assistants working on this project |
| `README.md` | GitHub landing page (English) |
| `pyproject.toml` | Project metadata, dependencies, tool config |
| `.env.example` | Environment variable template |
| `.gitignore` | Git ignore patterns |
| `alembic.ini` | Alembic configuration (`sqlalchemy.url` set programmatically) |

## `docs/project/` — Project Documentation

| File | Purpose |
|---|---|
| `MAIN_DOCUMENT.md` | Primary source of truth — vision, team, problem, solution, roadmap |
| `DECISION_LOG.md` | Log of all key decisions (DEC-001 through DEC-008) |
| `PERSONAS.md` | User personas (Karel, Tereza, Jana, MUDr. Novák) |
| `ACTION_PLAN.md` | Consolidated action plan with phases |

## `docs/business/` — Business & Investor Documents

| File | Purpose |
|---|---|
| `EXECUTIVE_SUMMARY.md` | 2-page summary for business partners |
| `PITCH_DECK_OUTLINE.md` | 12-slide pitch deck skeleton |

## `docs/research/` — Research

| File | Purpose |
|---|---|
| `deep-research.md` | Deep research — DTx market, competition, regulation, grants |
| `technical-research.md` | Technical research — clinical procedures, architecture, validation |

## `docs/technical/` — Technical Documentation

| File | Purpose |
|---|---|
| `ARCHITECTURE.md` | System architecture, layer diagram, chat flow, security |
| `API_REFERENCE.md` | Complete API endpoint documentation |
| `FILE_MAP.md` | This file — project file listing |
| `SETUP.md` | Development setup and running instructions |
| `SAFETY.md` | Crisis detection and guardrails documentation |

## `docs/reports/` — Session Reports

| File | Purpose |
|---|---|
| `REPORT_2026-04-05.md` | Session 1 report (2026-04-05) — refresh tokens, rate limiting, Alembic |
| `REPORT_2026-04-05_s3.md` | Session 3 report (2026-04-05) — security audit, test expansion, README |
| `REPORT_2026-04-06_s4.md` | Session 4 report (2026-04-06) — FK cascades, integration tests, codebase audit |

## `alembic/` — Database Migrations

| File | Purpose |
|---|---|
| `env.py` | Alembic async migration environment |

## `src/core/` — Core Logic

| File | Purpose | Dependencies |
|---|---|---|
| `config.py` | `Settings(BaseSettings)` — reads `.env`, computed `database_url` | pydantic-settings |
| `database.py` | AsyncEngine, `async_session_maker`, `get_db()` generator | SQLAlchemy, config |
| `security.py` | JWT create/decode, bcrypt hash/verify, AES-256-GCM encrypt/decrypt | python-jose, passlib, cryptography |
| `deps.py` | `get_current_user` FastAPI dependency (Bearer → User) | security, database, models |
| `crisis.py` | `detect_crisis()`, `CrisisLevel` enum, `get_crisis_response()` | **NONE** (intentionally) |
| `crisis_contacts.py` | Czech crisis phone numbers (hardcoded Pydantic models) | **NONE** (pydantic only) |
| `guardrails.py` | `check_response_guardrails()` — post-LLM regex checks | **NONE** (re only) |
| `prompts.py` | System prompt, AI disclaimer, disclaimer reminder | **NONE** |
| `audit.py` | `log_audit_event()` — AI Act / GDPR audit trail | models.audit_log |
| `rate_limit.py` | Rate limiting key function (JWT/IP extraction) | slowapi |
| `middleware.py` | `RequestLoggingMiddleware`, `SecurityHeadersMiddleware` | starlette |
| `__init__.py` | Package marker | — |

## `src/models/` — Database Models (SQLAlchemy 2.0)

| File | Model(s) | Table(s) |
|---|---|---|
| `base.py` | `Base` (DeclarativeBase), `BaseModel` (UUID PK, timestamps) | — |
| `user.py` | `User` | `users` |
| `conversation.py` | `Conversation`, `Message` | `conversations`, `messages` |
| `tracking.py` | `SobrietyCheckin`, `CravingEvent` | `sobriety_checkins`, `craving_events` |
| `screening.py` | `ScreeningResult` | `screening_results` |
| `knowledge_base.py` | `KnowledgeDocument` (with pgvector) | `knowledge_documents` |
| `audit_log.py` | `AuditLog` | `audit_logs` |
| `refresh_token.py` | `RefreshToken` | `refresh_tokens` |
| `__init__.py` | Package marker | — |

## `src/services/` — Business Logic

| File | Function | Notes |
|---|---|---|
| `chat.py` | `process_message()` — **core chat orchestrator** | Crisis → RAG → LLM → guardrails → store |
| `anthropic_client.py` | `generate_response()` — thin Claude API wrapper | Returns fallback on error |
| `rag.py` | `retrieve_context()`, `format_context()` | Keyword fallback for MVP |
| `screening.py` | `AUDIT_QUESTIONS`, `score_audit()` | WHO AUDIT 10-question tool |
| `tracking.py` | `get_sobriety_streak()`, `get_tracking_summary()` | Streak calculation, summaries |
| `__init__.py` | Package marker | — |

## `src/api/` — HTTP Endpoints

| File | Prefix | Auth | Endpoints |
|---|---|---|---|
| `auth.py` | `/api/v1/auth` | Mixed | POST /register, POST /login, GET /me, DELETE /me, POST /refresh, POST /logout |
| `chat.py` | `/api/v1/chat` | Yes | POST /conversations, POST /conversations/{id}/messages, GET /conversations |
| `screening.py` | `/api/v1/screening` | Mixed | GET /questionnaires/audit (no auth), POST /questionnaires/audit, GET /results |
| `tracking.py` | `/api/v1/tracking` | Yes | POST /checkin, GET /checkin/today, POST /cravings, GET /cravings, GET /summary, GET /streak |
| `crisis.py` | `/api/v1/crisis` | No | GET /contacts |
| `admin.py` | `/api/v1/admin` | Yes | GET /export-my-data (GDPR Art. 15) |
| `router.py` | — | — | Aggregates all routers into `all_routers` list |
| `__init__.py` | — | — | Package marker |

## `src/api/schemas/` — Request/Response Models (Pydantic)

| File | Models |
|---|---|
| `auth.py` | `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserResponse`, `RefreshRequest` |
| `chat.py` | `SendMessageRequest`, `ChatResponse`, `ConversationResponse` |
| `screening.py` | `AuditSubmission`, `AuditResultResponse` |
| `tracking.py` | `CheckinRequest/Response`, `CravingRequest/Response`, `TrackingSummary` |
| `__init__.py` | Package marker |

## `src/main.py` — Application Entry Point

FastAPI app with CORS middleware, security headers middleware, request logging middleware, lifespan (engine dispose), health endpoint, all routers included.

## `tests/`

| File | Coverage |
|---|---|
| `conftest.py` | Shared fixtures: async SQLite session, mock Anthropic client, all 9 model imports |
| `test_integration.py` | 31 tests: full HTTP flows (auth, tracking, screening, crisis, GDPR, chat, security headers) via httpx AsyncClient |
| `test_crisis.py` | 32 tests: normalize_text, zero-width bypass, CRITICAL/HIGH/MEDIUM/NONE detection, crisis responses |
| `test_guardrails.py` | 15 tests: diagnostic patterns, medication patterns, diacritics normalization, feminine forms, safe fallback self-check |
| `test_screening.py` | 13 tests: AUDIT scoring boundary tests, Q9/Q10 validation |
| `test_auth.py` | 7 tests: refresh token create, verify, expire, revoke, rotation, hash |
| `test_rate_limit.py` | 3 tests: JWT key extraction, IP fallback, invalid JWT |
| `test_middleware.py` | 7 tests: CSP, HSTS prod/dev, Permissions-Policy, X-XSS-Protection, Referrer-Policy, basic headers |
| `test_security.py` | 13 tests: AES-256-GCM round-trip, corrupt data, JWT create/decode, password hashing, production config validation |
| `test_tracking_service.py` | 10 tests: sobriety streak (consecutive, gaps, breaks), tracking summary (empty, with data, top trigger) |
| `__init__.py` | Package marker |
