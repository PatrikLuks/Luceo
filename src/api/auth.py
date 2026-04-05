from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from src.core.database import get_db
from src.core.deps import get_current_user
from src.core.security import create_access_token, hash_password, verify_password
from src.models.conversation import Conversation, Message
from src.models.screening import ScreeningResult
from src.models.tracking import CravingEvent, SobrietyCheckin
from src.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

GDPR_CONSENT_VERSION = "1.0"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if not req.gdpr_consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GDPR consent is required to create an account.",
        )

    # Check email uniqueness if provided
    if req.email:
        existing = await db.execute(select(User).where(User.email == req.email))
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered."
            )

    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        display_name=req.display_name,
        gdpr_consent_at=datetime.now(timezone.utc),
        gdpr_consent_version=GDPR_CONSENT_VERSION,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == req.email, User.is_active == True)  # noqa: E712
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """GDPR Article 17 — right to erasure. Soft-deletes user and wipes ALL PII."""
    # Delete related data (messages first due to FK, then conversations)
    user_convos = await db.execute(
        select(Conversation.id).where(Conversation.user_id == user.id)
    )
    convo_ids = [row[0] for row in user_convos.all()]
    if convo_ids:
        await db.execute(delete(Message).where(Message.conversation_id.in_(convo_ids)))
        await db.execute(delete(Conversation).where(Conversation.user_id == user.id))

    await db.execute(delete(ScreeningResult).where(ScreeningResult.user_id == user.id))
    await db.execute(delete(SobrietyCheckin).where(SobrietyCheckin.user_id == user.id))
    await db.execute(delete(CravingEvent).where(CravingEvent.user_id == user.id))

    # Wipe user PII
    user.is_active = False
    user.deleted_at = datetime.now(timezone.utc)
    user.email = None
    user.display_name = None
    user.password_hash = "REDACTED"
    await db.commit()
