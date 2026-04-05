from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.tracking import (
    CheckinRequest,
    CheckinResponse,
    CravingRequest,
    CravingResponse,
    TrackingSummary,
)
from src.core.database import get_db
from src.core.deps import get_current_user
from src.core.security import encrypt_field
from src.models.tracking import CravingEvent, SobrietyCheckin
from src.models.user import User
from src.services.tracking import get_sobriety_streak, get_tracking_summary

router = APIRouter(prefix="/api/v1/tracking", tags=["tracking"])


@router.post("/checkin", response_model=CheckinResponse, status_code=status.HTTP_201_CREATED)
async def daily_checkin(
    body: CheckinRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Daily sobriety check-in. Upsert for the same date."""
    today = date.today()

    # Upsert: check if already logged today
    result = await db.execute(
        select(SobrietyCheckin).where(
            SobrietyCheckin.user_id == user.id, SobrietyCheckin.date == today
        )
    )
    checkin = result.scalar_one_or_none()

    notes_enc = encrypt_field(body.notes) if body.notes else None

    if checkin:
        checkin.is_sober = body.is_sober
        checkin.mood = body.mood
        checkin.energy_level = body.energy_level
        checkin.notes_encrypted = notes_enc
    else:
        checkin = SobrietyCheckin(
            user_id=user.id,
            date=today,
            is_sober=body.is_sober,
            mood=body.mood,
            energy_level=body.energy_level,
            notes_encrypted=notes_enc,
        )
        db.add(checkin)

    await db.commit()

    streak = await get_sobriety_streak(user.id, db)
    return CheckinResponse(date=today, is_sober=body.is_sober, mood=body.mood, streak=streak)


@router.get("/checkin/today")
async def get_today_checkin(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get today's check-in status."""
    result = await db.execute(
        select(SobrietyCheckin).where(
            SobrietyCheckin.user_id == user.id, SobrietyCheckin.date == date.today()
        )
    )
    checkin = result.scalar_one_or_none()
    if not checkin:
        return {"checked_in": False}

    return {
        "checked_in": True,
        "is_sober": checkin.is_sober,
        "mood": checkin.mood,
        "energy_level": checkin.energy_level,
    }


@router.post("/cravings", response_model=CravingResponse, status_code=status.HTTP_201_CREATED)
async def log_craving(
    body: CravingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log a craving event."""
    notes_enc = encrypt_field(body.trigger_notes) if body.trigger_notes else None

    event = CravingEvent(
        user_id=user.id,
        intensity=body.intensity,
        trigger_category=body.trigger_category,
        trigger_notes_encrypted=notes_enc,
        coping_strategy_used=body.coping_strategy_used,
        outcome=body.outcome,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


@router.get("/cravings")
async def list_cravings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List craving history."""
    result = await db.execute(
        select(CravingEvent)
        .where(CravingEvent.user_id == user.id)
        .order_by(CravingEvent.created_at.desc())
        .limit(100)
    )
    events = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "intensity": e.intensity,
            "trigger_category": e.trigger_category,
            "outcome": e.outcome,
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]


@router.get("/summary", response_model=TrackingSummary)
async def get_summary(
    days: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get tracking summary for the last N days."""
    summary = await get_tracking_summary(user.id, days, db)
    return TrackingSummary(**summary)


@router.get("/streak")
async def get_streak(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current sobriety streak."""
    streak = await get_sobriety_streak(user.id, db)
    return {"current_streak": streak}
