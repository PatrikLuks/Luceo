# LUCEO — Projektový kontext

## O projektu
**Luceo** (latina: svítím/zářím) je AI-powered platforma pro podporu lidí bojujících se závislostí.
Primární zaměření MVP: **alkoholismus** v ČR. Globální ambice.

## Klíčové principy
- **Není to chatbot** — je to personalizovaný průvodce recovery
- **Není to náhrada terapeuta** — je to 24/7 podpora mezi sezeními
- **Wellness app positioning** — ne medical device (pro MVP fázi)
- **Privacy-first** — GDPR, EU hosting, zero third-party tracking
- Recovery jako světlo, ne trest. Bez stigmatu.

## Tým
- **Patrik** — PM/CEO, software developer, 19 let, VŠB-TUO Informatika
- **Jarda** — Business Manager
- **Josef Luks** — potenciální advisor/stakeholder (CFA, JPL Servis)
- **Clinical Advisor** — TBD (kritická mezera)
- **Legal Advisor** — TBD (kritická mezera)

## Technický stack
- **LLM:** Claude API (Anthropic) s RAG architekturou
- **RAG:** pgvector (PostgreSQL)
- **Backend:** Python (FastAPI) — rozhodnuto DEC-008
- **DB:** PostgreSQL + pgvector
- **Auth:** Vlastní JWT (GDPR-compliant)
- **Frontend:** React Native (mobile-first)
- **Hosting:** EU region povinně

## AI architektura — guardrails
- Crisis detection layer běží PŘED LLM odpovědí
- Luceo nikdy nediagnostikuje ani nedoporučuje konkrétní léky
- Vždy odkáže na odborníka při přesahu kompetencí
- Disclaimer v každé session

## Regulační kontext
- **GDPR** — zdravotní data = Article 9, special category (KRITICKÁ)
- **EU MDR** — wellness positioning pro MVP (ne SaMD)
- **EU AI Act** — deadline 2. srpna 2026 pro high-risk AI systémy
- **Zákon 379/2005 Sb.** — ČR zákon o ochraně zdraví

## Fáze projektu
- **Fáze 0** (duben 2026): Foundations — dokumentace, legal scan, kontakty
- **Fáze 1** (květen–červen 2026): Validation — pitch, clinical advisor, granty
- **Fáze 2** (léto–podzim 2026): Build — MVP development, pilot
- **Fáze 3** (2027): Scale — klinická validace, B2B, internacionalizace

## Struktura dokumentů

### Projektová dokumentace (`docs/project/`)
| Soubor | Účel |
|---|---|
| `docs/project/MAIN_DOCUMENT.md` | **Primární zdroj pravdy** — vize, tým, problém, řešení, roadmapa |
| `docs/project/DECISION_LOG.md` | Log všech klíčových rozhodnutí (DEC-001 až DEC-008) |
| `docs/project/PERSONAS.md` | User persony (Karel, Tereza, Jana, MUDr. Novák) |
| `docs/project/ACTION_PLAN.md` | Konsolidovaný akční plán s konkrétními kroky |

### Business dokumenty (`docs/business/`)
| Soubor | Účel |
|---|---|
| `docs/business/EXECUTIVE_SUMMARY.md` | 2-stránkový executive summary pro partnery |
| `docs/business/PITCH_DECK_OUTLINE.md` | 12-slide pitch deck |

### Výzkum (`docs/research/`)
| Soubor | Účel |
|---|---|
| `docs/research/deep-research.md` | Hloubkový výzkum — DTx trh, konkurence, regulace, granty |
| `docs/research/technical-research.md` | Technický výzkum — klinické postupy, architektura, validace |

### Technická dokumentace (`docs/technical/`)
| Soubor | Účel |
|---|---|
| `docs/technical/ARCHITECTURE.md` | Systémová architektura, vrstvy, chat flow, bezpečnost |
| `docs/technical/API_REFERENCE.md` | Kompletní API reference všech endpointů |
| `docs/technical/FILE_MAP.md` | Mapa všech souborů v projektu s popisem |
| `docs/technical/SETUP.md` | Dev setup, spuštění, env variables |
| `docs/technical/SAFETY.md` | Crisis detection, guardrails, bezpečnostní dokumentace |

