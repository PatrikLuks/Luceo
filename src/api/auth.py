from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from src.core.audit import log_audit_event
from src.core.database import get_db
from src.core.deps import get_current_user
from src.core.rate_limit import limiter
from src.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    revoke_refresh_token,
    verify_password,
    verify_refresh_token,
)
from src.models.audit_log import AuditLog
from src.models.conversation import Conversation, Message
from src.models.refresh_token import RefreshToken
from src.models.screening import ScreeningResult
from src.models.tracking import CravingEvent, SobrietyCheckin
from src.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

GDPR_CONSENT_VERSION = "1.0"


def _get_client_ip(request: Request) -> str | None:
    """Safely extract client IP — request.client can be None behind some proxies."""
    return request.client.host if request.client else None


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    req: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)
):
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
        gdpr_consent_at=datetime.now(UTC),
        gdpr_consent_version=GDPR_CONSENT_VERSION,
    )
    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered."
        )
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    refresh = await create_refresh_token(user.id, db)

    await log_audit_event(
        db, "user_register", user_id=user.id, ip_address=_get_client_ip(request)
    )
    await db.commit()

    return TokenResponse(access_token=token, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == req.email, User.is_active == True)  # noqa: E712
    )
    user = result.scalar_one_or_none()

    # Constant-time: always run verify_password to prevent timing-based email enumeration
    _dummy_hash = "$2b$12$LJ3m4ys3Lg3DEQFIY3Bqxe1111111111111111111111111111111"
    if not verify_password(req.password, user.password_hash if user else _dummy_hash) or not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    token = create_access_token({"sub": str(user.id)})
    refresh = await create_refresh_token(user.id, db)

    await log_audit_event(
        db, "user_login", user_id=user.id, ip_address=_get_client_ip(request)
    )
    await db.commit()

    return TokenResponse(access_token=token, refresh_token=refresh)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
    await db.execute(delete(AuditLog).where(AuditLog.user_id == user.id))
    await db.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))

    # Log the deletion event (will be committed with PII wipe below)
    await log_audit_event(
        db, "gdpr_deletion", user_id=user.id, ip_address=_get_client_ip(request)
    )

    # Wipe user PII
    user.is_active = False
    user.deleted_at = datetime.now(UTC)
    user.email = None
    user.display_name = None
    user.password_hash = "!"  # Unix locked-account convention
    await db.commit()


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh_tokens(
    body: RefreshRequest, request: Request, db: AsyncSession = Depends(get_db)
):
    """Exchange a valid refresh token for new access + refresh tokens (rotation)."""
    try:
        old_entry = await verify_refresh_token(body.refresh_token, db)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Revoke old token (rotation)
    await revoke_refresh_token(old_entry)

    # Issue new pair
    new_access = create_access_token({"sub": str(old_entry.user_id)})
    new_refresh = await create_refresh_token(old_entry.user_id, db)
    await db.commit()

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Revoke a refresh token (logout). Idempotent."""
    try:
        entry = await verify_refresh_token(body.refresh_token, db)
        await revoke_refresh_token(entry)
        await db.commit()
    except ValueError:
        pass  # Token already invalid — idempotent
