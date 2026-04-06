# CONTEXT_code_core.md — Core Module Source Code

> Generated 2026-04-06 · Luceo v0.1.0 · Session 6
> Full source, no truncation.

---

## src/core/crisis.py

```python
"""Crisis detection layer — runs BEFORE any LLM call.

This module is intentionally dependency-free (no database, no API calls,
no imports from src.services or src.models). It must be fast (<1ms),
deterministic, and auditable. If the LLM or database is down, crisis
detection still works.

All crisis responses are predefined — NO AI improvisation during crisis.
"""

import enum
import re
import unicodedata

from pydantic import BaseModel

from src.core.crisis_contacts import CZECH_CRISIS_CONTACTS, CrisisContact


class CrisisLevel(str, enum.Enum):
    NONE = "none"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CrisisResult(BaseModel):
    level: CrisisLevel
    matched_keywords: list[str]
    recommended_action: str
    crisis_contacts: list[CrisisContact]


def normalize_text(text: str) -> str:
    """Strip diacritics, zero-width characters, lowercase, collapse whitespace."""
    # Remove zero-width and invisible characters that could bypass keyword matching
    text = re.sub(r"[\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad\u2060\u180e]", "", text)
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", ascii_text.lower().strip())


# --- Keyword tiers (Czech-first, normalized/no-diacritics form) ---

_CRITICAL_PATTERNS: list[str] = [
    r"\bchci\s+zemrit\b",
    r"\bchci\s+umrit\b",
    r"\bchci\s+se\s+zabit\b",
    r"\bzabiju\s+se\b",
    r"\bsebevrazd",
    r"\bnemam\s+duvod\s+zit\b",
    r"\bskoncit\s+se?\s+vsim\b",
    r"\bskoncit\s+se\s+zivotem\b",
    r"\bnechci\s+zit\b",
    r"\bchci\s+skoncit\b",
    r"\bobesi[mt]\b",
    r"\botravit\s+se\b",
    r"\bskocim\b",
    # English equivalents
    r"\bwant\s+to\s+die\b",
    r"\bkill\s+myself\b",
    r"\bsuicid",
    r"\bend\s+(my|it\s+all)\b",
]

_HIGH_PATTERNS: list[str] = [
    r"\bchci\s+si\s+ublizit\b",
    r"\bchci\s+se\s+porezat\b",
    r"\biblizit\s+si\b",
    r"\bpredavkovat\s+se\b",
    r"\bse\s+predavkovat\b",
    r"\bpredavkovani\b",
    r"\bsebeposk",
    r"\bself.?harm",
    r"\boverdos",
]

_MEDIUM_PATTERNS: list[str] = [
    r"\brelaps\b",
    r"\bchci\s+pit\b",
    r"\bmusim\s+se\s+napit\b",
    r"\bnedokazu\s+to\b",
    r"\bneunesu\s+to\b",
    r"\bnezvladam\s+to\b",
    r"\bnemam\s+silu\b",
    r"\bvse\s+je\s+ztracen[eo]\b",
    r"\bbeznadej",
    r"\bnema\s+to\s+cenu\b",
    r"\bnema\s+to\s+smysl\b",
    r"\bnikomu\s+na\s+mne\s+nezalezi\b",
    r"\bnemohu\s+dal\b",
    r"\bnemuzu\s+dal\b",
    r"\bnevydrzim\b",
    r"\bcraving\b",
    r"\bi\s+can'?t\s+stop\b",
]

_COMPILED_CRITICAL = [re.compile(p) for p in _CRITICAL_PATTERNS]
_COMPILED_HIGH = [re.compile(p) for p in _HIGH_PATTERNS]
_COMPILED_MEDIUM = [re.compile(p) for p in _MEDIUM_PATTERNS]


def detect_crisis(message: str) -> CrisisResult:
    """Detect crisis level in a user message.

    Normalizes text (strips diacritics, lowercases) and checks against
    keyword tiers from highest to lowest.
    """
    normalized = normalize_text(message)
    matched: list[str] = []

    # Check CRITICAL first
    for pattern in _COMPILED_CRITICAL:
        m = pattern.search(normalized)
        if m:
            matched.append(m.group())
    if matched:
        return CrisisResult(
            level=CrisisLevel.CRITICAL,
            matched_keywords=matched,
            recommended_action="immediate_crisis_response",
            crisis_contacts=CZECH_CRISIS_CONTACTS,
        )

    # Check HIGH
    for pattern in _COMPILED_HIGH:
        m = pattern.search(normalized)
        if m:
            matched.append(m.group())
    if matched:
        return CrisisResult(
            level=CrisisLevel.HIGH,
            matched_keywords=matched,
            recommended_action="crisis_response_with_contacts",
            crisis_contacts=CZECH_CRISIS_CONTACTS,
        )

    # Check MEDIUM
    for pattern in _COMPILED_MEDIUM:
        m = pattern.search(normalized)
        if m:
            matched.append(m.group())
    if matched:
        return CrisisResult(
            level=CrisisLevel.MEDIUM,
            matched_keywords=matched,
            recommended_action="append_crisis_resources",
            crisis_contacts=CZECH_CRISIS_CONTACTS[:4],
        )

    return CrisisResult(
        level=CrisisLevel.NONE,
        matched_keywords=[],
        recommended_action="proceed_normally",
        crisis_contacts=[],
    )


def get_crisis_response(result: CrisisResult) -> str:
    """Return a predefined crisis response. NO AI improvisation.

    These messages should be reviewed by a clinical advisor.
    """
    if result.level == CrisisLevel.CRITICAL:
        return (
            "Rozumím, že procházíš velmi těžkým obdobím. Tvůj život má hodnotu "
            "a zasloužíš si podporu.\n\n"
            "Prosím, zavolej na krizovou linku — jsou dostupní 24/7 a pomohou ti:\n"
            "📞 Krizová pomoc: 116 123\n"
            "📞 Linka bezpečí: 116 111\n"
            "📞 Záchranná služba: 155\n\n"
            "Nejsi na to sám/sama. Odborníci na těchto linkách ti pomohou."
        )

    if result.level == CrisisLevel.HIGH:
        return (
            "Slyším tě a beru to vážně. To, co popisuješ, vyžaduje odbornou pomoc.\n\n"
            "Prosím, obrať se na krizovou linku:\n"
            "📞 Krizová pomoc: 116 123 (24/7)\n"
            "📞 Národní linka pro odvykání: 800 350 000\n\n"
            "Nechci ti radit něco, co přesahuje moje možnosti jako AI nástroje. "
            "Na těchto linkách jsou lidé, kteří ti skutečně pomohou."
        )

    if result.level == CrisisLevel.MEDIUM:
        return (
            "\n\n---\n"
            "💡 Pokud cítíš silnou touhu po alkoholu nebo ti není dobře, "
            "můžeš zavolat na Národní linku pro odvykání: 800 350 000 (Po-Pá 10-18). "
            "Pro akutní krizi: 116 123 (24/7)."
        )

    return ""
```