### Reporty (`docs/reports/`)
| Soubor | Účel |
|---|---|
| `docs/reports/REPORT_2026-04-05.md` | Session 1 report — refresh tokens, rate limiting, Alembic, security |

## Backend architektura (src/)
```
src/
├── main.py                  # FastAPI entry point
├── core/                    # Core logic (config, security, crisis detection)
│   ├── config.py            #   Settings (pydantic-settings, .env)
│   ├── database.py          #   AsyncEngine, session factory
│   ├── security.py          #   JWT, argon2, AES-256-GCM, refresh tokens
│   ├── deps.py              #   get_current_user dependency
│   ├── crisis.py            #   Crisis detection (ZERO DEPS)
│   ├── crisis_contacts.py   #   Czech crisis phone numbers
│   ├── guardrails.py        #   Post-LLM output filter
│   ├── prompts.py           #   System prompt, disclaimers
│   ├── audit.py             #   Audit trail logging
│   ├── rate_limit.py        #   Rate limiting (slowapi)
│   └── middleware.py         #   Request logging, security headers (CSP, HSTS)
├── models/                  # SQLAlchemy 2.0 ORM models
│   ├── base.py              #   Base with UUID PK, timestamps
│   ├── user.py              #   User (email optional!)
│   ├── conversation.py      #   Conversation + Message (encrypted)
│   ├── tracking.py          #   SobrietyCheckin + CravingEvent
│   ├── screening.py         #   ScreeningResult (AUDIT)
│   ├── knowledge_base.py    #   KnowledgeDocument (pgvector)
│   ├── audit_log.py         #   AuditLog (AI Act compliance)
│   └── refresh_token.py     #   RefreshToken (SHA-256 hashed)
├── services/                # Business logic
│   ├── chat.py              #   Chat orchestrator (core!)
│   ├── anthropic_client.py  #   Claude API wrapper
│   ├── rag.py               #   Knowledge base retrieval
│   ├── screening.py         #   WHO AUDIT scoring
│   └── tracking.py          #   Streak calculation, summaries
└── api/                     # HTTP endpoints
    ├── router.py             #   All routers aggregated
    ├── auth.py               #   /api/v1/auth/*
    ├── chat.py               #   /api/v1/chat/*
    ├── screening.py          #   /api/v1/screening/*
    ├── tracking.py           #   /api/v1/tracking/*
    ├── crisis.py             #   /api/v1/crisis/*
    ├── admin.py              #   /api/v1/admin/* (GDPR export)
    └── schemas/              #   Pydantic request/response models
```

## Kritické bezpečnostní moduly
- `src/core/crisis.py` — **SAFETY-CRITICAL**. Intentionally zero dependencies. Runs before LLM.
- `src/core/guardrails.py` — Post-LLM filter. Prevents diagnoses and medication recommendations.
- Oba moduly vyžadují review clinical advisorem před production deploymentem.

## Jazyk
- Primární jazyk dokumentace: **čeština**
- Technické termíny: angličtina
- Kód a komentáře: angličtina

## Stav implementace (Session 5)
- **135 testů** (135 pass, 0 skip) — unit testy + 31 integration testů (httpx AsyncClient)
- **6 API routerů** — auth, chat, screening, tracking, crisis, admin
- **21 endpointů** celkem (20 v routerech + /health), **všechny s response_model**
- **9 DB tabulek** — users, conversations, messages, sobriety_checkins, craving_events, screening_results, knowledge_documents, audit_logs, refresh_tokens
- **Session 5 změny:** response modely na všech endpointech, pagination (3 list endpointy), SQL agregace v tracking summary, CheckConstraint na mood/energy_level/intensity, audit logging na chat/tracking/craving, globální exception handler, rate limit na GDPR export, argon2-cffi migrace (bcrypt backward compat)
- **Auth:** JWT access tokens (1h) + refresh tokens (30d, SHA-256 hashed, rotation)
- **Password hashing:** argon2-cffi (primary) + passlib/bcrypt (legacy backward compat)
- **Alembic:** inicializován (async template), env.py nakonfigurován, migrace se generují po připojení k PostgreSQL
- Frontend: TODO (React Native)
