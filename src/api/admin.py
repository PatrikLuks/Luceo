"""Admin/GDPR endpoints — data export and maintenance."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.admin import GDPRExportResponse
from src.api.schemas.auth import MessageResponse
from src.core.database import get_db
from src.core.deps import get_current_user
from src.core.rate_limit import limiter
from src.core.security import cleanup_expired_tokens, decrypt_field
from src.models.conversation import Conversation, Message
from src.models.screening import ScreeningResult
from src.models.tracking import CravingEvent, SobrietyCheckin
from src.models.user import User

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get(
    "/export-my-data",
    response_model=GDPRExportResponse,
    summary="Export user data (GDPR Art. 15)",
    description="Right of access. Export all user data as JSON: "
    "profile, check-ins, cravings, screenings, conversations (decrypted).",
)
@limiter.limit("5/minute")
async def export_my_data(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GDPR Article 15 — right of access. Export all user data as JSON."""
    # Checkins
    checkins_result = await db.execute(
        select(SobrietyCheckin)
        .where(SobrietyCheckin.user_id == user.id)
        .order_by(SobrietyCheckin.date)
    )
    checkins = []
    for c in checkins_result.scalars().all():
        notes = None
        if c.notes_encrypted:
            try:
                notes = decrypt_field(c.notes_encrypted, "sobriety_checkins.notes_encrypted")
            except Exception:
                notes = "[decryption_error]"
        checkins.append({
            "date": str(c.date),
            "is_sober": c.is_sober,
            "mood": c.mood,
            "energy_level": c.energy_level,
            "notes": notes,
        })

    # Cravings
    cravings_result = await db.execute(
        select(CravingEvent)
        .where(CravingEvent.user_id == user.id)
        .order_by(CravingEvent.created_at)
    )
    cravings = []
    for c in cravings_result.scalars().all():
        trigger_notes = None
        if c.trigger_notes_encrypted:
            try:
                trigger_notes = decrypt_field(
                    c.trigger_notes_encrypted,
                    "craving_events.trigger_notes_encrypted",
                )
            except Exception:
                trigger_notes = "[decryption_error]"
        cravings.append({
            "intensity": c.intensity,
            "trigger_category": c.trigger_category,
            "trigger_notes": trigger_notes,
            "coping_strategy_used": c.coping_strategy_used,
            "outcome": c.outcome,
            "created_at": c.created_at.isoformat(),
        })

    # Screenings
    screenings_result = await db.execute(
        select(ScreeningResult).where(ScreeningResult.user_id == user.id)
    )
    screenings = [
        {
            "type": s.questionnaire_type,
            "total_score": s.total_score,
            "risk_level": s.risk_level,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
        }
        for s in screenings_result.scalars().all()
    ]

    # Conversations (decrypted)
    convs_result = await db.execute(
        select(Conversation).where(Conversation.user_id == user.id)
    )
    conversations = []
    for conv in convs_result.scalars().all():
        msgs_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at)
        )
        messages = []
        for m in msgs_result.scalars().all():
            try:
                content = decrypt_field(m.content_encrypted, "messages.content_encrypted")
            except Exception:
                content = "[decryption_error]"
            messages.append(
                {"role": m.role, "content": content, "created_at": m.created_at.isoformat()}
            )
        conversations.append(
            {"started_at": conv.started_at.isoformat(), "messages": messages}
        )

    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "created_at": user.created_at.isoformat(),
            "data_region": user.data_region,
            "gdpr_consent_at": user.gdpr_consent_at.isoformat() if user.gdpr_consent_at else None,
            "gdpr_consent_version": user.gdpr_consent_version,
        },
        "checkins": checkins,
        "cravings": cravings,
        "screenings": screenings,
        "conversations": conversations,
    }


@router.post(
    "/cleanup-tokens",
    response_model=MessageResponse,
    summary="Cleanup expired tokens",
    description="Remove expired and revoked refresh tokens from the database.",
)
@limiter.limit("1/minute")
async def cleanup_tokens(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove expired and revoked refresh tokens from the database."""
    deleted = await cleanup_expired_tokens(db)
    await db.commit()
    return MessageResponse(message=f"Cleaned up {deleted} expired/revoked tokens.")
