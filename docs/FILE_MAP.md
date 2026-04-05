# Luceo — Project File Map

Complete listing of every file and its purpose. Use this as the entry point when navigating the codebase.

## Root

| File | Purpose |
|---|---|
| `pyproject.toml` | Project metadata, dependencies, tool config |
| `.env.example` | Environment variable template |
| `.gitignore` | Git ignore patterns |
| `CLAUDE.md` | Instructions for AI assistants working on this project |
| `LUCEO_MAIN_DOCUMENT_v1.md` | Primary source of truth — vision, team, problem, solution |
| `LUCEO_ACTION_PLAN.md` | Consolidated action plan with phases |
| `LUCEO_DECISION_LOG.md` | Log of all key decisions (DEC-001 through DEC-008) |
| `LUCEO_PERSONAS.md` | User personas (Karel, Tereza, Jana, MUDr. Novák) |
| `luceo-deep-research.md` | Deep research — DTx market, competition, regulation |
| `zprava-hluboky-vyzkum.md` | Technical research — clinical procedures, architecture |

## `docs/`

| File | Purpose |
|---|---|
| `ARCHITECTURE.md` | System architecture, layer diagram, chat flow, security |
| `API_REFERENCE.md` | Complete API endpoint documentation |
| `FILE_MAP.md` | This file — project file listing |
| `EXECUTIVE_SUMMARY.md` | 2-page summary for business partners |
| `PITCH_DECK_OUTLINE.md` | 12-slide pitch deck skeleton |
| `SETUP.md` | Development setup and running instructions |
| `SAFETY.md` | Crisis detection and guardrails documentation |

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
| `auth.py` | `/api/v1/auth` | Mixed | POST /register, POST /login, GET /me, DELETE /me |
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
| `auth.py` | `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserResponse` |
| `chat.py` | `SendMessageRequest`, `MessageResponse`, `ChatResponse`, `ConversationResponse` |
| `screening.py` | `AuditSubmission`, `AuditResultResponse` |
| `tracking.py` | `CheckinRequest/Response`, `CravingRequest/Response`, `TrackingSummary` |
| `__init__.py` | Package marker |

## `src/main.py` — Application Entry Point

FastAPI app with CORS middleware, security headers middleware, request logging middleware, lifespan (engine dispose), health endpoint, all routers included.

## `tests/`

| File | Coverage |
|---|---|
| `conftest.py` | Shared fixtures: async SQLite session, mock Anthropic client |
| `test_crisis.py` | 30 tests: normalize_text, CRITICAL/HIGH/MEDIUM/NONE detection, crisis responses |
| `test_guardrails.py` | 7 tests: diagnostic patterns, medication patterns, safe fallback |
| `test_screening.py` | 10 tests: AUDIT scoring boundary tests |
| `__init__.py` | Package marker |
