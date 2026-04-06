# CONTEXT_code_services.md — Services, Models & Config Source Code

> Generated 2026-04-06 · Luceo v0.1.0 · Session 6
> Full source, no truncation.

---

## src/services/chat.py

```python
"""Chat orchestration service — the core product logic.

Flow for every user message:
1. Crisis detection (BEFORE anything else)
2. If crisis HIGH+ → predefined response, no LLM call
3. If crisis MEDIUM → flag to append crisis resources
4. Load conversation history
5. RAG: retrieve relevant clinical docs
6. Build system prompt
7. Call Claude API
8. Check output guardrails
9. Encrypt & store messages
10. Return response
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.audit import log_audit_event
from src.core.crisis import CrisisLevel, detect_crisis, get_crisis_response
from src.core.guardrails import SAFE_FALLBACK, check_response_guardrails
from src.core.prompts import DISCLAIMER_REMINDER, LUCEO_SYSTEM_PROMPT
from src.core.security import decrypt_field, encrypt_field
from src.models.conversation import Message
from src.services.anthropic_client import generate_response
from src.services.rag import format_context, retrieve_context

logger = logging.getLogger("luceo.chat")

MAX_HISTORY_MESSAGES = 20
DISCLAIMER_INTERVAL = 10  # Remind every N messages


async def process_message(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    content: str,
    db: AsyncSession,
) -> dict:
    """Process a user message and return assistant response.

    Returns dict with: message, crisis_detected, crisis_contacts, disclaimer.
    """
    # 1. Crisis detection — BEFORE anything else
    crisis_result = detect_crisis(content)

    # Store user message (encrypted)
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content_encrypted=encrypt_field(content),
        crisis_level=crisis_result.level.value,
    )
    db.add(user_msg)

    # 2. If crisis HIGH or CRITICAL → predefined response, NO LLM call
    if crisis_result.level in (CrisisLevel.HIGH, CrisisLevel.CRITICAL):
        response_text = get_crisis_response(crisis_result)
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content_encrypted=encrypt_field(response_text),
            crisis_level=crisis_result.level.value,
        )
        db.add(assistant_msg)
        await db.commit()

        return {
            "message": response_text,
            "crisis_detected": True,
            "crisis_contacts": [c.model_dump() for c in crisis_result.crisis_contacts],
            "disclaimer": None,
        }

    # 3. Load conversation history (flush pending user_msg first to include it)
    await db.flush()
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
    )
    history_msgs = list(reversed(result.scalars().all()))

    messages = []
    for msg in history_msgs:
        try:
            decrypted = decrypt_field(msg.content_encrypted)
        except Exception:
            decrypted = "[encrypted message]"
        messages.append({"role": msg.role, "content": decrypted})

    # 4. RAG: retrieve relevant clinical docs (graceful degradation)
    try:
        docs = await retrieve_context(content, db)
    except Exception:
        logger.warning("RAG retrieval failed, continuing without context")
        docs = []
    rag_context = format_context(docs)

    # 5. Build system prompt (use Template to avoid crashes on { } in RAG content)
    user_context = ""  # TODO: inject sobriety streak, mood data
    system_prompt = LUCEO_SYSTEM_PROMPT.replace(
        "{rag_context}", rag_context
    ).replace(
        "{user_context}", user_context
    )

    # 6. Call Claude API
    response_text, token_count = await generate_response(system_prompt, messages)

    # 7. Check output guardrails
    is_safe, reason = check_response_guardrails(response_text)
    if not is_safe:
        logger.warning("Guardrail triggered: %s", reason)
        response_text = SAFE_FALLBACK

    # 8. Append crisis resources for MEDIUM level
    if crisis_result.level == CrisisLevel.MEDIUM:
        response_text += "\n\n" + get_crisis_response(crisis_result)

    # 9. Determine if disclaimer reminder is needed
    msg_count = len(history_msgs)
    disclaimer = (
        DISCLAIMER_REMINDER if msg_count > 0 and msg_count % DISCLAIMER_INTERVAL == 0 else None
    )

    # 10. Store assistant message
    assistant_msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content_encrypted=encrypt_field(response_text),
        crisis_level=crisis_result.level.value,
        token_count=token_count,
    )
    db.add(assistant_msg)

    await log_audit_event(
        db, "chat_message",
        user_id=user_id,
        details={"crisis_level": crisis_result.level.value},
    )

    await db.commit()

    return {
        "message": response_text,
        "crisis_detected": crisis_result.level != CrisisLevel.NONE,
        "crisis_contacts": (
            [c.model_dump() for c in crisis_result.crisis_contacts]
            if crisis_result.level == CrisisLevel.MEDIUM
            else None
        ),
        "disclaimer": disclaimer,
    }
```

