# LUCEO — Comprehensive Project Report
**Generated:** 2026-04-06 | **For:** Claude AI (Anthropic) consumption
**Purpose:** Complete project context in a single document — vision, business, technical, research, implementation status

---

## TABLE OF CONTENTS

1. [Project Identity & Vision](#1-project-identity--vision)
2. [Team](#2-team)
3. [Problem Statement](#3-problem-statement)
4. [Product & Solution](#4-product--solution)
5. [User Personas](#5-user-personas)
6. [Market & Competition](#6-market--competition)
7. [Regulatory Landscape](#7-regulatory-landscape)
8. [Business Model & Financials](#8-business-model--financials)
9. [Grant Strategy](#9-grant-strategy)
10. [Technical Architecture](#10-technical-architecture)
11. [Safety Systems](#11-safety-systems)
12. [API Reference](#12-api-reference)
13. [Implementation Status](#13-implementation-status)
14. [Development History (Sessions 0–5)](#14-development-history-sessions-05)
15. [Key Decisions](#15-key-decisions)
16. [Risks & Open Questions](#16-risks--open-questions)
17. [Roadmap](#17-roadmap)
18. [File Map](#18-file-map)

---

## 1. PROJECT IDENTITY & VISION

**Name:** Luceo (Latin: *luceo* = I shine, I glow)
**Framing:** Recovery as light, not punishment. "I'm starting to shine" — not "I'm quitting drinking."
**Status:** Ideation/early development phase — living document
**Primary document language:** Czech (technical terms and code in English)

### Vision
Build the best AI-powered addiction support platform in the world — starting in the Czech Republic, with global ambition.

### Mission
Make effective addiction support accessible to everyone — regardless of stigma, clinic availability, or financial situation.

### Positioning
- **Not a chatbot** — a personalized recovery companion
- **Not a therapist replacement** — 24/7 support between sessions
- **Not a detox app** — a long-term partner
- **Wellness app positioning** for MVP (not a medical device) — deliberate regulatory strategy

---

## 2. TEAM

| Role | Person | Background |
|---|---|---|
| **Project Manager / CEO** | Patrik Luks | Software developer, 19, IT entrepreneur, finance background via JPL Servis, entering VŠB-TUO Computer Science → Quantum Computing |
| **Business Manager** | Jarda | Manager, PM collaborator |
| **Potential stakeholder/advisor** | Josef Luks | CFA charterholder, founder of JPL Servis (wealth management, Prague), family connection to PM |
| **Clinical Advisor** | **TBD** | AT physician or addictologist — **critical gap** |
| **Legal Advisor** | **TBD** | Healthtech/medtech lawyer — **critical gap** |

**Critical gaps:** Clinical advisor is a blocker for grants and pilot partnerships. Legal advisor needed for GDPR Article 9, MDR positioning, and AI Act compliance. Specific outreach targets identified: Adiktologická klinika VFN Praha, CARG (Czech Addiction Research Group), AT ambulance Ostrava.

---

## 3. PROBLEM STATEMENT

### Epidemiology — Czech Republic
- **1.3–1.7 million** adults with risky alcohol consumption
- **720–900 thousand** in harmful drinking category
- Czech Republic consistently in **top 5 worldwide** per-capita alcohol consumption
- AT (addiction treatment) clinics are overloaded — doctor sees patient 20 min every 2–4 weeks
- **Stigma** is the primary barrier — "I won't go to a psychologist" but they always have their phone

### Full scope of addiction in CZ

| Addiction Type | Estimated at-risk population |
|---|---|
| Alcohol (risky drinking) | 1.3–1.7 million |
| Alcohol (harmful drinking) | 720–900 thousand |
| Psychoactive medications | 720K–1.2 million |
| Tobacco (daily smokers) | 1.5–2.0 million |
| Gambling (risky) | 60–110 thousand |
| Digital addictions | 360–540 thousand |

### Market Gap
- **Zero** Czech-localized digital solutions for addiction that combine AI and clinical methods
- Foreign apps (Monument, Tempest, Woebot) are not available in Czech and are not culturally adapted
- Czech/Moravian mentality is specific — "nepůjdu k psychologovi" ("I won't go to a psychologist") is stronger than in the US
- Monument was fined $2.5M by FTC in 2024 for sharing health data with advertisers — opens opportunity for privacy-first alternative

---

## 4. PRODUCT & SOLUTION

### Core Product
AI assistant built on Claude API (Anthropic) with RAG architecture over a clinically validated knowledge base, providing:

1. **Personalized support** — conversation adapted to user's recovery phase, triggers, and history
2. **Tracking** — craving logs, sobriety streak, mood tracking, trigger identification
3. **CBT-based interventions** — cognitive-behavioral techniques available 24/7
4. **Crisis protocol** — crisis state detection + escalation to crisis lines and professionals
5. **Education** — knowledge base about addiction, recovery processes, pharmacotherapy
6. **Family module** — support for family members (Phase 2)

### MVP Scope (v1.0)
- Onboarding screening (WHO AUDIT questionnaire for alcohol)
- AI chat assistant (Claude API + RAG)
- Sobriety tracker + craving log
- Crisis detection + crisis contacts (Czech crisis lines)
- Basic CBT techniques (structured exercises)
- GDPR-compliant auth + data storage

### Deliberately Excluded from MVP
- Direct EHR system integration (Phase 2)
- Telemedicine / video with therapist (Phase 2)
- Wearables integration (Phase 3)
- Gamification (Phase 2)
- Family module (Phase 2)

### Primary Focus
**Alcoholism** as the launching vertical. Reasons: largest epidemiological segment, most clinical data and standardized tools (AUDIT, CBT protocols), strongest argument for public health grants.

---

## 5. USER PERSONAS

### Persona 1 — Karel ("The Hidden Drinker") — PRIMARY
- Male, 42–55, Moravia, small town
- Drinks daily (3–4 beers after work, more on weekends)
- Knows it's not normal but won't tell his wife. Won't go to a doctor — stigma
- Would download the app at night, secretly
- **Communication:** No "you're an addict" — say "you want to change your relationship with alcohol." Direct masculine tone. Anonymity as a feature. Practical steps, not emotional analysis.
- **Luceo because:** "I want to try to reduce my drinking. Alone. Without anyone knowing."

### Persona 2 — Tereza ("Millennial Cope") — PRIMARY
- Female, 24–34, Prague, university-educated, white-collar
- Drinks at parties, after stressful days, for anxiety. Tells herself "everyone drinks"
- Digitally native — downloads and tries apps without barriers. Pays for Spotify, Netflix.
- **Communication:** Modern clean UX. Framing: "conscious drinking" / "relationship with alcohol." Empathetic tone. Beautiful data visualizations.
- **Luceo because:** "I want to understand why I drink and try to change. Without dramatization."

### Persona 3 — Jana ("Caring Wife/Mother") — SECONDARY
- Female, 40–60, Moravia
- Partner or child has an alcohol problem
- Looking for information and support for herself as a caregiver
- **Communication:** Clear information about addiction. "How to help a loved one" as an explicit use case. Crisis contacts clearly visible.

### Persona 4 — MUDr. Novák ("AT Clinic Doctor") — B2B
- Doctor/addictologist, 35–55, AT clinic
- Sees patients 20–30 min every 2–4 weeks. No data between sessions.
- Wants better patient outcomes, data from between-session periods
- **Communication:** Clinical terminology. Evidence-based references. Clear AI boundaries. GDPR compliance as a feature.

### Design Principles from Personas
1. Anonymity is a feature, not a disclaimer
2. No-stigma framing — never "addiction" in first contact, use "relationship with alcohol"
3. Mobile-first, nighttime usage — Karel downloads at 23:00 when alone
4. Immediate value — Tereza leaves if first 3 minutes aren't good
5. Crisis is an edge case, not core UX
6. Czech as first language — not translated English

---

## 6. MARKET & COMPETITION

### Global DTx Market 2026
- Estimated **$10–14 billion** globally (19–27% CAGR through 2034)
- Mental health + addiction: ~25% of market, fastest growing segment
- FDA-approved precedents exist (reSET-O for opioid addiction, A-CHESS for alcoholism)
- Germany DiGA: 68 approved apps, ~50% are psychology/mental health, €234M cumulative insurer spending

### Competitive Landscape

| Product | Market | Weakness vs. Luceo |
|---|---|---|
| Monument/Tempest (USA) | US-only, pivoted to broader healthcare | $2.5M FTC fine for data sharing, culturally unadapted |
| Woebot | Global, general mental health | Not addiction-specific, no clinical track record for addictions |
| Reframe (USA) | US, gamification | Shallow clinical foundation, high churn |
| Sober Grid | Global | Peer support only, no AI, no clinical intervention |
| Czech alternatives | CZ | Simple trackers, no AI, no clinical foundation |

**Conclusion:** The Czech-language gap is real. No localized, clinically-oriented AI assistant for addiction exists.

### Competitive Moat (5 Pillars)
1. **Privacy-first** — Monument fined $2.5M for data sharing. Luceo: zero third-party tracking, EU data residency, GDPR by design.
2. **Czech localization** — first mover, no alternative exists
3. **Cultural fit** — Czech/Moravian mentality requires specific approach; anonymity as feature
4. **AI safety** — Claude API (Anthropic) has strongest safety focus; crisis layer before LLM; guardrails
5. **Academic partner** — VŠB-TUO for TAČR grants = structural advantage

---

## 7. REGULATORY LANDSCAPE

### GDPR (EU 2016/679) — CRITICAL
- Health data = Article 9, special category
- Privacy by design mandatory
- Encryption at rest (AES-256) and in transit (TLS)
- EU hosting required (data residency)
- Explicit consent required
- Zero third-party tracking pixels (no Google Analytics, no Meta Pixel)
- Monument/Tempest scandal is a direct example of what happens without privacy-by-design

### EU MDR (2017/745) — HIGH
- If app makes therapeutic claims → may be classified as SaMD (Software as Medical Device) → CE marking required
- **MVP strategy:** position as "wellness and information platform" — no diagnoses, no treatment claims
- Terminology: "support", "companion", "information" — never "therapy", "treatment", "diagnosis"
- This is a deliberate decision for MVP. Phase 2 may include clinical validation and MDR process.

### EU AI Act — HIGH (URGENT)
- **Critical deadline: August 2, 2026** — full compliance for high-risk AI systems
- If Luceo stays as wellness/informational app → "limited risk" → only transparency obligations (user must know they're communicating with AI) — manageable
- If Luceo makes clinical claims or is classified as SaMD → "high-risk" → requires risk management system, technical documentation, data governance, human oversight, post-market monitoring, CE marking
- **Phase 2 (build, summer–fall 2026) directly collides with AI Act deadline**
- **Recommendation:** Wellness positioning for MVP is correct strategy for both MDR and AI Act

### Czech Law 379/2005 Sb. — MEDIUM
- Czech law on health protection against addiction
- Must be reflected in product design

### AI Act Compliance Architecture (Implemented)
- AI Disclaimer shown at conversation start
- Disclaimer reminder every 10 messages
- Audit trail: every message stored with `crisis_level` field
- AuditLog model: logs all AI interactions, crisis detections, logins, data deletions

---

## 8. BUSINESS MODEL & FINANCIALS

### Revenue Streams (by phase)

| Model | Potential | Phase |
|---|---|---|
| **Grants** (EU4Health, TAČR, MZČR, regional) | Realistic for MVP financing | Phase 0–1 |
| **B2B → AT clinic pilot** | Low revenue, high validation | Phase 1 |
| **B2C subscription** | Medium — stigma reduces conversion | Phase 2 |
| **B2B → Insurance (VZP, ZP MV)** | High — motivated to reduce treatment costs | Phase 2–3 |
| **B2G → Municipalities/regions/MZČR** | Solid — public health agenda | Phase 2 |
| **Corporate wellness** | Interesting — companies pay for employees | Phase 3 (consider earlier) |

### Go-to-Market
1. **Grants** → finance MVP (no immediate revenue needed)
2. **One AT pilot partner** → clinical validation + reference + first users
3. **Families** as distribution channel → people with addiction don't seek help themselves, but their loved ones do

### MVP Budget Estimate
| Item | Estimate |
|---|---|
| Development (6 months) | 300–800K CZK |
| Claude API (10K messages/month) | 2–5K CZK/month |
| Legal (GDPR, ToS, healthtech) | 50–150K CZK |
| **Total MVP** | **500K–1.5M CZK** |

### Year 1 Revenue Projection

| Source | Realistic | Ambitious |
|---|---|---|
| MAU after 12 months | 500–2,000 | 5,000–10,000 |
| B2C subscription | 0–40K CZK/month | 100–200K CZK/month |
| B2B (AT pilot) | 0 | 50–150K CZK/year |
| Grants | 500K–2M CZK | 2–5M CZK |

---

## 9. GRANT STRATEGY

### TAČR SIGMA / Nováčci — Most Realistic Path
- Up to **15M CZK** for "nováčci" (newcomers)
- **Critical condition:** requires academic research partner
- **Natural partner:** VŠB-TUO (PM entering the university; FEI has health IT experience)
- Timeline: summer 2026 consortial application

### Regional Grants MSK
- Moravskoslezský kraj has startup support programs
- Luceo as a startup from MSK (Opava) = natural advantage
- Lower competition than national/EU grants

### EU4Health
- Award range: up to €2,000,000
- Too slow and complex for MVP phase (lead time 12–18 months)
- Relevant for Phase 2–3 with institutional partner

### EIC Accelerator (Horizon Europe)
- Up to €2.5M grant or €0.5–15M investment
- "Seal of Excellence" → alternative financing via NPO even if EIC fails
- Requires validation data from pilot (Phase 2–3)

### VZP (Czech Health Insurance)
- VZP operates mental health program with prevention fund
- Already supports DeePsy (VUT Brno + Masaryk University) — precedent exists
- Realistic path: pilot data → VZP prevention department → prevention fund contribution
- Czech Republic has no DiGA equivalent — gap but also opportunity

### German DiGA Model — Strategic Long-term Opportunity
- "Apps on prescription" reimbursed by statutory health insurance (73M insured individuals)
- 68 approved DiGA, cumulative €234M insurer spending
- **Czech precedent:** Vitadio (CZ diabetes management) obtained DiGA approval — path from CZ to DiGA exists
- DiGA pricing: €400–900/patient/year
- Requires: CE marking (MDR Class I/IIa) + clinical study proving "positive healthcare effect"
- **Luceo DiGA path:** MVP (2026) → pilot study (2027) → MDR CE (2027–28) → DiGA BfArM (2028) → German market

---

## 10. TECHNICAL ARCHITECTURE

### Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| **LLM** | Claude API (Anthropic) | Core AI engine |
| **RAG** | pgvector (PostgreSQL) | Semantic search over clinical knowledge base |
| **Backend** | Python (FastAPI) | Decided DEC-008, async-native |
| **Database** | PostgreSQL + pgvector | User data + vector store |
| **Auth** | Custom JWT | GDPR-compliant, refresh tokens |
| **Frontend** | React Native (mobile-first) | iOS + Android (TODO) |
| **Hosting** | EU region mandatory | GDPR requirement |

### System Architecture Diagram

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
│  │  AuditLog, RefreshToken                           │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                   │
│           PostgreSQL + pgvector                          │
└─────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

**API Layer (`src/api/`):**
- HTTP endpoint definitions (routes)
- Request validation (Pydantic v2 schemas in `src/api/schemas/`)
- Dependency injection (auth, database session)
- No business logic — delegates to services

**Core Layer (`src/core/`):**
- `config.py` — Settings via pydantic-settings, reads `.env`
- `database.py` — AsyncEngine, session factory, `get_db()` dependency
- `security.py` — JWT (HS256), argon2 hashing (bcrypt legacy compat), AES-256-GCM encryption
- `crisis.py` — Crisis detection (zero dependencies, keyword matching, pre-LLM)
- `crisis_contacts.py` — Czech crisis phone numbers (hardcoded Pydantic models)
- `guardrails.py` — Post-LLM output filtering (diagnoses, medications)
- `prompts.py` — System prompt, AI disclaimer, disclaimer reminder
- `deps.py` — `get_current_user` FastAPI dependency
- `audit.py` — Audit trail logging (AI Act compliance)
- `rate_limit.py` — Rate limiting with JWT/IP key extraction (slowapi)
- `middleware.py` — Request logging, security headers (CSP, HSTS, Permissions-Policy)

**Services Layer (`src/services/`):**
- `chat.py` — Chat orchestrator (crisis → RAG → LLM → guardrails → store)
- `anthropic_client.py` — Thin Claude API wrapper, lazy singleton
- `rag.py` — Knowledge base retrieval (keyword fallback for MVP)
- `screening.py` — WHO AUDIT questionnaire scoring (10 questions)
- `tracking.py` — Sobriety streak calculation, SQL-aggregated summaries

**Models Layer (`src/models/`):**
- SQLAlchemy 2.0 ORM models with UUID v4 primary keys
- `BaseModel` provides id, created_at, updated_at
- Field-level encryption for sensitive data (messages, notes)
- 9 tables: users, conversations, messages, sobriety_checkins, craving_events, screening_results, knowledge_documents, audit_logs, refresh_tokens

### Chat Message Flow

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

### Security Architecture

| Layer | Mechanism | Purpose |
|---|---|---|
| Transport | HTTPS (infrastructure) | Encryption in transit |
| Authentication | JWT HS256 (1h) + refresh tokens (30d, SHA-256) | User identity |
| Password hashing | argon2-cffi (primary) + passlib/bcrypt (legacy compat) | Credential security |
| Data at rest | AES-256-GCM per-field | GDPR encryption |
| Crisis detection | Keyword matching pre-LLM | Immediate safety |
| Output guardrails | Regex post-LLM | Prevent diagnoses/medications |
| Audit trail | AuditLog model | AI Act compliance |
| IP logging | SHA-256 hash only | GDPR — no raw IPs |
| User deletion | Soft delete + PII wipe (7 tables) | GDPR Art. 17 |
| CORS | Middleware (env-configurable) | Cross-origin protection |
| Security headers | CSP, HSTS (prod), X-Frame-Options, X-Content-Type-Options, Permissions-Policy, Referrer-Policy | Content security |
| Rate limiting | slowapi (JWT/IP key, per-endpoint) | Abuse prevention |
| Global exception handler | ValidationError → 422, SQLAlchemyError → 500, Exception → 500 | Error consistency |

### Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Primary keys | UUID v4 | GDPR portability, no enumeration |
| Chat storage | AES-256-GCM field-level | Defense in depth |
| Crisis detection | Keyword matching (not ML) | Deterministic, auditable |
| Guardrails | 2 layers (prompt + post-LLM regex) | Belt and suspenders |
| Email | Optional (nullable) | Anonymity per Karel persona |
| User deletion | Soft delete + PII wipe | Audit trail + GDPR Art. 17 |
| System prompt | Constant in code | Version controlled |
| Embedding model | Deferred (keyword fallback) | MVP without embedding infra |
| Password hashing | argon2-cffi (primary) | passlib/bcrypt deprecated; backward compat maintained |

---

## 11. SAFETY SYSTEMS

Safety is the #1 priority. The system uses multiple independent layers — if one fails, others catch it.

### Layer 1: Crisis Detection (`src/core/crisis.py`)
- **Zero dependencies** — no database, no API calls, no imports from services/models
- **Runs BEFORE the LLM** — if DB or API is down, crisis detection still works
- **Deterministic** — regex pattern matching, not ML. Output is auditable
- **Fast** — <1ms execution time
- **Clinical advisor reviewable** — keyword lists are human-readable

| Level | Example Triggers | Response |
|---|---|---|
| **CRITICAL** | "chci zemřít", "sebevražda", "kill myself" | Predefined message + all crisis contacts. NO LLM call. |
| **HIGH** | "chci si ublížit", "předávkovat se", "self-harm" | Predefined message + key contacts. NO LLM call. |
| **MEDIUM** | "relaps", "chci pít", "neschopnost dál" | LLM responds normally, crisis resources appended. |
| **NONE** | Normal conversation | Normal LLM response. |

- Czech text is NFKD-normalized so "chci zemřít" and "chci zemrit" both trigger detection
- Zero-width character bypass prevention

### Layer 2: System Prompt (`src/core/prompts.py`)
Instructs Claude to: never diagnose, never recommend specific medications/dosages, immediately refer to emergency services for withdrawal symptoms, use empathetic non-stigmatizing language, stay within RAG context, respond in Czech unless user writes in English.

### Layer 3: Output Guardrails (`src/core/guardrails.py`)
Post-LLM regex filter catches responses that slip past the system prompt:
- **Diagnostic patterns:** ICD-10 codes (F10.x-F19.x), "diagnostikuji", "vaše diagnóza", "trpíte", "jsi alkoholik"
- **Medication patterns:** naltrexon, acamprosat, disulfiram, antabus, campral, benzodiazepines (diazepam, lorazepam, etc.), SSRIs (sertralin, fluoxetin, etc.), dosage patterns ("X mg denně")
- **When triggered:** Unsafe response replaced with safe fallback: "Na toto se prosím zeptej svého lékaře..."
- NFKD normalization (diacritics-insensitive matching)
- Feminine Czech forms covered (závislá, alkoholička)

### Crisis Contacts (hardcoded)
- Linka bezpečí: 116 111 (24/7)
- Krizová pomoc: 116 123 (24/7)
- Národní linka pro odvykání: 800 350 000
- Podané ruce: 549 257 217
- Záchranná služba: 155
- Tísňová linka: 112

### TODO for Clinical Advisor (BEFORE production)
- Review all keyword patterns for completeness and false positive rate
- Review all predefined crisis responses for clinical appropriateness
- Add patterns for drug-specific crisis (beyond alcohol)
- Add patterns for domestic violence context

---

## 12. API REFERENCE

**Base URL:** `/api/v1`
**Total endpoints:** 21 (20 in routers + /health)
**All endpoints have `response_model`** (Pydantic schemas)

### Authentication
Bearer token flow: register/login → access_token (1h) + refresh_token (30d) → refresh rotates both tokens.

### Rate Limits

| Endpoint | Limit |
|---|---|
| `POST /auth/register`, `/login` | 5/minute |
| `POST /auth/refresh` | 10/minute |
| `POST /chat/.../messages` | 20/minute |
| Tracking, screening write endpoints | 60/minute |
| `GET /admin/export-my-data` | 5/minute |

### Endpoint Summary

**Auth (`/api/v1/auth`):**
- `POST /register` — create account (email optional for anonymity), returns tokens + AI disclaimer
- `POST /login` — authenticate, returns tokens
- `POST /refresh` — rotate token pair
- `POST /logout` — revoke refresh token
- `GET /me` — user profile
- `DELETE /me` — GDPR Art. 17 erasure (soft delete + PII wipe across 7 tables)

**Chat (`/api/v1/chat`):**
- `POST /conversations` — create conversation, returns AI Act disclaimer
- `POST /conversations/{id}/messages` — send message, get AI response (with crisis detection)
- `GET /conversations` — list conversations (paginated: skip/limit, max 100)

**Screening (`/api/v1/screening`):**
- `GET /questionnaires/audit` — WHO AUDIT questionnaire, 10 questions (public, no auth)
- `POST /questionnaires/audit` — submit answers, get risk assessment
- `GET /results` — screening history (paginated)

Risk levels: `low_risk` (0-7), `hazardous` (8-15), `harmful` (16-19), `possible_dependence` (20-40)

**Tracking (`/api/v1/tracking`):**
- `POST /checkin` — daily sobriety check-in (upsert), mood 1-5, energy_level 1-5
- `GET /checkin/today` — check if today is logged
- `POST /cravings` — log craving event (intensity 1-10, trigger_category, outcome)
- `GET /cravings` — craving history (paginated)
- `GET /summary` — tracking summary for last N days (SQL-aggregated)
- `GET /streak` — current sobriety streak

Trigger categories: `stress`, `social`, `emotional`, `habitual`, `environmental`, `other`

**Crisis (`/api/v1/crisis`):**
- `GET /contacts` — Czech crisis phone numbers (public, no auth)

**Admin (`/api/v1/admin`):**
- `GET /export-my-data` — GDPR Art. 15 full data export (rate limited 5/min)

**Health:**
- `GET /health` — `{"status": "ok", "version": "0.1.0"}`

---

## 13. IMPLEMENTATION STATUS (After Session 5 — April 6, 2026)

### Metrics

| Metric | Value |
|---|---|
| **Tests** | 135 (135 pass, 0 skip, 0 fail) |
| **Integration tests** | 31 (full HTTP flows via httpx AsyncClient) |
| **API routers** | 6 (auth, chat, screening, tracking, crisis, admin) |
| **Endpoints** | 21 (20 in routers + /health) |
| **Endpoints with response_model** | 21/21 |
| **Endpoints with pagination** | 3 (conversations, cravings, screening results) |
| **DB tables** | 9 |
| **src/ lines** | ~2,574 |
| **tests/ lines** | ~1,436 |
| **Ruff warnings** | 26 (all pre-existing: long Czech strings in screening.py, StrEnum in crisis.py) |

### What's Implemented
- Complete auth system: JWT (1h) + refresh tokens (30d, SHA-256, rotation)
- Password hashing: argon2-cffi (primary) + passlib/bcrypt (legacy backward compatibility)
- AES-256-GCM field-level encryption for sensitive data
- Crisis detection (zero-dependency, pre-LLM, CZ+EN keywords, zero-width char bypass protection)
- Output guardrails (post-LLM regex filter with NFKD normalization)
- WHO AUDIT screening (10-question, boundary scoring, Q9/Q10 validation)
- Sobriety tracking with streak calculation
- Craving logging with trigger categorization
- SQL-aggregated tracking summaries (func.count, func.avg, GROUP BY)
- CheckConstraint on mood (1-5), energy_level (1-5), intensity (1-10)
- GDPR export (Art. 15) and erasure (Art. 17) with 7-table cascade
- Audit logging on all critical endpoints (AI Act compliance)
- Rate limiting (slowapi, per-endpoint, JWT/IP key)
- Security headers (CSP, HSTS, X-Frame-Options, Permissions-Policy, Referrer-Policy)
- Global exception handler (ValidationError, SQLAlchemyError, generic Exception)
- Alembic initialized (async template, migrations pending PostgreSQL)
- All FK have ondelete (CASCADE or SET NULL for audit_log)

### What's NOT Implemented
- **Frontend** — React Native (TODO)
- **RAG embedding** — keyword fallback for MVP (pgvector ready but no embeddings)
- **PostgreSQL deployment** — using SQLite for tests, Alembic migrations pending
- **Clinical knowledge base content** — schema ready, content pending clinical advisor
- **CBT exercise modules** — not started
- **EHR integration** — Phase 2
- **Telemedicine** — Phase 2
- **Family module** — Phase 2

---

## 14. DEVELOPMENT HISTORY (Sessions 0–5)

### Session 0 — Founding (April 5, 2026)
- Initial project documentation created
- All founding decisions (DEC-001 through DEC-008)
- Core models, API endpoints, crisis detection, guardrails implemented
- 49 tests, 19 endpoints, 8 tables, ~1,850 lines src/

### Session 1 — Security Hardening (April 5, 2026)
- Refresh tokens (SHA-256, 30d, rotation)
- Rate limiting (slowapi)
- Alembic initialization
- Comprehensive audit + bug fixes (10 issues fixed)
- 67 tests (+18), 21 endpoints (+2), 9 tables (+1), ~2,188 lines src/

### Session 3 — Security Audit (April 5, 2026)
- Complete security audit: 3 CRITICAL, 5 HIGH, 9 MEDIUM issues found and fixed
- Critical: message duplication in Claude API, str.format() crash on RAG docs, guardrails diacritics bypass
- High: GDPR export missing encrypted fields, timing oracle on login, Anthropic client error handling
- +36 new tests (including test_security.py, test_tracking_service.py)
- README.md created
- 103 tests, ~2,298 lines src/

### Session 4 — FK Cascades & Integration Tests (April 6, 2026)
- FK ondelete on all foreign keys
- date.today() → UTC fix
- 31 integration tests (full HTTP flows)
- Register race condition fix
- Anthropic IndexError guard
- RAG graceful degradation
- 134 tests, 2,318 lines src/

### Session 5 — Response Models & Argon2 (April 6, 2026)
- Response models on all 21 endpoints (9 previously missing)
- Pagination on 3 list endpoints
- SQL aggregation for tracking summary (replaced in-memory)
- CheckConstraint on mood, energy_level, intensity
- Audit logging on chat/tracking/craving endpoints
- Global exception handler
- GDPR export rate limiting
- passlib/bcrypt → argon2-cffi migration (with backward compatibility)
- 135 tests (135 pass, 0 skip), ~2,574 lines src/

---

## 15. KEY DECISIONS

| ID | Decision | Rationale | Date |
|---|---|---|---|
| DEC-001 | Name: **Luceo** | Global, no stigma association, premium feel, recovery as light | 2026-04-05 |
| DEC-002 | AI engine: **Claude API (Anthropic)** | PM experience, safety focus, well-documented RAG | 2026-04-05 |
| DEC-003 | Primary vertical: **Alcoholism** | Largest CZ segment, most clinical data, strongest grant argument | 2026-04-05 |
| DEC-004 | Positioning: **Wellness app** (not medical device) | Avoids MDR CE marking requirements for MVP; legal if no diagnosis/treatment claims | 2026-04-05 |
| DEC-005 | GTM: **Grants → AT pilot → scale** | B2C fails without brand awareness; grants don't require product; AT clinic = validation + distribution | 2026-04-05 |
| DEC-006 | Team: **Patrik (PM) + Jarda (business)** | Clinical + legal advisors are critical gaps for Phase 1 | 2026-04-05 |
| DEC-007 | Session 0 is founding document | Traceable reasoning for all key decisions | 2026-04-05 |
| DEC-008 | Backend: **Python (FastAPI)** | Stronger AI/ML ecosystem, faster RAG prototyping, PM preference | 2026-04-05 |

---

## 16. RISKS & OPEN QUESTIONS

### Risks

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| EU MDR classification as medical device | Blocks launch | Medium | Wellness positioning; lawyer from start |
| AI hallucination in crisis context | Critical | High | Crisis layer before LLM; guardrails; disclaimer |
| No clinical advisor | Loss of credibility | Medium | Active search from Phase 1; specific targets identified |
| GDPR violation | Legal, reputational | Low (if done right) | Privacy by design from start |
| Distribution — getting app to users | Growth stagnation | High | AT clinic as distribution; families |
| MVP funding | Blocks build | Medium | Grants as primary path |

### Known Technical Issues (Remaining)
- `score_audit()` doesn't validate per-answer values (validation at API layer)
- Register endpoint: 2 commits instead of atomic operation (user + audit log)
- Anonymous users cannot re-authenticate after token loss
- Alembic migrations pending PostgreSQL instance
- passlib DeprecationWarning on legacy bcrypt hash detection (remove passlib after all hashes migrated)

### Open Questions (Decisions Needed)
- Legal entity — s.r.o. or a.s.? Part of JPL Servis ecosystem or standalone?
- Josef Luks — investor, advisor, or just a contact?
- Mobile-first or web-first in MVP?
- Freemium or subscription from start?
- App Store name: "Luceo" or add subtitle for SEO?
- Corporate wellness in Phase 2 instead of Phase 3?

---

## 17. ROADMAP

### Phase 0 — Foundations (April 2026, parallel with high school exams)
- [x] Backend MVP development (Sessions 0–5)
- [ ] Register domain luceo.app
- [ ] Contact Jarda — initiate collaboration
- [ ] Contact clinical advisor (AT Ostrava, VFN Praha, CARG)
- [ ] Legal scan with healthtech lawyer (1 session, ~500–1000 EUR)
- [ ] Vision & Scope document for Jarda and Josef

### Phase 1 — Validation (May–June 2026, post graduation)
- [ ] Pitch to Josef in Prague (JPL Servis) — seed funding or advisory
- [ ] Find clinical advisor (AT doctor or addictologist)
- [ ] Lock down MVP scope
- [ ] Start building clinical knowledge base (CBT, AUDIT, Czech sources)
- [ ] Pitch deck v1 for grants
- [ ] Contact: VŠB-TUO research office, TAČR, regional MSK grants
- [ ] Legal entity decision

### Phase 2 — Build (Summer–Fall 2026)
- [ ] React Native frontend
- [ ] PostgreSQL deployment + Alembic migrations
- [ ] Pilot partner: one AT clinic (Ostrava or Prague)
- [ ] First users, first feedback
- [ ] TAČR grant application (with VŠB-TUO as research partner)
- [ ] GDPR compliance finalization (DPA, ToS, disclaimer, privacy policy)

### Phase 3 — Scale (2027+)
- [ ] Clinical validation (pilot RCT study)
- [ ] B2B expansion (insurance, corporate wellness)
- [ ] Internationalization (SK first, then DE via DiGA, PL)
- [ ] MDR process (if pursuing pharmaceutical grade)
- [ ] VZP prevention fund application

### KPIs

**MVP KPIs:**
- DAU/MAU (active users)
- Retention rate (day 7, day 30)
- Average sobriety streak length
- Crisis escalation rate
- User satisfaction (NPS)

**Clinical KPIs (post-pilot):**
- Program adherence
- Relapse reduction vs. control group
- AUDIT score improvement
- Successful crisis interventions

---

## 18. FILE MAP

### Root
| File | Purpose |
|---|---|
| `CLAUDE.md` | Instructions for AI assistants working on this project |
| `README.md` | GitHub landing page (English) |
| `pyproject.toml` | Project metadata, dependencies (FastAPI, SQLAlchemy, anthropic, argon2-cffi, etc.) |
| `.env.example` | Environment variable template |
| `alembic.ini` | Alembic configuration |

### `docs/project/`
| File | Purpose |
|---|---|
| `MAIN_DOCUMENT.md` | **Primary source of truth** — vision, team, problem, solution, roadmap |
| `DECISION_LOG.md` | Log of all key decisions (DEC-001 through DEC-008) |
| `PERSONAS.md` | User personas (Karel, Tereza, Jana, MUDr. Novák) |
| `ACTION_PLAN.md` | Consolidated action plan with phases and grant details |

### `docs/business/`
| File | Purpose |
|---|---|
| `EXECUTIVE_SUMMARY.md` | 2-page summary for business partners |
| `PITCH_DECK_OUTLINE.md` | 12-slide pitch deck skeleton |

### `docs/research/`
| File | Purpose |
|---|---|
| `deep-research.md` | DTx market, competition, regulation, grants (strategic) |
| `technical-research.md` | Clinical procedures, architecture, validation, regulatory (technical) |

### `docs/technical/`
| File | Purpose |
|---|---|
| `ARCHITECTURE.md` | System architecture, chat flow, security layers |
| `API_REFERENCE.md` | Complete API endpoint documentation |
| `FILE_MAP.md` | Complete file listing with purposes |
| `SETUP.md` | Development setup instructions |
| `SAFETY.md` | Crisis detection and guardrails documentation |

### `docs/reports/`
| File | Purpose |
|---|---|
| `REPORT_2026-04-05.md` | Session 1 — refresh tokens, rate limiting, Alembic |
| `REPORT_2026-04-05_s3.md` | Session 3 — security audit, test expansion, README |
| `REPORT_2026-04-06_s4.md` | Session 4 — FK cascades, integration tests |
| `REPORT_2026-04-06_s5.md` | Session 5 — response models, pagination, argon2 |

### `src/core/` — Core Logic (11 modules)
| File | Purpose |
|---|---|
| `config.py` | Settings (pydantic-settings, .env), production validation |
| `database.py` | AsyncEngine, session factory, `get_db()` |
| `security.py` | JWT, argon2 hash/verify, AES-256-GCM |
| `deps.py` | `get_current_user` dependency |
| `crisis.py` | Crisis detection (ZERO external deps, SAFETY-CRITICAL) |
| `crisis_contacts.py` | Czech crisis phone numbers |
| `guardrails.py` | Post-LLM output filter |
| `prompts.py` | System prompt, disclaimers |
| `audit.py` | Audit trail logging |
| `rate_limit.py` | Rate limiting key function |
| `middleware.py` | Request logging, security headers |

### `src/models/` — Database Models (8 model files, 9 tables)
| File | Table(s) |
|---|---|
| `base.py` | Base (UUID PK, timestamps) |
| `user.py` | `users` |
| `conversation.py` | `conversations`, `messages` |
| `tracking.py` | `sobriety_checkins`, `craving_events` |
| `screening.py` | `screening_results` |
| `knowledge_base.py` | `knowledge_documents` (pgvector) |
| `audit_log.py` | `audit_logs` |
| `refresh_token.py` | `refresh_tokens` |

### `src/services/` — Business Logic (5 modules)
| File | Function |
|---|---|
| `chat.py` | Chat orchestrator (crisis → RAG → LLM → guardrails → store) |
| `anthropic_client.py` | Claude API wrapper, lazy singleton |
| `rag.py` | Knowledge base retrieval (keyword fallback) |
| `screening.py` | WHO AUDIT scoring |
| `tracking.py` | Streak calculation, SQL-aggregated summaries |

### `src/api/` — HTTP Endpoints (6 routers)
| File | Prefix | Auth | Endpoints |
|---|---|---|---|
| `auth.py` | `/api/v1/auth` | Mixed | register, login, me, delete, refresh, logout |
| `chat.py` | `/api/v1/chat` | Yes | create conversation, send message, list conversations |
| `screening.py` | `/api/v1/screening` | Mixed | AUDIT questionnaire, submit, results |
| `tracking.py` | `/api/v1/tracking` | Yes | checkin, today, cravings, craving list, summary, streak |
| `crisis.py` | `/api/v1/crisis` | No | contacts |
| `admin.py` | `/api/v1/admin` | Yes | export-my-data |

### `src/api/schemas/` — Pydantic Request/Response Models (7 files)
| File | Models |
|---|---|
| `auth.py` | RegisterRequest, LoginRequest, TokenResponse, UserResponse, RefreshRequest |
| `chat.py` | SendMessageRequest, ChatResponse, ConversationResponse, ConversationListItem |
| `screening.py` | AuditSubmission, AuditResultResponse, AuditQuestionsResponse, ScreeningResultItem |
| `tracking.py` | CheckinRequest/Response, TodayCheckinResponse, CravingRequest/Response, CravingListItem, TrackingSummary, StreakResponse |
| `admin.py` | GDPRExportResponse and nested export models |
| `crisis.py` | CrisisContactsResponse |

### `tests/` — 135 Tests
| File | Tests | Coverage |
|---|---|---|
| `conftest.py` | — | Shared fixtures: async SQLite, mock Anthropic, all 9 model imports |
| `test_integration.py` | 31 | Full HTTP flows (auth, tracking, screening, crisis, GDPR, chat, security headers) |
| `test_crisis.py` | 32 | Crisis detection: normalization, bypass prevention, all levels |
| `test_guardrails.py` | 15 | Diagnostic and medication patterns, diacritics, feminine forms |
| `test_screening.py` | 13 | AUDIT scoring boundaries, Q9/Q10 validation |
| `test_auth.py` | 7 | Refresh token lifecycle |
| `test_rate_limit.py` | 3 | Rate limit key extraction |
| `test_middleware.py` | 7 | Security headers (CSP, HSTS, Permissions-Policy) |
| `test_security.py` | 13 | AES-256-GCM, JWT, argon2 hashing, production config validation |
| `test_tracking_service.py` | 10 | Sobriety streak, tracking summary, SQL aggregation |

---

## DEPENDENCIES

```toml
# Core
fastapi>=0.115
uvicorn[standard]>=0.34
anthropic>=0.52
sqlalchemy>=2.0
asyncpg>=0.30
pgvector>=0.3
pydantic>=2.0
pydantic-settings>=2.0
python-jose[cryptography]>=3.3
argon2-cffi>=25.1
passlib[bcrypt]>=1.7        # Legacy support for existing bcrypt hashes
cryptography>=44.0
alembic>=1.14
slowapi>=0.1.9
email-validator>=2.0

# Dev
pytest>=8.0
pytest-asyncio>=0.24
httpx>=0.28
aiosqlite>=0.20
ruff>=0.9
mypy>=1.14
```

---

*This report consolidates all documentation from the `docs/` directory (17 source files across project, business, research, technical, and reports subdirectories) plus implementation state from the codebase as of Session 5 (April 6, 2026). It is designed to provide complete project context for AI assistants working with the Luceo project.*
