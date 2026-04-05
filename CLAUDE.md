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

### Projektová dokumentace (root)
| Soubor | Účel |
|---|---|
| `LUCEO_MAIN_DOCUMENT_v1.md` | **Primární zdroj pravdy** — vize, tým, problém, řešení, roadmapa |
| `LUCEO_DECISION_LOG.md` | Log všech klíčových rozhodnutí (DEC-001 až DEC-008) |
| `LUCEO_PERSONAS.md` | User persony (Karel, Tereza, Jana, MUDr. Novák) |
| `LUCEO_ACTION_PLAN.md` | Konsolidovaný akční plán s konkrétními kroky |
| `luceo-deep-research.md` | Hloubkový výzkum — DTx trh, konkurence, regulace, granty |
| `zprava-hluboky-vyzkum.md` | Technický výzkum — klinické postupy, architektura, validace |

### Technická dokumentace (`docs/`)
| Soubor | Účel |
|---|---|
| `docs/ARCHITECTURE.md` | Systémová architektura, vrstvy, chat flow, bezpečnost |
| `docs/API_REFERENCE.md` | Kompletní API reference všech endpointů |
| `docs/FILE_MAP.md` | Mapa všech souborů v projektu s popisem |
| `docs/SETUP.md` | Dev setup, spuštění, env variables |
| `docs/SAFETY.md` | Crisis detection, guardrails, bezpečnostní dokumentace |
| `docs/EXECUTIVE_SUMMARY.md` | 2-stránkový executive summary pro partnery |
| `docs/PITCH_DECK_OUTLINE.md` | 12-slide pitch deck |

## Backend architektura (src/)
```
src/
├── main.py                  # FastAPI entry point
├── core/                    # Core logic (config, security, crisis detection)
│   ├── config.py            #   Settings (pydantic-settings, .env)
│   ├── database.py          #   AsyncEngine, session factory
│   ├── security.py          #   JWT, bcrypt, AES-256-GCM
│   ├── deps.py              #   get_current_user dependency
│   ├── crisis.py            #   Crisis detection (ZERO DEPS)
│   ├── crisis_contacts.py   #   Czech crisis phone numbers
│   ├── guardrails.py        #   Post-LLM output filter
│   ├── prompts.py           #   System prompt, disclaimers
│   ├── audit.py             #   Audit trail logging
│   └── middleware.py         #   Request logging, security headers
├── models/                  # SQLAlchemy 2.0 ORM models
│   ├── base.py              #   Base with UUID PK, timestamps
│   ├── user.py              #   User (email optional!)
│   ├── conversation.py      #   Conversation + Message (encrypted)
│   ├── tracking.py          #   SobrietyCheckin + CravingEvent
│   ├── screening.py         #   ScreeningResult (AUDIT)
│   ├── knowledge_base.py    #   KnowledgeDocument (pgvector)
│   └── audit_log.py         #   AuditLog (AI Act compliance)
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

## Stav implementace (Session 0 + audit)
- **49 testů** — vše prochází (crisis detection, guardrails, AUDIT scoring)
- **6 API routerů** — auth, chat, screening, tracking, crisis, admin
- **19 endpointů** celkem (18 v routerech + /health)
- **Bezpečnostní audit:** CORS restricted, GDPR erasure complete, ForeignKeys, LIKE injection fix, startup secret validation, zero-width char bypass fix in crisis detection
- Alembic migrace: TODO
- Frontend: TODO (React Native)
