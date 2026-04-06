# LUCEO — Comprehensive Project Report

> **Generated:** 2026-04-06 | **Source:** All project documentation (17 files) | **Purpose:** Single-file project knowledge base for Claude AI consumption

---

## 1. PROJECT IDENTITY

**Name:** Luceo (Latin: "I shine / I glow")
**Tagline:** "Recovery jako světlo, ne trest." (Recovery as light, not punishment.)
**Type:** AI-powered addiction recovery support platform
**Primary focus (MVP):** Alcoholism in the Czech Republic
**Long-term ambition:** Global, multi-addiction platform
**Positioning:** Wellness/informational app — NOT a medical device (for MVP phase)
**Version:** 0.1.0 (MVP backend complete)
**Repository:** Python/FastAPI backend with PostgreSQL + pgvector
**Frontend:** React Native (planned, not yet implemented)

### Core Principles
- **Not a chatbot** — personalized recovery guide
- **Not a therapist replacement** — 24/7 support between therapy sessions
- **Privacy-first** — GDPR, EU hosting, zero third-party tracking
- **No stigma** — "change your relationship with alcohol", not "you're an addict"
- **Wellness positioning** — avoids EU MDR medical device classification for MVP

---

## 2. TEAM

| Role | Person | Details |
|---|---|---|
| PM / CEO | Patrik Luks | 19 years old, software developer, IT entrepreneur, finance background via JPL Servis, entering VŠB-TUO Informatika (then Quantum Informatics) |
| Business Manager | Jarda | Business operations |
| Potential Advisor/Stakeholder | Josef Luks | CFA charterholder, founder of JPL Servis (wealth management, Prague), family connection to PM |
| Clinical Advisor | **TBD** | CRITICAL gap — must be resolved in Phase 1. Targets: AT ambulance Ostrava, Adiktologická klinika VFN Praha, CARG |
| Legal Advisor | **TBD** | CRITICAL gap — healthtech lawyer needed for AI Act + MDR positioning |

---

## 3. PROBLEM & MARKET

### Czech Epidemiology
| Substance/Behavior | Affected Population |
|---|---|
| Risky alcohol drinking | 1.3–1.7 million adults |
| Harmful alcohol drinking | 720,000–900,000 |
| Daily alcohol consumption | 6–10% of population |
| Psychoactive medication abuse | 720K–1.2M |
| Daily smokers | 1.5–2.0 million |
| High-risk gambling | 60,000–110,000 |
| Digital addiction risk (adults) | 360,000–540,000 |
| Tobacco-related deaths/year | 16,000–18,000 |

- Czech Republic consistently in world **top 5** for per-capita alcohol consumption
- AT ambulances overloaded: 20 min appointments every 2-4 weeks, zero between-session visibility
- **Zero** Czech-localized, clinically-oriented digital addiction solution exists

### Global DTx Market
- **$10–14 billion** estimated 2026, CAGR 19–27% through 2034
- Mental health + addiction: ~25% of market, fastest-growing segment
- Germany DiGA registry: 68 approved apps, psychology/mental health = ~50% of all DiGAs
- DiGA pricing: EUR 400–900/patient/year

### Competition
| Competitor | Weakness vs Luceo |
|---|---|
| Monument (USA) | FTC $2.5M fine for sharing health data; English only; US market |
| Tempest (USA) | Acquired by Monument; same data scandal; expensive |
| Woebot | General mental health, not addiction-specific |
| Reframe | Gamification, shallow clinical basis, high churn |
| Sober Grid | Peer support only, no AI, no clinical intervention |
| Czech trackers | Simple apps, no AI, no clinical foundation |

**Competitive moat (5 pillars):** (1) Privacy-first (Monument scandal), (2) Czech localization (first mover), (3) Cultural fit (Czech/Moravian mentality, anonymity as feature), (4) AI safety (Anthropic/Claude), (5) Academic partner (VŠB-TUO for TAČR grants).

---

## 4. SOLUTION — MVP FEATURES

