# Luceo — Development Setup

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ with pgvector extension (for production)
- Virtual environment

## Quick Start

```bash
# Clone
git clone <repo-url>
cd Luceo

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
# Edit .env with your values

# Run tests (no PostgreSQL needed — uses SQLite)
pytest

# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

See `.env.example` for a complete template. Key variables:

| Variable | Required | Default | Description |
|---|---|---|---|
| `POSTGRES_USER` | For DB | `luceo` | PostgreSQL username |
| `POSTGRES_PASSWORD` | For DB | `changeme` | PostgreSQL password |
| `POSTGRES_DB` | For DB | `luceo` | Database name |
| `POSTGRES_HOST` | For DB | `localhost` | Database host |
| `JWT_SECRET` | Yes (prod) | `changeme-...` | JWT signing secret |
| `ANTHROPIC_API_KEY` | For chat | — | Claude API key |
| `ENCRYPTION_KEY` | For chat | — | 32-byte hex string for AES-256-GCM |

Generate secrets:
```bash
# JWT secret
python3 -c "import secrets; print(secrets.token_hex(32))"

# Encryption key (AES-256 = 32 bytes = 64 hex chars)
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Database Setup

```bash
# Install pgvector extension (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS vector;

# Run migrations (when Alembic is configured)
alembic upgrade head
```

**Note:** Alembic initialization is pending. For MVP development, tables can be created via:
```python
from src.models.base import Base
from src.core.database import engine

async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

## Running Tests

```bash
# All tests
pytest

# Verbose
pytest -v

# Specific module
pytest tests/test_crisis.py

# With coverage (when pytest-cov is installed)
pytest --cov=src
```

Tests use **SQLite in-memory** — no PostgreSQL required. The `conftest.py` provides async SQLite session fixtures.

## Project Structure

See `docs/FILE_MAP.md` for a complete file listing, or `docs/ARCHITECTURE.md` for system design.

## Development Notes

- Code and comments are in **English**
- Project documentation is in **Czech** (primary audience)
- All sensitive data is encrypted at field level (AES-256-GCM)
- Crisis detection module (`src/core/crisis.py`) has **ZERO external dependencies** by design
- Post-LLM guardrails (`src/core/guardrails.py`) are the second safety layer
