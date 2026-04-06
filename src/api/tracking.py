from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.tracking import (
    CheckinRequest,
    CheckinResponse,
    CravingListItem,
    CravingRequest,
    CravingResponse,
    StreakResponse,
    TodayCheckinResponse,
    TrackingSummary,
)
from src.api.utils import get_client_ip
from src.core.audit import log_audit_event
from src.core.database import get_db
from src.core.deps import get_current_user
from src.core.rate_limit import limiter
from src.core.security import encrypt_field
from src.models.tracking import CravingEvent, SobrietyCheckin
from src.models.user import User
from src.services.tracking import get_sobriety_streak, get_tracking_summary

router = APIRouter(prefix="/api/v1/tracking", tags=["tracking"])


@router.post(
    "/checkin",
    response_model=CheckinResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Daily sobriety check-in",
    description="Log daily sobriety status, mood (1-5), and energy level (1-5). "
    "Upsert: updates if already checked in today.",
)
@limiter.limit("60/minute")
async def daily_checkin(
    body: CheckinRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Daily sobriety check-in. Upsert for the same date."""
    today = datetime.now(UTC).date()

    # Upsert: check if already logged today
    result = await db.execute(
        select(SobrietyCheckin).where(
            SobrietyCheckin.user_id == user.id, SobrietyCheckin.date == today
        )
    )
    checkin = result.scalar_one_or_none()

    notes_enc = (
        encrypt_field(body.notes, "sobriety_checkins.notes_encrypted")
        if body.notes else None
    )

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

    await log_audit_event(
        db, "checkin_logged",
        user_id=user.id,
        details={"is_sober": body.is_sober},
        ip_address=get_client_ip(request),
    )
    try:
        await db.commit()
    except IntegrityError:
        # Race condition: concurrent insert for same user+date
        await db.rollback()
        result = await db.execute(
            select(SobrietyCheckin).where(
                SobrietyCheckin.user_id == user.id, SobrietyCheckin.date == today
            )
        )
        checkin = result.scalar_one_or_none()
        if checkin:
            checkin.is_sober = body.is_sober
            checkin.mood = body.mood
            checkin.energy_level = body.energy_level
            checkin.notes_encrypted = notes_enc
            await db.commit()

    streak = await get_sobriety_streak(user.id, db)
    return CheckinResponse(date=today, is_sober=body.is_sober, mood=body.mood, streak=streak)


@router.get(
    "/checkin/today",
    response_model=TodayCheckinResponse,
    summary="Today's check-in status",
)
async def get_today_checkin(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get today's check-in status."""
    result = await db.execute(
        select(SobrietyCheckin).where(
            SobrietyCheckin.user_id == user.id,
            SobrietyCheckin.date == datetime.now(UTC).date(),
        )
    )
    checkin = result.scalar_one_or_none()
    if not checkin:
        return TodayCheckinResponse(checked_in=False)

    return TodayCheckinResponse(
        checked_in=True,
        is_sober=checkin.is_sober,
        mood=checkin.mood,
        energy_level=checkin.energy_level,
    )


@router.post(
    "/cravings",
    response_model=CravingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Log a craving event",
    description="Record a craving with intensity (1-10), "
    "trigger category, coping strategy, and outcome.",
)
@limiter.limit("60/minute")
async def log_craving(
    body: CravingRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log a craving event."""
    notes_enc = (
        encrypt_field(body.trigger_notes, "craving_events.trigger_notes_encrypted")
        if body.trigger_notes else None
    )

    event = CravingEvent(
        user_id=user.id,
        intensity=body.intensity,
        trigger_category=body.trigger_category,
        trigger_notes_encrypted=notes_enc,
        coping_strategy_used=body.coping_strategy_used,
        outcome=body.outcome,
    )
    db.add(event)

    await log_audit_event(
        db, "craving_logged",
        user_id=user.id,
        details={"intensity": body.intensity, "trigger_category": body.trigger_category},
        ip_address=get_client_ip(request),
    )
    await db.commit()
    await db.refresh(event)
    return event


@router.get(
    "/cravings",
    response_model=list[CravingListItem],
    summary="List craving history",
)
async def list_cravings(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List craving history."""
    result = await db.execute(
        select(CravingEvent)
        .where(CravingEvent.user_id == user.id)
        .order_by(CravingEvent.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get(
    "/summary",
    response_model=TrackingSummary,
    summary="Get tracking summary",
    description="Aggregated statistics for the last N days (default 30): "
    "sober days, average mood, craving count, and top trigger.",
)
async def get_summary(
    days: int = Query(30, ge=1, le=365),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get tracking summary for the last N days."""
    summary = await get_tracking_summary(user.id, days, db)
    return TrackingSummary(**summary)


@router.get("/streak", response_model=StreakResponse, summary="Get sobriety streak")
async def get_streak(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current sobriety streak."""
    streak = await get_sobriety_streak(user.id, db)
    return StreakResponse(current_streak=streak)