1. **Onboarding screening** — WHO AUDIT-10 questionnaire with automated risk assessment
2. **AI chat assistant** — Claude API + RAG over clinical knowledge base (CBT techniques, MI scripts, WHO guidelines)
3. **Sobriety tracker + craving log** — daily check-ins, mood/energy tracking, streak calculation, craving events with triggers
4. **Crisis detection + contacts** — 3-layer safety system (pre-LLM keywords → system prompt → post-LLM guardrails), 6 Czech crisis phone numbers
5. **GDPR-compliant auth + storage** — AES-256-GCM field encryption, JWT + refresh tokens, data export (Art. 15), right to erasure (Art. 17)
6. **Audit trail** — AI Act compliance logging of all AI interactions

**Deliberately excluded from MVP:** EHR integration, telemedicine, wearables, gamification, family module, VR/AR — all deferred to Phase 2+.

---

## 5. USER PERSONAS

### P1 — Karel ("Hidden drinker") — PRIMARY
Male, 42-55, Moravia, smaller town. Manual/admin work, married with children. Drinks daily (3-4 beers/evening). Won't tell his wife, won't see a doctor (stigma). Would download app secretly at 23:00. Needs: anonymity, no "addict" label, masculine direct tone, no visible push notifications.

### P2 — Tereza ("Millennial cope") — PRIMARY
Female, 24-34, Prague. University, white-collar. Drinks at parties, after stressful days, for social anxiety. Digitally native, pays for subscriptions. Needs: modern clean UX, "conscious drinking" framing, immediate value in first 3 minutes, beautiful data visualizations.

### P3 — Jana ("Caring wife/mother") — SECONDARY
Female, 40-60, Moravia. Partner or child has alcohol problem. Seeks info online. Could recommend app to loved one or seek support for herself.

### P4 — MUDr. Novák ("AT ambulance doctor") — B2B
Doctor/addictologist, 35-55. Overloaded. Wants: between-session data, reduced no-shows, modern approach. Barriers: distrust of AI, liability, GDPR concerns.

### Design Principles from Personas
1. Anonymity is a feature, not a disclaimer (email is optional)
2. No-stigma framing — never "addiction" in first contact
3. Mobile-first, nighttime usage
4. Immediate value (Tereza leaves after 3 bad minutes)
5. Crisis is edge case, not core UX
6. Czech as first language — native Czech tone, not translated English

---

## 6. TECHNICAL ARCHITECTURE

### Stack
| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI |
| Database | PostgreSQL 15+ with pgvector |
| AI | Claude API (Anthropic), claude-sonnet-4-20250514 |
| Auth | JWT HS256 (1h access) + refresh tokens (30d, SHA-256 hashed, rotation) |
| Encryption | AES-256-GCM field-level encryption |
| Password hashing | argon2-cffi (primary) + passlib/bcrypt (legacy backward compat) |
| Migrations | Alembic (async template) |
| Rate limiting | slowapi (JWT/IP key extraction) |
| Testing | pytest + pytest-asyncio, SQLite in-memory |
| Frontend | React Native (planned) |

