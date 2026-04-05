# Luceo

**AI-powered addiction recovery support platform.**

Luceo (Latin: *I shine*) is a personalized recovery companion for people struggling with alcohol addiction. It provides 24/7 support between therapy sessions — not as a replacement for professional help, but as a wellness tool that's always available.

> **Status:** MVP backend complete. Frontend (React Native) in development.

## Features

- **AI Chat** — Empathetic conversations powered by Claude API with RAG context
- **Crisis Detection** — Real-time safety layer that runs *before* every LLM call (Czech + English)
- **Output Guardrails** — Post-LLM filter preventing diagnoses and medication recommendations
- **AUDIT Screening** — WHO AUDIT-10 questionnaire with automated risk assessment
- **Sobriety Tracking** — Daily check-ins, mood tracking, craving logs, streak calculation
- **GDPR Compliant** — AES-256-GCM encryption, data export (Art. 15), right to erasure (Art. 17)
- **Audit Trail** — Full event logging for EU AI Act compliance

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| Database | PostgreSQL + pgvector |
| AI | Claude API (Anthropic) with RAG |
| Auth | JWT (1h) + refresh tokens (30d, SHA-256 hashed) |
| Encryption | AES-256-GCM field-level encryption |
| Migrations | Alembic (async) |
| Frontend | React Native (planned) |

## Quick Start

```bash
# Clone
git clone https://github.com/PatrikLuks/Luceo.git
cd Luceo

# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your settings

# Run tests
pytest tests/ -v

# Start server (requires PostgreSQL)
uvicorn src.main:app --reload
```

See [docs/technical/SETUP.md](docs/technical/SETUP.md) for detailed setup instructions.

## API Overview

| Endpoint Group | Description |
|---------------|-------------|
| `/api/v1/auth/*` | Registration, login, token refresh, logout, GDPR deletion |
| `/api/v1/chat/*` | Conversations and messages |
| `/api/v1/screening/*` | AUDIT questionnaire |
| `/api/v1/tracking/*` | Sobriety check-ins, cravings, streaks |
| `/api/v1/crisis/*` | Crisis contacts (public, no auth) |
| `/api/v1/admin/*` | GDPR data export |

Full API documentation: [docs/technical/API_REFERENCE.md](docs/technical/API_REFERENCE.md)

## Project Structure

```
src/
├── core/        # Config, security, crisis detection, guardrails, middleware
├── models/      # SQLAlchemy 2.0 ORM models (9 tables)
├── services/    # Business logic (chat orchestrator, RAG, screening, tracking)
└── api/         # FastAPI endpoints + Pydantic schemas
```

Architecture details: [docs/technical/ARCHITECTURE.md](docs/technical/ARCHITECTURE.md)

## Safety

Luceo is a **wellness app**, not a medical device. Two safety-critical modules ensure user safety:

- **`src/core/crisis.py`** — Zero-dependency crisis detection (runs before LLM)
- **`src/core/guardrails.py`** — Post-LLM output filter (blocks diagnoses, medications)

Both modules require clinical advisor review before production deployment.

## Documentation

| Document | Purpose |
|----------|---------|
| [MAIN_DOCUMENT](docs/project/MAIN_DOCUMENT.md) | Vision, team, roadmap |
| [ARCHITECTURE](docs/technical/ARCHITECTURE.md) | System design |
| [API_REFERENCE](docs/technical/API_REFERENCE.md) | Endpoint documentation |
| [SAFETY](docs/technical/SAFETY.md) | Crisis detection & guardrails |
| [FILE_MAP](docs/technical/FILE_MAP.md) | Complete file listing |

## License

See [LICENCE](LICENCE) file.

---

*Recovery is light, not punishment. Without stigma.*