---

## src/core/security.py

```python
import hashlib
import os
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.refresh_token import RefreshToken

_ph = PasswordHasher()

# JWT
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    # Backward compatibility: bcrypt hashes start with "$2b$" or "$2a$"
    if hashed.startswith(("$2b$", "$2a$")):
        try:
            from passlib.context import CryptContext
            _legacy = CryptContext(schemes=["bcrypt"], deprecated="auto")
            return _legacy.verify(plain, hashed)
        except Exception:
            return False

    try:
        return _ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(hours=settings.jwt_expiration_hours)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError("Invalid or expired token") from e


# --- Refresh tokens (SHA-256 hash for O(1) index lookup) ---


def _hash_token(raw_token: str) -> str:
    """SHA-256 hash of a refresh token — deterministic, allows index lookup."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


async def create_refresh_token(user_id: uuid.UUID, db: AsyncSession) -> str:
    """Generate a secure refresh token, store its hash, return the raw token."""
    raw_token = secrets.token_urlsafe(64)
    entry = RefreshToken(
        user_id=user_id,
        token_hash=_hash_token(raw_token),
        expires_at=datetime.now(UTC)
        + timedelta(days=settings.refresh_token_expiry_days),
    )
    db.add(entry)
    return raw_token


async def verify_refresh_token(raw_token: str, db: AsyncSession) -> RefreshToken:
    """Find and validate a refresh token. Raises ValueError if invalid."""
    token_hash = _hash_token(raw_token)
    now = datetime.now(UTC)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise ValueError("Invalid or expired refresh token")
    return entry


async def revoke_refresh_token(token_entry: RefreshToken) -> None:
    """Revoke a refresh token (soft-delete). Caller must commit."""
    token_entry.revoked_at = datetime.now(UTC)


# AES-256-GCM field-level encryption
def _get_aes_key() -> bytes:
    key_hex = settings.encryption_key
    if len(key_hex) < 64:
        # Pad/hash short keys for dev — in production use a proper 32-byte hex key
        key_hex = hashlib.sha256(key_hex.encode()).hexdigest()
    return bytes.fromhex(key_hex[:64])


def encrypt_field(plaintext: str) -> str:
    """Encrypt a string field using AES-256-GCM. Returns hex(nonce + ciphertext)."""
    key = _get_aes_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return (nonce + ciphertext).hex()


def decrypt_field(encrypted_hex: str) -> str:
    """Decrypt a hex-encoded AES-256-GCM field.

    Raises ValueError on corrupt/invalid data.
    """
    try:
        key = _get_aes_key()
        aesgcm = AESGCM(key)
        raw = bytes.fromhex(encrypted_hex)
        if len(raw) < 13:  # 12-byte nonce + at least 1 byte ciphertext
            raise ValueError("Encrypted data too short")
        nonce = raw[:12]
        ciphertext = raw[12:]
        return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
    except (ValueError, Exception) as e:
        raise ValueError(f"Decryption failed: {e}") from e
```