### Four-Layer Architecture
```
src/
├── api/           # HTTP endpoints (FastAPI routers) + Pydantic schemas
│   ├── auth.py         /api/v1/auth/*     (6 endpoints)
│   ├── chat.py         /api/v1/chat/*     (3 endpoints)
│   ├── screening.py    /api/v1/screening/* (3 endpoints)
│   ├── tracking.py     /api/v1/tracking/*  (6 endpoints)
│   ├── crisis.py       /api/v1/crisis/*    (1 endpoint)
│   ├── admin.py        /api/v1/admin/*     (1 endpoint)
│   └── schemas/        Pydantic request/response models
├── core/          # Cross-cutting concerns
│   ├── config.py       Settings (pydantic-settings, .env)
│   ├── database.py     AsyncEngine, session factory, get_db()
│   ├── security.py     JWT, argon2, AES-256-GCM
│   ├── deps.py         get_current_user dependency
│   ├── crisis.py       Crisis detection (ZERO DEPS, <1ms)
│   ├── crisis_contacts.py  Czech crisis phone numbers (hardcoded)
│   ├── guardrails.py   Post-LLM regex filter
│   ├── prompts.py      System prompt, disclaimers
│   ├── audit.py        Audit trail logging (AI Act)
│   ├── rate_limit.py   slowapi rate limiting
│   └── middleware.py    Request logging, security headers
├── services/      # Business logic
│   ├── chat.py         Chat orchestrator (crisis → RAG → LLM → guardrails → store)
│   ├── anthropic_client.py  Claude API wrapper (lazy singleton)
│   ├── rag.py          Knowledge retrieval (keyword fallback for MVP)
│   ├── screening.py    WHO AUDIT scoring
│   └── tracking.py     Streak calculation, SQL-aggregated summaries
└── models/        # SQLAlchemy 2.0 ORM
    ├── base.py         Base with UUID v4 PK, created_at, updated_at
    ├── user.py         User (email optional!)
    ├── conversation.py Conversation + Message (encrypted)
    ├── tracking.py     SobrietyCheckin + CravingEvent (CheckConstraints)
    ├── screening.py    ScreeningResult
    ├── knowledge_base.py KnowledgeDocument (pgvector)
    ├── audit_log.py    AuditLog
    └── refresh_token.py RefreshToken (SHA-256 hashed)
```

### Database Schema (9 Tables)
| Table | Purpose | FK Cascade |
|---|---|---|
| `users` | User accounts (email optional for anonymity) | — |
| `conversations` | Chat conversation containers | CASCADE to users |
| `messages` | Chat messages (content encrypted AES-256-GCM) | CASCADE to conversations |
| `sobriety_checkins` | Daily sobriety check-ins (unique per user+date) | CASCADE to users |
| `craving_events` | Craving event logs with triggers | CASCADE to users |
| `screening_results` | AUDIT questionnaire results | CASCADE to users |
| `knowledge_documents` | RAG knowledge base (pgvector embeddings) | — |
| `audit_logs` | AI Act compliance audit trail | SET NULL on user deletion |
| `refresh_tokens` | JWT refresh tokens (SHA-256 hashed) | CASCADE to users |

**CheckConstraints:** mood (1-5 or NULL), energy_level (1-5 or NULL), intensity (1-10).

### Chat Message Flow
1. `detect_crisis(message)` — pure logic, zero deps, <1ms
2. CRITICAL/HIGH → predefined response + crisis contacts, NO LLM call
3. MEDIUM → flag to append crisis resources after LLM response
4. Load conversation history (decrypt last 20 messages)
5. RAG retrieval from knowledge_documents
6. Build system prompt (identity + RAG context + user context)
7. Call Claude API → `check_response_guardrails()` → encrypt and store both messages

### Security Architecture (11 Layers)
| Layer | Implementation |
|---|---|
| Transport | HTTPS/TLS |
| Authentication | JWT HS256 (1h) + refresh tokens (30d, rotation) |
| Password hashing | argon2-cffi (bcrypt legacy compat) |
| Data at rest | AES-256-GCM per-field encryption |
| Crisis detection | Deterministic keyword matching pre-LLM |
| Output guardrails | Regex post-LLM filter |
| Audit trail | AuditLog model (every AI interaction, login, deletion) |
| IP logging | SHA-256 hash only (GDPR — no raw IPs) |
| User deletion | Soft delete + PII wipe across 7 tables |
| Security headers | CSP, HSTS (prod), X-Content-Type-Options, X-Frame-Options, Permissions-Policy |
| Rate limiting | Per-endpoint: auth 5/min, chat 20/min, tracking 60/min, GDPR export 5/min |

---

## 7. API REFERENCE (21 Endpoints)

### Auth (`/api/v1/auth`) — 6 endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /register | No | Create account (email optional, GDPR consent required) → tokens + AI disclaimer |
| POST | /login | No | Login → tokens |
| POST | /refresh | No | Rotate refresh token → new token pair |
| POST | /logout | No | Revoke refresh token |
| GET | /me | Yes | User profile |
| DELETE | /me | Yes | GDPR Art. 17 erasure (soft delete + PII wipe) |

