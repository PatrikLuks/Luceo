# Luceo — Architecture Overview

## System Overview

Luceo is an AI-powered addiction recovery support platform. The MVP backend is a Python/FastAPI application with PostgreSQL storage, Claude API integration, and multi-layer safety systems.

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                    │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
│  │  Auth    │  │  Chat    │  │ Tracking │  │Screening│  │
│  │ /auth/* │  │ /chat/*  │  │/tracking/│  │/screen./│  │
│  └────┬────┘  └────┬─────┘  └────┬─────┘  └────┬────┘  │
│       │            │             │              │        │
│  ┌────┴────────────┴─────────────┴──────────────┴────┐  │
│  │              Core Layer (src/core/)                │  │
│  │  ┌────────┐ ┌─────────┐ ┌──────────┐ ┌────────┐  │  │
│  │  │Security│ │ Crisis  │ │Guardrails│ │ Audit  │  │  │
│  │  │JWT,AES │ │Detection│ │Post-LLM  │ │Logging │  │  │
│  │  └────────┘ └─────────┘ └──────────┘ └────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
│       │            │                                     │
│  ┌────┴────────────┴─────────────────────────────────┐  │
│  │           Services Layer (src/services/)           │  │
│  │  ┌──────────┐  ┌─────┐  ┌──────────┐             │  │
│  │  │Anthropic │  │ RAG │  │   Chat   │             │  │
│  │  │ Client   │  │     │  │Orchestr. │             │  │
│  │  └──────────┘  └─────┘  └──────────┘             │  │
│  └───────────────────────────────────────────────────┘  │
│       │            │                                     │
│  ┌────┴────────────┴─────────────────────────────────┐  │
│  │         Models Layer (src/models/)                 │  │
│  │  User, Conversation, Message, SobrietyCheckin,    │  │
│  │  CravingEvent, ScreeningResult, KnowledgeDocument,│  │
│  │  AuditLog, RefreshToken                             │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                   │
│           PostgreSQL + pgvector                          │
└─────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### API Layer (`src/api/`)
- HTTP endpoint definitions (routes)
- Request validation (Pydantic schemas in `src/api/schemas/`)
- Dependency injection (auth, database session)
- No business logic — delegates to services

### Core Layer (`src/core/`)
- **config.py** — Settings via pydantic-settings, reads `.env`
- **database.py** — AsyncEngine, session factory, `get_db()` dependency
- **security.py** — JWT (PyJWT, HS256), argon2 (+ legacy bcrypt), AES-256-GCM with AAD, refresh tokens
- **crisis.py** — Crisis detection (keyword matching, no dependencies)
- **crisis_contacts.py** — Czech crisis phone numbers (hardcoded)
- **guardrails.py** — Post-LLM output filtering (diagnoses, medications)
- **prompts.py** — System prompt, AI disclaimer, `build_system_prompt()` (safe_substitute)
- **text_utils.py** — Shared NFKD normalization (zero deps, used by crisis.py + guardrails.py)
- **deps.py** — `get_current_user` FastAPI dependency
- **audit.py** — Audit trail logging (AI Act compliance)
- **rate_limit.py** — Rate limiting with JWT/IP key extraction (slowapi)
- **middleware.py** — Request logging, security headers (CSP, HSTS, Permissions-Policy)

### Services Layer (`src/services/`)
- **chat.py** — Chat orchestrator (crisis → RAG → LLM → guardrails → store)
- **anthropic_client.py** — Thin Claude API wrapper
- **rag.py** — Knowledge base retrieval (keyword fallback for MVP)
- **screening.py** — WHO AUDIT questionnaire scoring
- **tracking.py** — Sobriety streak calculation, summaries
- **user_context.py** — Build personalized user context (streak, mood, cravings, AUDIT) for chat

### Models Layer (`src/models/`)
- SQLAlchemy 2.0 ORM models with UUID primary keys
- `BaseModel` provides id, created_at, updated_at
- Field-level encryption for sensitive data

## Chat Message Flow

```
User message
    │
    ▼
1. detect_crisis(message)     ← Pure logic, no DB/API, <1ms
    │
    ├── CRITICAL/HIGH → Predefined response (NO LLM call)
    │                    Store with crisis_level audit trail
    │                    Return crisis contacts
    │
    ├── MEDIUM → Flag to append crisis resources after LLM
    │
    ▼
2. Load conversation history (decrypt last 20 messages)
    │
    ▼
3. RAG: retrieve relevant clinical docs from knowledge_documents
    │
    ▼
4. Build system prompt (identity + RAG context + user context)
    │
    ▼
5. Call Claude API (claude-sonnet-4-20250514)
    │
    ▼
6. check_response_guardrails(response)
    │
    ├── UNSAFE → Replace with safe fallback
    │
    ▼
7. Encrypt & store both messages with crisis_level
    │
    ▼
8. Return response (+ crisis resources if MEDIUM, + disclaimer if interval)
```

## Security Architecture

| Layer | Mechanism | Purpose |
|---|---|---|
| Transport | HTTPS (infrastructure) | Encryption in transit |
| Authentication | JWT HS256 (1h) + refresh tokens (30d, SHA-256) | User identity |
| Data at rest | AES-256-GCM per-field with AAD | GDPR encryption, cross-field swap prevention |
| Crisis detection | Keyword matching pre-LLM | Immediate safety |
| Output guardrails | Regex post-LLM | Prevent diagnoses/medications |
| Audit trail | AuditLog model | AI Act compliance |
| IP logging | SHA-256 hash only | GDPR — no raw IPs |
| User deletion | Soft delete + PII wipe (audit logs preserved) | GDPR Art. 17 + AI Act |
| CORS | Middleware (configure per env) | Cross-origin protection |
| Headers | X-Content-Type-Options, X-Frame-Options | XSS/clickjacking |
| Rate limiting | slowapi (JWT/IP key, per-endpoint) | Abuse prevention |
| Security headers | CSP, HSTS (prod), Permissions-Policy | Content security |

## Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Primary keys | UUID v4 | GDPR portability, no enumeration |
| Chat storage | AES-256-GCM field-level | Defense in depth |
| Crisis detection | Keyword matching (not ML) | Deterministic, auditable |
| Guardrails | 2 layers (prompt + post-LLM) | Belt and suspenders |
| Email | Optional (nullable) | Anonymity per Karel persona |
| User deletion | Soft delete + PII wipe | Audit trail + GDPR Art. 17 |
| System prompt | string.Template with safe_substitute | Version controlled, injection-safe |
| Chat protocol | Request-response | Sufficient for MVP |
| Embedding model | Deferred (keyword fallback) | MVP without embedding infra |