---

## src/core/guardrails.py

```python
"""Post-LLM output guardrails — defense in depth.

Scans LLM responses for forbidden patterns that should not appear
in Luceo's output, even if the system prompt was bypassed.
"""

import re
import unicodedata

# --- Text normalization (mirrors crisis.py approach) ---


def _normalize_text(text: str) -> str:
    """Strip diacritics and normalize whitespace for pattern matching."""
    # NFKD decomposes characters (e.g., é → e + combining accent)
    nfkd = unicodedata.normalize("NFKD", text)
    # Strip combining marks (accents)
    stripped = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return stripped.lower()


# Patterns are written WITHOUT diacritics — normalization strips them
_DIAGNOSTIC_PATTERNS = [
    r"\bF1[0-9]\.[0-9]\b",  # ICD-10 codes
    r"\b(diagnostikuji|vase diagnoza|trpite)\b",
    r"\bmas\s+(diagnozu|poruchu|nemoc)\b",
    r"\bjsi\s+alkoholi[ck]\w*\b",  # alkoholik, alkoholicka, alkoholikem...
    r"\bjsi\s+zavisl[yae]\w*\b",  # zavisly, zavisla, zavisle, zavislym...
]

_MEDICATION_PATTERNS = [
    r"\b(naltrexon|acamprosat|disulfiram|antabus|campral)\b",
    r"\b(baclofen|baklofen|gabapentin|topiramat|nalmefen|nalmefene)\b",
    r"\b(diazepam|lorazepam|alprazolam|xanax|lexaurin)\b",
    r"\b(sertralin|fluoxetin|escitalopram|citalopram|paroxetin)\b",
    r"\b(\d+\s*mg\s*(denne|rano|vecer|2x|3x|daily|twice|once))\b",
]

_COMPILED_DIAGNOSTIC = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in _DIAGNOSTIC_PATTERNS]
_COMPILED_MEDICATION = [re.compile(p, re.IGNORECASE | re.UNICODE) for p in _MEDICATION_PATTERNS]

SAFE_FALLBACK = (
    "Na toto se prosím zeptej svého lékaře. "
    "Mohu ti ale pomoci s technikami zvládání chutí, sledováním nálad "
    "a dalšími podpůrnými nástroji."
)


def check_response_guardrails(response: str) -> tuple[bool, str | None]:
    """Check LLM response for forbidden content.

    Returns (is_safe, reason). If not safe, caller should replace
    the offending response with SAFE_FALLBACK.
    """
    normalized = _normalize_text(response)

    for pattern in _COMPILED_DIAGNOSTIC:
        if pattern.search(normalized):
            return False, "Diagnostic language detected"

    for pattern in _COMPILED_MEDICATION:
        if pattern.search(normalized):
            return False, "Medication recommendation detected"

    return True, None
```

---

## src/core/prompts.py

```python
"""System prompts and templates for Luceo AI assistant.

The system prompt is a constant in code (not in DB) so that any change
goes through version control and code review.
"""

LUCEO_SYSTEM_PROMPT = """\
Jsi Luceo, podpůrný průvodce pro lidi, kteří chtějí změnit svůj vztah k alkoholu.

ZÁSADY (dodržuj vždy):
1. Nejsi terapeut ani lékař. Jsi podpůrný nástroj.
2. NIKDY nediagnostikuj. Neříkej "máš závislost" ani "jsi alkoholik."
3. NIKDY nedoporučuj konkrétní léky ani dávkování.
4. Pokud uživatel popisuje závažné zdravotní příznaky (třes, halucinace, záchvaty), \
OKAMŽITĚ ho odkaž na lékaře nebo záchrannou službu (155).
5. Používej empatický, nestigmatizující jazyk. Říkej "vztah k alkoholu", ne "závislost."
6. Odpovídej česky, pokud uživatel nepíše anglicky.
7. Drž se informací z poskytnutého kontextu. Nevymýšlej fakta.

{rag_context}

{user_context}
"""

AI_DISCLAIMER = (
    "Komunikuješ s AI asistentem Luceo. Luceo je podpůrný wellness nástroj, "
    "nikoli lékař, terapeut ani zdravotnické zařízení."
)

DISCLAIMER_REMINDER = (
    "Připomínám, že jsem AI asistent — podpůrný nástroj, ne terapeut. "
    "Pro odbornou pomoc se prosím obrať na svého lékaře nebo AT ambulanci."
)
```