### Chat (`/api/v1/chat`) — 3 endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /conversations | Yes | Create conversation → id, disclaimer (AI Act) |
| POST | /conversations/{id}/messages | Yes | Send message → AI response, crisis_detected, crisis_contacts |
| GET | /conversations | Yes | List conversations (paginated: skip/limit, max 100) |

### Screening (`/api/v1/screening`) — 3 endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /questionnaires/audit | No | WHO AUDIT 10 questions (Czech + English) |
| POST | /questionnaires/audit | Yes | Submit answers → score, risk_level, recommendation |
| GET | /results | Yes | Screening history (paginated) |

**AUDIT Risk Levels:** low_risk (0-7), hazardous (8-15), harmful (16-19), possible_dependence (20-40).

### Tracking (`/api/v1/tracking`) — 6 endpoints
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /checkin | Yes | Daily sobriety check-in (upserts), audit logged |
| GET | /checkin/today | Yes | Check if today already logged |
| POST | /cravings | Yes | Log craving event (intensity 1-10, trigger category), audit logged |
| GET | /cravings | Yes | Craving history (paginated) |
| GET | /summary | Yes | SQL-aggregated stats for last N days |
| GET | /streak | Yes | Current sobriety streak in days |

### Crisis (`/api/v1/crisis`) — 1 endpoint
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /contacts | No | Czech crisis contacts (6 numbers) |

### Admin (`/api/v1/admin`) — 1 endpoint
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /export-my-data | Yes | GDPR Art. 15 data export (rate limited 5/min) |

### Health — 1 endpoint
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /health | No | `{"status": "ok", "version": "0.1.0"}` |

**All 21 endpoints have typed Pydantic response_model schemas.**
**3 list endpoints have pagination (skip/limit, default 50, max 100).**
**Global exception handlers:** ValidationError→422, SQLAlchemyError→500, Exception→500.

---

## 8. SAFETY SYSTEM (3 Independent Layers)

### Layer 1: Crisis Detection (`src/core/crisis.py`)
- **Design:** Zero external dependencies, deterministic regex matching, <1ms, runs BEFORE every LLM call
- **Normalization:** NFD decomposition + combining chars stripped (handles diacritics: "chci zemřít" = "chci zemrit")
- **Crisis levels:**
  - **CRITICAL:** "chci zemřít", "sebevražda", "kill myself" → predefined message + ALL crisis contacts, NO LLM
  - **HIGH:** "chci si ublížit", "předávkovat se", "self-harm" → predefined message + key contacts, NO LLM
  - **MEDIUM:** "relaps", "chci pít", "neschopnost dál" → LLM responds, crisis resources appended
  - **NONE:** Normal conversation

### Layer 2: System Prompt (`src/core/prompts.py`)
- Instructions to Claude: never diagnose, never recommend medications/dosages, refer to emergency for withdrawal symptoms (tremors, hallucinations, seizures), empathetic non-stigmatizing language, stay within RAG context, respond in Czech unless user writes English
- AI disclaimer shown at conversation start + every 10 messages

### Layer 3: Output Guardrails (`src/core/guardrails.py`)
- Post-LLM regex filter with NFKD normalization
- **Diagnostic patterns blocked:** ICD-10 codes (F10.x-F19.x), "diagnóza", "trpíte", "jsi alkoholik/závislý"
- **Medication patterns blocked:** naltrexon, acamprosat, disulfiram, antabus, campral, benzodiazepines (diazepam, lorazepam, alprazolam, xanax, lexaurin), SSRIs (sertralin, fluoxetin, paroxetin, escitalopram, citalopram), dosage patterns ("X mg denně/ráno/večer")
- **When triggered:** Unsafe response replaced with safe fallback redirecting to doctor

### Czech Crisis Contacts (Hardcoded)
| Service | Phone |
|---|---|
| Linka bezpečí | 116 111 |
| Krizová pomoc | 116 123 |
| Národní linka pro odvykání | 800 350 000 |
| Podané ruce | 549 257 217 |
| Záchranná služba | 155 |
| Tísňová linka | 112 |

