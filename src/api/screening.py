from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.screening import (
    AuditQuestionsResponse,
    AuditResultResponse,
    AuditSubmission,
    ScreeningResultItem,
)
from src.api.utils import get_client_ip
from src.core.audit import log_audit_event
from src.core.database import get_db
from src.core.deps import get_current_user
from src.core.rate_limit import limiter
from src.models.screening import ScreeningResult
from src.models.user import User
from src.services.screening import AUDIT_QUESTIONS, score_audit

router = APIRouter(prefix="/api/v1/screening", tags=["screening"])


@router.get(
    "/questionnaires/audit",
    response_model=AuditQuestionsResponse,
    summary="Get AUDIT questionnaire",
    description="Return the WHO AUDIT questionnaire structure. No auth required.",
)
async def get_audit_questions():
    """Return the AUDIT questionnaire structure. No auth required (preview)."""
    return AuditQuestionsResponse(questions=AUDIT_QUESTIONS)


@router.post(
    "/questionnaires/audit",
    response_model=AuditResultResponse,
    summary="Submit AUDIT answers",
    description="Submit 10 AUDIT answers and receive risk assessment with Czech recommendation.",
)
@limiter.limit("60/minute")
async def submit_audit(
    body: AuditSubmission,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit AUDIT answers and get risk assessment."""
    # Validate answer values against actual option values (Q9/Q10 only accept {0, 2, 4})
    for i, answer in enumerate(body.answers):
        valid_values = {o.value for o in AUDIT_QUESTIONS[i].options}
        if answer not in valid_values:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Answer {i+1} must be one of {sorted(valid_values)}",
            )

    result = score_audit(body.answers)

    screening = ScreeningResult(
        user_id=user.id,
        questionnaire_type="AUDIT",
        answers={"answers": body.answers},
        total_score=result.total_score,
        risk_level=result.risk_level,
    )
    db.add(screening)
    await log_audit_event(
        db, "audit_completed",
        user_id=user.id,
        details={"total_score": result.total_score, "risk_level": result.risk_level},
        ip_address=get_client_ip(request),
    )
    await db.commit()

    return AuditResultResponse(
        total_score=result.total_score,
        risk_level=result.risk_level,
        recommendation=result.recommendation_cs,
    )


@router.get(
    "/results",
    response_model=list[ScreeningResultItem],
    summary="Get screening history",
)
async def get_screening_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's screening history."""
    result = await db.execute(
        select(ScreeningResult)
        .where(ScreeningResult.user_id == user.id)
        .order_by(ScreeningResult.completed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    screenings = result.scalars().all()
    return [
        ScreeningResultItem(
            id=s.id,
            type=s.questionnaire_type,
            total_score=s.total_score,
            risk_level=s.risk_level,
            completed_at=s.completed_at,
        )
        for s in screenings
    ]