---

## src/core/crisis_contacts.py

```python
"""Czech crisis contacts — hardcoded for reliability.

This module has NO external dependencies. It must work even if the database
or any API is down. Crisis contacts are life-critical information.
"""

from pydantic import BaseModel


class CrisisContact(BaseModel):
    name: str
    phone: str
    description: str
    available: str
    url: str | None = None


CZECH_CRISIS_CONTACTS: list[CrisisContact] = [
    CrisisContact(
        name="Linka bezpečí",
        phone="116 111",
        description="Krizová linka pro děti a mladistvé",
        available="24/7",
        url="https://www.linkabezpeci.cz",
    ),
    CrisisContact(
        name="Linka první psychické pomoci",
        phone="116 123",
        description="Telefonická krizová intervence a první psychická pomoc",
        available="24/7",
        url="https://www.csspraha.cz",
    ),
    CrisisContact(
        name="Národní linka pro odvykání",
        phone="800 350 000",
        description="Bezplatná linka pro závislosti (alkohol, drogy, tabák)",
        available="Po-Pá 10:00-18:00",
        url="https://www.adfranklinova.cz",
    ),
    CrisisContact(
        name="Podané ruce",
        phone="549 257 217",
        description="Poradenství a léčba závislostí",
        available="Po-Pá 8:00-16:00",
        url="https://www.podaneruce.cz",
    ),
    CrisisContact(
        name="Záchranná služba",
        phone="155",
        description="Zdravotnická záchranná služba",
        available="24/7",
    ),
    CrisisContact(
        name="Tísňová linka",
        phone="112",
        description="Integrovaný záchranný systém",
        available="24/7",
    ),
]
```

---

## src/core/config.py

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "case_sensitive": False}

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "info"

    # Database
    postgres_user: str = "luceo"
    postgres_password: str = "changeme"
    postgres_db: str = "luceo"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Auth
    jwt_secret: str = "changeme-generate-a-real-secret"
    jwt_expiration_hours: int = 1  # Short-lived access token (use refresh tokens)
    refresh_token_expiry_days: int = 30

    # Anthropic
    anthropic_api_key: str = ""

    # Encryption
    encryption_key: str = "changeme-generate-a-real-key"

    # CORS
    cors_allowed_origins: str = ""  # Comma-separated origins for production

    # GDPR
    data_region: str = "eu-central"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync URL for Alembic migrations."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()


def validate_production_settings() -> None:
    """Ensure critical secrets are set in non-development environments."""
    if settings.app_env == "development":
        return
    errors = []
    if settings.jwt_secret.startswith("changeme") or len(settings.jwt_secret) < 32:
        errors.append("jwt_secret must be a real secret (min 32 chars) in production")
    enc = settings.encryption_key
    if enc.startswith("changeme") or len(enc) < 64:
        errors.append("encryption_key must be a 64-char hex string in production")
    if not settings.anthropic_api_key:
        errors.append("anthropic_api_key must be set in production")
    if settings.postgres_password.startswith("changeme"):
        errors.append("postgres_password must be set to a real password in production")
    if errors:
        raise RuntimeError(f"Production configuration errors: {'; '.join(errors)}")
```

---

## src/core/audit.py

```python
"""Audit trail logging for AI Act and GDPR compliance."""

import hashlib
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditLog

logger = logging.getLogger("luceo.audit")


async def log_audit_event(
    db: AsyncSession,
    action: str,
    *,
    user_id: uuid.UUID | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """Log an auditable event. IP is hashed (GDPR — no raw IPs stored)."""
    ip_hash = hashlib.sha256(ip_address.encode()).hexdigest() if ip_address else None

    entry = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_hash=ip_hash,
    )
    db.add(entry)
    # Caller is responsible for db.commit() — usually happens at request end
```

---

## src/core/database.py

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings

engine = create_async_engine(
    settings.database_url, pool_size=5, max_overflow=10, pool_pre_ping=True
)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```

---

## src/core/deps.py

```python
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import decode_access_token
from src.models.user import User

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
```

---

## src/core/middleware.py

```python
"""FastAPI middleware — request logging and security headers."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.config import settings

logger = logging.getLogger("luceo.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request method, path, status, and duration. No request body (GDPR)."""

    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        response = await call_next(request)
        duration_ms = (time.monotonic() - start) * 1000
        logger.info(
            "%s %s %d %.0fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "0"  # Disabled; CSP provides protection
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if settings.app_env != "development":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response
```

---

## src/core/rate_limit.py

```python
"""Rate limiting configuration using slowapi (in-memory, Redis-swappable)."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from src.core.security import decode_access_token


def _key_func(request: Request) -> str:
    """Extract user_id from JWT if present, otherwise fall back to IP."""
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            pass
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(key_func=_key_func)
```