### AI Act Compliance
- AI disclaimer at conversation start and every 10 messages
- Every message stored with `crisis_level` field
- AuditLog: logs all AI interactions, crisis detections, logins, deletions, conversation creation, check-ins, craving logs
- Audit trail preserved even after user deletion (FK SET NULL)

**Both crisis.py and guardrails.py require clinical advisor review before production deployment.**

---

## 9. REGULATORY CONTEXT

| Regulation | Impact on Luceo | Priority | Strategy |
|---|---|---|---|
| **GDPR** (EU 2016/679) | Health data = Article 9 special category | CRITICAL | Privacy-by-design, AES-256-GCM, zero tracking, EU hosting, Art. 15 export, Art. 17 erasure |
| **EU AI Act** | Health AI could be high-risk if clinical claims | HIGH | Wellness positioning = limited risk (transparency only). Deadline: **2 August 2026** |
| **EU MDR** (2017/745) | SaMD classification if therapeutic claims | HIGH | Avoid "therapy/treatment/diagnosis" terminology. Wellness app = exempt |
| **Czech Law 379/2005 Sb.** | Health protection from addictions | MEDIUM | Align with national prevention policy |
| **EHDS** (adopted 2023) | EHR interoperability requirement by 2029 | LOW (future) | HL7 FHIR preparation for Phase 3 |

**Key terminology rule:** Use "support", "guide", "information" — NEVER "treatment", "therapy", "diagnosis".

**Monument scandal precedent:** FTC fined Monument $2.5M (April 2024) for sharing health data with Google/Facebook/Pinterest via tracking pixels. This validates Luceo's privacy-first positioning as a competitive differentiator.

---

## 10. BUSINESS MODEL & FINANCIAL FRAMEWORK

### Revenue Streams (by phase)
| Phase | Source | Revenue Estimate |
|---|---|---|
| 0-1 | Grants (TAČR SIGMA, MSK regional) | 500K–5M CZK |
| 1 | B2B AT ambulance pilot | Low (validation, not revenue) |
| 2 | B2C subscription | 0–200K CZK/month |
| 2 | B2G municipalities/regions/MZČR | Moderate |
| 3 | Insurance (VZP prevention fund) | High potential |
| 3 | Corporate wellness (employer benefits) | No regulatory approval needed |
| 3+ | DiGA (Germany, 73M insured) | EUR 400–900/patient/year |

### Grant Opportunities
| Grant | Amount | Realistic for Luceo | Key Condition |
|---|---|---|---|
| TAČR SIGMA/Novacci | Up to 15M CZK | **HIGH** | Research partner (VŠB-TUO) |
| Regional MSK grants | Variable | MEDIUM-HIGH | Startup from MSK (Opava) = advantage |
| EU4Health | Up to EUR 2M | LOW for MVP | Consortium, 12-18 month lead |
| EIC Accelerator | Up to EUR 2.5M grant | MEDIUM | Needs pilot validation data |

### MVP Budget
| Item | Estimate |
|---|---|
| Development (6 months) | 300–800K CZK |
| Claude API (10K msgs/month) | 2–5K CZK/month |
| Legal (GDPR, ToS, healthtech) | 50–150K CZK |
| **Total MVP** | **500K–1.5M CZK** |

### Year 1 Projections
| Metric | Realistic | Ambitious |
|---|---|---|
| MAU after 12 months | 500–2,000 | 5,000–10,000 |
| B2C subscription revenue | 0–40K CZK/month | 100–200K CZK/month |
| B2B (AT pilot) | 0 | 50–150K CZK/year |
| Grant revenue | 500K–2M CZK | 2–5M CZK |

### KPIs
- **Engagement:** DAU/MAU, retention (day 7, day 30)
- **Clinical:** AUDIT score reduction, abstinent days, craving frequency reduction
- **Product:** avg sobriety streak, crisis escalation rate, NPS
- **Technical:** API availability, latency, error rates
- **Economic:** CAC, LTV, health system savings

---

## 11. ROADMAP

### Phase 0 — Foundations (April 2026, parallel with maturita)
**CRITICAL (blockers):**
- Contact clinical advisor — targets: AT ambulance Ostrava, VFN Praha, CARG
- Legal scan with healthtech lawyer — one session, AI Act + MDR, ~EUR 500-1000
- Register domain luceo.app

