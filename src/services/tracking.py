"""Sobriety tracking business logic — streak calculation, summaries."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
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
    """Get aggregate tracking stats for the last N days."""
    since = datetime.now(UTC).date() - timedelta(days=days)

    # Sobriety stats
    checkins_result = await db.execute(
        select(SobrietyCheckin).where(
            SobrietyCheckin.user_id == user_id,
            SobrietyCheckin.date >= since,
        )
    )
    checkins = checkins_result.scalars().all()

    sober_days = sum(1 for c in checkins if c.is_sober)
    moods = [c.mood for c in checkins if c.mood is not None]
    avg_mood = sum(moods) / len(moods) if moods else None

    # Craving stats
    cravings_result = await db.execute(
        select(CravingEvent).where(
            CravingEvent.user_id == user_id,
            CravingEvent.created_at >= since,
        )
    )
    cravings = cravings_result.scalars().all()

    # Find most common trigger
    trigger_counts: dict[str, int] = {}
    for c in cravings:
        trigger_counts[c.trigger_category] = trigger_counts.get(c.trigger_category, 0) + 1
    top_trigger = max(trigger_counts, key=trigger_counts.get) if trigger_counts else None

    streak = await get_sobriety_streak(user_id, db)

    return {
        "sober_days": sober_days,
        "total_days": len(checkins),
        "average_mood": round(avg_mood, 1) if avg_mood else None,
        "total_cravings": len(cravings),
        "top_trigger": top_trigger,
        "current_streak": streak,
    }
