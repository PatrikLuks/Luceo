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