**HIGH:**
- Contact Jarda, share vision document
- 2-page executive summary for Jarda and Josef
- Legal entity decision (s.r.o. or a.s.) — needed by summer for TAČR

### Phase 1 — Validation (May–June 2026, post-maturita)
- Pitch to Josef Luks in Prague (key: his network — insurers, corporates)
- VŠB-TUO research office contact (co-applicant for TAČR)
- TAČR consultation (first meeting free)
- Build clinical knowledge database (CBT Czech, AUDIT/CAGE/DAST, MI scripts, crisis contacts)
- Pitch deck v1.0

### Phase 2 — Build (Summer–Autumn 2026)
- MVP development with AI Act compliance architecture from day 1
- Pilot partner: one AT ambulance (Ostrava preferred)
- TAČR SIGMA grant application with VŠB-TUO
- GDPR compliance finalization (DPA, ToS, disclaimer, privacy policy)
- React Native frontend development
- First users and feedback

### Phase 3 — Scale (2027+)
- Clinical validation: pilot RCT with AT ambulance (6-12 months)
- VZP prevention fund (softer path than full reimbursement)
- Corporate wellness B2B
- Internationalization: SK → DE (via DiGA) → PL
- DiGA process: CE marking (MDR Class I/IIa) → BfArM application → German market

### Long-term (2028+)
- Full DiGA application to BfArM
- EU market expansion (AT → FR → IT)
- Relapse prediction model
- Wearables integration
- Additional addictions (drugs, gambling, digital)

---

## 12. KEY DECISIONS LOG

| ID | Decision | Rationale |
|---|---|---|
| DEC-001 | Name: Luceo | Latin "I shine", globally pronounceable, no addiction stigma, premium feel |
| DEC-002 | AI engine: Claude API (Anthropic) | PM experience with Claude, strongest AI safety focus, well-documented RAG |
| DEC-003 | Primary vertical: Alcoholism | Largest CZ segment (1.3-1.7M), best clinical data, strongest grant argument |
| DEC-004 | Positioning: Wellness app | Avoids EU MDR CE marking (tens of thousands EUR, months delay) |
| DEC-005 | GTM: Grants → AT pilot → scale | B2C fails without clinical credibility; grants don't need product |
| DEC-006 | Team: Patrik + Jarda + Josef (potential) | Clinical + legal advisors are critical gaps for Phase 1 |
| DEC-007 | Session 0 = founding document | 5 April 2026 |
| DEC-008 | Backend: Python (FastAPI) | Stronger AI/ML ecosystem, Anthropic SDK, pgvector, async-native |

---

## 13. IMPLEMENTATION STATUS (After Session 5)

### Test Suite
| Metric | Value |
|---|---|
| Total tests | 135 |
| Passing | 135 |
| Skipped | 0 |
| Integration tests | 31 (full HTTP flows via httpx AsyncClient) |

### Test Files
| File | Tests | Coverage |
|---|---|---|
| test_integration.py | 31 | Auth, tracking, screening, crisis, GDPR, chat, security headers |
| test_crisis.py | 32 | normalize_text, zero-width bypass, CRITICAL/HIGH/MEDIUM/NONE, responses |
| test_guardrails.py | 15 | Diagnostic patterns, medication patterns, diacritics, feminine forms |
| test_screening.py | 13 | AUDIT scoring boundaries, Q9/Q10 validation |
| test_security.py | 13 | AES-256-GCM, JWT, password hashing, production config validation |
| test_tracking_service.py | 10 | Streak logic (consecutive, gaps, breaks), tracking summary |
| test_auth.py | 7 | Refresh tokens (create, verify, expire, revoke, rotation) |
| test_middleware.py | 7 | CSP, HSTS, Permissions-Policy, X-XSS-Protection, Referrer-Policy |
| test_rate_limit.py | 3 | JWT key extraction, IP fallback, invalid JWT |

### Codebase Size
| Component | Lines |
|---|---|
| src/ | ~2,574 |
| tests/ | ~1,436 |