---

## src/services/anthropic_client.py

```python
"""Anthropic Claude API wrapper — thin layer for testability."""

import logging

import anthropic

from src.core.config import settings

logger = logging.getLogger("luceo.anthropic")

_client: anthropic.AsyncAnthropic | None = None


def _get_client() -> anthropic.AsyncAnthropic:
    """Lazy singleton — avoids recreating HTTP connection pool on every request."""
    global _client
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    return _client


async def generate_response(
    system_prompt: str,
    messages: list[dict],
    max_tokens: int = 1024,
) -> tuple[str, int]:
    """Call Claude API and return (response_text, total_token_count).

    Returns a fallback message on API failure — crisis contacts included.
    """
    client = _get_client()

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages,
        )
        text = response.content[0].text if response.content else ""
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return text, tokens

    except Exception as e:
        logger.error("Anthropic API error: %s: %s", type(e).__name__, e)
        return (
            "Omlouvám se, momentálně nemohu odpovědět. Zkus to prosím za chvíli. "
            "Pokud potřebuješ okamžitou pomoc, zavolej na 116 123.",
            0,
        )
```

---

## src/services/rag.py

```python
"""RAG retrieval service — semantic search over clinical knowledge base."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.knowledge_base import KnowledgeDocument

logger = logging.getLogger("luceo.rag")


async def retrieve_context(
    query: str,
    db: AsyncSession,
    top_k: int = 3,
) -> list[KnowledgeDocument]:
    """Retrieve the most relevant knowledge documents for a query.

    For MVP without embedding infrastructure, falls back to keyword-based
    search. When embeddings are populated, uses pgvector cosine similarity.
    """
    # MVP fallback: simple keyword search using PostgreSQL ilike
    # TODO: Replace with proper embedding-based search when embedding service is ready
    # Escape LIKE-special chars to prevent pattern injection
    safe_query = query[:100].replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    result = await db.execute(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.content.ilike(f"%{safe_query}%"))
        .limit(top_k)
    )
    docs = list(result.scalars().all())

    if not docs:
        # Fallback: get most recent documents from relevant categories
        result = await db.execute(
            select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).limit(top_k)
        )
        docs = list(result.scalars().all())

    return docs


def format_context(documents: list[KnowledgeDocument]) -> str:
    """Format retrieved documents into context string for the LLM prompt."""
    if not documents:
        return ""

    parts = ["KONTEXT Z KLINICKÉ DATABÁZE:"]
    for doc in documents:
        parts.append(f"\n[{doc.source} — {doc.category}] {doc.title}:\n{doc.content}")

    return "\n".join(parts)
```

---

## src/services/screening.py

