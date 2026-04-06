"""Build personalized user context for injection into the LLM system prompt.

Fetches sobriety streak, today's check-in, recent cravings, and latest
AUDIT screening to give the AI assistant relevant background about the user.
No encrypted fields are read — only structured data.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.screening import ScreeningResult
from src.models.tracking import CravingEvent, SobrietyCheckin
from src.services.tracking import get_sobriety_streak

_RISK_LEVEL_CS: dict[str, str] = {
    "low_risk": "nízké riziko",
    "hazardous": "rizikové pití",
    "harmful": "škodlivé pití",
    "possible_dependence": "možná závislost",
}


async def build_user_context(user_id: uuid.UUID, db: AsyncSession) -> str:
    """Return a Czech-language context block for the system prompt.

    Returns "" if no data exists (new user).
    """
    lines: list[str] = []

    # 1. Sobriety streak
    streak = await get_sobriety_streak(user_id, db)
    if streak > 0:
        lines.append(f"- Střízlivost: {streak} dní v řadě")

    # 2. Today's check-in
    today = datetime.now(UTC).date()
    result = await db.execute(
        select(SobrietyCheckin).where(
            SobrietyCheckin.user_id == user_id,
            SobrietyCheckin.date == today,
        )
    )
    checkin = result.scalar_one_or_none()
    if checkin:
        parts: list[str] = []
        if checkin.mood is not None:
            parts.append(f"Nálada: {checkin.mood}/5")
        if checkin.energy_level is not None:
            parts.append(f"Energie: {checkin.energy_level}/5")
        if parts:
            lines.append(f"- Dnešní {' | '.join(parts)}")

    # 3. Last 3 craving events (no encrypted notes)
    cravings_result = await db.execute(
        select(CravingEvent)
        .where(CravingEvent.user_id == user_id)
        .order_by(CravingEvent.created_at.desc())
        .limit(3)
    )
    cravings = cravings_result.scalars().all()
    for c in cravings:
        parts_c = [f"intenzita {c.intensity}/10", f"spouštěč: {c.trigger_category}"]
        if c.outcome:
            outcome_cs = "odolal" if c.outcome == "resisted" else "neodolal"
            parts_c.append(f"výsledek: {outcome_cs}")
        lines.append(f"- Chuť: {', '.join(parts_c)}")

    # 4. Most recent AUDIT screening
    screening_result = await db.execute(
        select(ScreeningResult)
        .where(ScreeningResult.user_id == user_id)
        .order_by(ScreeningResult.completed_at.desc())
        .limit(1)
    )
    screening = screening_result.scalar_one_or_none()
    if screening:
        label = _RISK_LEVEL_CS.get(screening.risk_level, screening.risk_level)
        lines.append(f"- Screening AUDIT: skóre {screening.total_score} ({label})")

    if not lines:
        return ""

    return "KONTEXT UŽIVATELE:\n" + "\n".join(lines)