### Cross-Session Evolution
| Metric | S0 | S1 | S3 | S4 | S5 |
|---|---|---|---|---|---|
| Tests (pass/total) | 49/49 | 67/67 | 100/103 | 131/134 | **135/135** |
| Endpoints | 19 | 21 | 21 | 21 | 21 |
| DB tables | 8 | 9 | 9 | 9 | 9 |
| src/ lines | ~1,850 | ~2,188 | ~2,298 | 2,318 | ~2,574 |
| tests/ lines | ~390 | ~512 | ~824 | 1,435 | ~1,436 |
| response_model | — | — | — | 12/21 | **21/21** |

### Session Highlights
- **Session 1:** Refresh tokens, rate limiting, Alembic, 10 bug fixes, +18 tests
- **Session 3:** Security audit (3 CRITICAL, 5 HIGH, 9 MEDIUM fixes), guardrails NFKD normalization, README, +36 tests
- **Session 4:** FK cascades, 31 integration tests, UTC date fix, register race condition fix
- **Session 5:** Response models on all 21 endpoints, pagination (3 endpoints), SQL aggregation, CheckConstraints, audit logging, global exception handler, GDPR rate limit, argon2-cffi migration

---

## 14. DEPENDENCIES

### Production
| Package | Purpose |
|---|---|
| fastapi >= 0.115 | Web framework |
| uvicorn[standard] >= 0.34 | ASGI server |
| anthropic >= 0.52 | Claude API client |
| sqlalchemy >= 2.0 | ORM (async) |
| asyncpg >= 0.30 | PostgreSQL async driver |
| pgvector >= 0.3 | Vector similarity search |
| pydantic >= 2.0 | Data validation |
| pydantic-settings >= 2.0 | Settings from .env |
| python-jose[cryptography] >= 3.3 | JWT tokens |
| argon2-cffi >= 25.1 | Password hashing (primary) |
| passlib[bcrypt] >= 1.7 | Legacy bcrypt support |
| cryptography >= 44.0 | AES-256-GCM encryption |
| alembic >= 1.14 | Database migrations |
| slowapi >= 0.1.9 | Rate limiting |
| email-validator >= 2.0 | Email validation |

### Dev
pytest, pytest-asyncio, httpx, aiosqlite, ruff, mypy

---

## 15. RISKS & MITIGATIONS

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| EU MDR classification as medical device | Blocks launch | Medium | Wellness positioning + healthtech lawyer from start |
| AI hallucination in crisis context | Critical (safety) | High | 3-layer safety (crisis before LLM, guardrails after, disclaimer) |
| No clinical advisor | Credibility loss | Medium | Active search in Phase 1 (AT Ostrava, VFN Praha, CARG) |
| GDPR breach | Legal + reputational | Low (if done right) | Privacy-by-design, AES-256-GCM, zero tracking, pen tests |
| Distribution challenge | Growth stagnation | High | AT ambulance as distribution, families, corporate wellness |
| MVP financing | Blocks build | Medium | Grants as primary (TAČR SIGMA + MSK regional) |

---

## 16. KNOWN ISSUES (Remaining after Session 5)

| Issue | Severity | Notes |
|---|---|---|
| `score_audit()` doesn't validate per-answer values | Low | Validation is at API layer (Pydantic schema) |
| Register endpoint: 2 commits instead of atomic | Low | User + audit log in separate transactions |
| Anonymous users cannot re-authenticate after token loss | Medium | No recovery mechanism without email |
| Alembic migrations pending PostgreSQL instance | Medium | Generated after DB connection (by design) |
| passlib DeprecationWarning on legacy bcrypt detection | Low | Remove passlib after all hashes migrated |
| 28 pre-existing ruff warnings | Low | Mostly screening.py long translated strings |
| Frontend not implemented | High | React Native planned for Phase 2 |
| RAG uses keyword fallback (no embedding model) | Medium | pgvector ready, embedding model deferred |
| Clinical advisor review needed | Critical | crisis.py + guardrails.py need expert review |
| Legal advisor review needed | Critical | AI Act + MDR positioning needs confirmation |

---