```python
"""WHO AUDIT (Alcohol Use Disorders Identification Test) scoring.

The AUDIT is a 10-question screening tool developed by the WHO.
It is public domain and widely validated.
"""

from pydantic import BaseModel


class AuditOption(BaseModel):
    text_cs: str
    text_en: str
    value: int


class AuditQuestion(BaseModel):
    number: int
    text_cs: str
    text_en: str
    options: list[AuditOption]


class AuditResult(BaseModel):
    total_score: int
    risk_level: str
    recommendation_cs: str
    recommendation_en: str


AUDIT_QUESTIONS: list[AuditQuestion] = [
    AuditQuestion(
        number=1,
        text_cs="Jak často piješ alkoholické nápoje?",
        text_en="How often do you have a drink containing alcohol?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Jednou za měsíc nebo méně", text_en="Monthly or less", value=1),
            AuditOption(text_cs="2–4× za měsíc", text_en="2-4 times a month", value=2),
            AuditOption(text_cs="2–3× za týden", text_en="2-3 times a week", value=3),
            AuditOption(text_cs="4× nebo vícekrát za týden", text_en="4 or more times a week", value=4),
        ],
    ),
    AuditQuestion(
        number=2,
        text_cs="Kolik sklenic alkoholu obvykle vypiješ, když piješ?",
        text_en="How many drinks containing alcohol do you have on a typical day when you are drinking?",
        options=[
            AuditOption(text_cs="1–2", text_en="1 or 2", value=0),
            AuditOption(text_cs="3–4", text_en="3 or 4", value=1),
            AuditOption(text_cs="5–6", text_en="5 or 6", value=2),
            AuditOption(text_cs="7–9", text_en="7 to 9", value=3),
            AuditOption(text_cs="10 nebo více", text_en="10 or more", value=4),
        ],
    ),
    AuditQuestion(
        number=3,
        text_cs="Jak často vypiješ 6 nebo více sklenic při jedné příležitosti?",
        text_en="How often do you have 6 or more drinks on one occasion?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=4,
        text_cs="Jak často se ti za poslední rok stalo, že jsi nemohl/a přestat pít, když jsi začal/a?",
        text_en="How often during the last year have you found that you were not able to stop drinking once you had started?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=5,
        text_cs="Jak často se ti za poslední rok stalo, že jsi kvůli pití nesplnil/a, co se od tebe očekávalo?",
        text_en="How often during the last year have you failed to do what was normally expected of you because of drinking?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=6,
        text_cs="Jak často se ti za poslední rok stalo, že jsi po pití potřeboval/a ráno alkohol, abys mohl/a fungovat?",
        text_en="How often during the last year have you needed a first drink in the morning to get yourself going after a heavy drinking session?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=7,
        text_cs="Jak často se ti za poslední rok stalo, že jsi měl/a pocit viny nebo výčitek svědomí po pití?",
        text_en="How often during the last year have you had a feeling of guilt or remorse after drinking?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=8,
        text_cs="Jak často se ti za poslední rok stalo, že sis nemohl/a vzpomenout, co se stalo předchozí večer, protože jsi pil/a?",
        text_en="How often during the last year have you been unable to remember what happened the night before because of your drinking?",
        options=[
            AuditOption(text_cs="Nikdy", text_en="Never", value=0),
            AuditOption(text_cs="Méně než jednou za měsíc", text_en="Less than monthly", value=1),
            AuditOption(text_cs="Jednou za měsíc", text_en="Monthly", value=2),
            AuditOption(text_cs="Jednou za týden", text_en="Weekly", value=3),
            AuditOption(text_cs="Denně nebo téměř denně", text_en="Daily or almost daily", value=4),
        ],
    ),
    AuditQuestion(
        number=9,
        text_cs="Byl/a jsi ty nebo někdo jiný zraněn v důsledku tvého pití?",
        text_en="Have you or someone else been injured because of your drinking?",
        options=[
            AuditOption(text_cs="Ne", text_en="No", value=0),
            AuditOption(text_cs="Ano, ale ne za poslední rok", text_en="Yes, but not in the last year", value=2),
            AuditOption(text_cs="Ano, za poslední rok", text_en="Yes, during the last year", value=4),
        ],
    ),
    AuditQuestion(
        number=10,
        text_cs="Navrhl ti někdo z příbuzných, přátel, lékař nebo jiný zdravotník, abys omezil/a pití?",
        text_en="Has a relative, friend, doctor, or other health care worker been concerned about your drinking or suggested you cut down?",
        options=[
            AuditOption(text_cs="Ne", text_en="No", value=0),
            AuditOption(text_cs="Ano, ale ne za poslední rok", text_en="Yes, but not in the last year", value=2),
            AuditOption(text_cs="Ano, za poslední rok", text_en="Yes, during the last year", value=4),
        ],
    ),
]

# Risk levels per WHO AUDIT manual
_RISK_LEVELS = {
    "low_risk": (0, 7),
    "hazardous": (8, 15),
    "harmful": (16, 19),
    "possible_dependence": (20, 40),
}

_RECOMMENDATIONS_CS = {
    "low_risk": "Tvé odpovědi naznačují nízké riziko. Pokračuj v udržování zdravého vztahu k alkoholu.",
    "hazardous": "Tvé odpovědi naznačují rizikové pití. Luceo ti může pomoci s technikami pro snížení konzumace.",
    "harmful": "Tvé odpovědi naznačují škodlivé pití. Doporučujeme konzultaci s odborníkem. Luceo tě podpoří na cestě ke změně.",
    "possible_dependence": "Tvé odpovědi naznačují, že by ti prospěla konzultace se zdravotnickým odborníkem. Luceo tě může podpořit, ale odborné vedení je důležité.",
}

_RECOMMENDATIONS_EN = {
    "low_risk": "Your responses suggest a low-risk relationship with alcohol.",
    "hazardous": "Your responses suggest hazardous drinking. Luceo can help you with techniques to reduce consumption.",
    "harmful": "Your responses suggest harmful drinking. We recommend consulting with a professional. Luceo will support you on your path to change.",
    "possible_dependence": "Your responses suggest it would be beneficial to speak with a healthcare professional. Luceo can support you, but professional guidance is recommended.",
}


def score_audit(answers: list[int]) -> AuditResult:
    """Score AUDIT questionnaire answers. Expects a list of 10 integers."""
    if len(answers) != 10:
        raise ValueError("AUDIT requires exactly 10 answers")

    total = sum(answers)

    risk_level = "low_risk"
    for level, (low, high) in _RISK_LEVELS.items():
        if low <= total <= high:
            risk_level = level
            break

    return AuditResult(
        total_score=total,
        risk_level=risk_level,
        recommendation_cs=_RECOMMENDATIONS_CS[risk_level],
        recommendation_en=_RECOMMENDATIONS_EN[risk_level],
    )
```

---

## src/services/tracking.py

```python
"""Sobriety tracking business logic — streak calculation, summaries."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.tracking import CravingEvent, SobrietyCheckin


async def get_sobriety_streak(user_id: uuid.UUID, db: AsyncSession) -> int:
    """Count consecutive sober days backward from today."""
    today = datetime.now(UTC).date()
    result = await db.execute(
        select(SobrietyCheckin)
        .where(SobrietyCheckin.user_id == user_id)
        .order_by(SobrietyCheckin.date.desc())
        .limit(365)
    )
    checkins = result.scalars().all()

    streak = 0
    expected_date = today
    for checkin in checkins:
        if checkin.date == expected_date and checkin.is_sober:
            streak += 1
            expected_date -= timedelta(days=1)
        elif checkin.date == expected_date and not checkin.is_sober:
            break
        elif checkin.date < expected_date:
            # Gap in days — streak broken
            break

    return streak


async def get_tracking_summary(
    user_id: uuid.UUID, days: int, db: AsyncSession
) -> dict:
    """Get aggregate tracking stats for the last N days using SQL aggregation."""
    since = datetime.now(UTC).date() - timedelta(days=days)

    # Total checkin days + average mood via SQL
    stats_result = await db.execute(
        select(
            func.count().label("total_days"),
            func.avg(SobrietyCheckin.mood).label("avg_mood"),
        ).where(
            SobrietyCheckin.user_id == user_id,
            SobrietyCheckin.date >= since,
        )
    )
    stats_row = stats_result.one()
    total_days = stats_row.total_days or 0
    avg_mood_raw = stats_row.avg_mood
    avg_mood = round(float(avg_mood_raw), 1) if avg_mood_raw is not None else None

    # Sober days count via SQL
    sober_result = await db.execute(
        select(func.count()).where(
            SobrietyCheckin.user_id == user_id,
            SobrietyCheckin.date >= since,
            SobrietyCheckin.is_sober == True,  # noqa: E712
        )
    )
    sober_days = sober_result.scalar() or 0

    since_dt = datetime.combine(since, datetime.min.time())

    # Craving count — compare created_at with datetime for cross-DB compat
    craving_count_result = await db.execute(
        select(func.count()).where(
            CravingEvent.user_id == user_id,
            CravingEvent.created_at >= since_dt,
        )
    )
    total_cravings = craving_count_result.scalar() or 0

    # Top trigger via SQL GROUP BY
    top_trigger_result = await db.execute(
        select(
            CravingEvent.trigger_category,
            func.count().label("cnt"),
        )
        .where(
            CravingEvent.user_id == user_id,
            CravingEvent.created_at >= since_dt,
        )
        .group_by(CravingEvent.trigger_category)
        .order_by(func.count().desc())
        .limit(1)
    )
    top_trigger_row = top_trigger_result.first()
    top_trigger = top_trigger_row.trigger_category if top_trigger_row else None

    streak = await get_sobriety_streak(user_id, db)

    return {
        "sober_days": sober_days,
        "total_days": total_days,
        "average_mood": avg_mood,
        "total_cravings": total_cravings,
        "top_trigger": top_trigger,
        "current_streak": streak,
    }
```

---

## src/models/base.py

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

---

## src/models/user.py

```python
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    # Email is OPTIONAL — Karel persona needs anonymity
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    # GDPR consent tracking (Article 7)
    gdpr_consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    gdpr_consent_version: Mapped[str | None] = mapped_column(String(20))
    data_region: Mapped[str] = mapped_column(String(20), default="eu-central")

    # Profile (minimal — data minimization principle)
    display_name: Mapped[str | None] = mapped_column(String(100))

    # Soft delete for GDPR Article 17 (right to erasure)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
```