## 17. FILE MAP

### Root
`CLAUDE.md` (AI instructions), `README.md` (GitHub landing), `pyproject.toml` (metadata/deps), `.env.example`, `.gitignore`, `alembic.ini`

### Documentation (17 files)
- `docs/project/` — MAIN_DOCUMENT, DECISION_LOG, PERSONAS, ACTION_PLAN
- `docs/business/` — EXECUTIVE_SUMMARY, PITCH_DECK_OUTLINE
- `docs/research/` — deep-research.md, technical-research.md
- `docs/technical/` — ARCHITECTURE, API_REFERENCE, FILE_MAP, SETUP, SAFETY
- `docs/reports/` — Session 1, 3, 4, 5 reports + this project report

### Source Code (27 files)
- `src/main.py` — FastAPI app entry point with middleware, exception handlers, health endpoint
- `src/core/` (11 files) — config, database, security, deps, crisis, crisis_contacts, guardrails, prompts, audit, rate_limit, middleware
- `src/models/` (9 files inc. __init__) — base, user, conversation, tracking, screening, knowledge_base, audit_log, refresh_token
- `src/services/` (6 files inc. __init__) — chat, anthropic_client, rag, screening, tracking
- `src/api/` (9 files inc. __init__) — router, auth, chat, screening, tracking, crisis, admin + schemas/

### Tests (10 files)
conftest.py, test_integration.py, test_crisis.py, test_guardrails.py, test_screening.py, test_security.py, test_tracking_service.py, test_auth.py, test_middleware.py, test_rate_limit.py

---

## 18. CLINICAL KNOWLEDGE BASE (Planned Content)

| Category | Content |
|---|---|
| CBT techniques | Czech-language cognitive-behavioral exercises |
| Screening protocols | AUDIT (WHO), CAGE, DAST |
| Motivational interviewing | MI scripts adapted for Czech context |
| Crisis contacts | 6 verified Czech crisis lines |
| WHO guidelines | Alcohol use disorder guidelines |
| Czech procedures | Doporučené postupy České společnosti pro adiktologii |

---

## 19. PITCH DECK STRUCTURE (12 Slides)

1. Title + tagline
2. Problem (CZ epidemiology: 1.5M risky drinkers, top 5 globally)
3. Market gap (zero CZ-localized AI solution, Monument scandal)
4. Solution (AI recovery guide: AUDIT → AI chat → Tracking → Crisis)
5. Technology (Claude AI + RAG, crisis detection, privacy-first)
6. User personas (Karel, Tereza, Jana)
7. Traction & validation plan (Phase 0-3, AT ambulance pilot)
8. Business model (Grants → B2B pilots → B2C → Insurance/DiGA)
9. Market sizing (TAM/SAM/SOM, DiGA EUR 400-900/patient/year)
10. Competitive moat (5 pillars)
11. Team
12. Ask (seed/grant, MVP 500K-1.5M CZK, timeline)

**Adaptation:** Josef Luks = ROI focus; TAČR = research emphasis; AT ambulance = clinical safety + GDPR.

---

## 20. GLOSSARY

| Term | Meaning |
|---|---|
| AT ambulance | Ambulance pro léčbu závislostí (addiction treatment outpatient clinic) |
| AUDIT | Alcohol Use Disorders Identification Test (WHO, 10 questions) |
| CBT | Cognitive Behavioral Therapy |
| DiGA | Digitale Gesundheitsanwendungen (German digital health apps on prescription) |
| DTx | Digital Therapeutics |
| GDPR | General Data Protection Regulation (EU 2016/679) |
| MI | Motivational Interviewing |
| MDR | Medical Device Regulation (EU 2017/745) |
| RAG | Retrieval-Augmented Generation |
| SaMD | Software as a Medical Device |
| TAČR | Technologická agentura České republiky |
| VZP | Všeobecná zdravotní pojišťovna (Czech general health insurance) |

---

*This report synthesizes all 17 documentation files from the Luceo project as of 2026-04-06, Session 5. It is designed as a single-file knowledge base for Claude AI consumption — comprehensive, structured, and cross-referenced.*