---

## src/models/conversation.py

```python
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Conversation(BaseModel):
    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # AI Act compliance: user must know they talk to AI
    disclaimer_shown: Mapped[bool] = mapped_column(Boolean, default=False)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", passive_deletes=True
    )


class Message(BaseModel):
    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20))  # "user", "assistant", "system"
    content_encrypted: Mapped[str] = mapped_column(Text)  # AES-256-GCM encrypted
    crisis_level: Mapped[str | None] = mapped_column(String(20))  # Audit trail
    token_count: Mapped[int | None] = mapped_column(Integer)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
```

---

## src/models/tracking.py

```python
import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class SobrietyCheckin(BaseModel):
    __tablename__ = "sobriety_checkins"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    is_sober: Mapped[bool] = mapped_column(Boolean)
    mood: Mapped[int | None] = mapped_column(Integer)  # 1-5
    energy_level: Mapped[int | None] = mapped_column(Integer)  # 1-5
    notes_encrypted: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_checkin_user_date"),
        CheckConstraint("mood IS NULL OR (mood >= 1 AND mood <= 5)", name="ck_checkin_mood"),
        CheckConstraint(
            "energy_level IS NULL OR (energy_level >= 1 AND energy_level <= 5)",
            name="ck_checkin_energy_level",
        ),
    )


class CravingEvent(BaseModel):
    __tablename__ = "craving_events"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    intensity: Mapped[int] = mapped_column(Integer)  # 1-10
    trigger_category: Mapped[str] = mapped_column(
        String(30)
    )  # stress, social, emotional, habitual, environmental, other
    trigger_notes_encrypted: Mapped[str | None] = mapped_column(Text)
    coping_strategy_used: Mapped[str | None] = mapped_column(String(200))
    outcome: Mapped[str | None] = mapped_column(String(20))  # resisted, gave_in

    __table_args__ = (
        CheckConstraint("intensity >= 1 AND intensity <= 10", name="ck_craving_intensity"),
    )
```

---

## src/models/screening.py

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class ScreeningResult(BaseModel):
    __tablename__ = "screening_results"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    questionnaire_type: Mapped[str] = mapped_column(String(20), default="AUDIT")
    answers: Mapped[dict] = mapped_column(JSON)
    total_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(30))
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

---

## src/models/knowledge_base.py

```python
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Allow import without pgvector installed (tests with SQLite)
    Vector = None


class KnowledgeDocument(BaseModel):
    __tablename__ = "knowledge_documents"

    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100))  # "who_guidelines", "cbt_protocol", etc.
    category: Mapped[str] = mapped_column(
        String(50), index=True
    )  # "cbt", "screening", "crisis", "motivational_interviewing"

    # pgvector embedding — nullable for records not yet embedded
    # Using 1024 dimensions (can be adjusted based on embedding model)
    # Note: Vector column defined via raw SQL if pgvector not available
    embedding = mapped_column(Vector(1024), nullable=True) if Vector else None

    verified_by: Mapped[str | None] = mapped_column(String(200))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
```

---

## src/models/audit_log.py

```python
import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(50), index=True)
    # e.g. "chat_message", "crisis_detected", "login", "gdpr_deletion"
    details: Mapped[dict | None] = mapped_column(JSON)
    ip_hash: Mapped[str | None] = mapped_column(String(64))  # SHA-256 of IP (GDPR)
    # Timestamp is inherited from BaseModel.created_at
```

---

## src/models/refresh_token.py

```python
"""Refresh token model for persistent authentication."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
```

---

## pyproject.toml

```toml
[project]
name = "luceo"
version = "0.1.0"
description = "AI-powered addiction recovery support platform"
readme = "README.md"
license = { file = "LICENCE" }
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    "anthropic>=0.52",
    "sqlalchemy>=2.0",
    "asyncpg>=0.30",
    "pgvector>=0.3",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "python-jose[cryptography]>=3.3",
    "argon2-cffi>=25.1",
    "passlib[bcrypt]>=1.7",  # Legacy support for existing bcrypt hashes
    "cryptography>=44.0",
    "alembic>=1.14",
    "slowapi>=0.1.9",
    "email-validator>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest >= 8.0",
    "pytest-asyncio >= 0.24",
    "httpx >= 0.28",
    "aiosqlite >= 0.20",
    "ruff >= 0.9",
    "mypy >= 1.14",
]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```
