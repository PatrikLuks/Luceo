import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.chat import ChatResponse, ConversationResponse, SendMessageRequest
from src.core.database import get_db
from src.core.deps import get_current_user
from src.core.prompts import AI_DISCLAIMER
from src.core.rate_limit import limiter
from src.models.conversation import Conversation
from src.models.user import User
from src.services.chat import process_message

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new conversation. Returns AI disclaimer (AI Act compliance)."""
    conv = Conversation(user_id=user.id, disclaimer_shown=True)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return ConversationResponse(
        id=conv.id,
        started_at=conv.started_at,
        disclaimer_shown=conv.disclaimer_shown,
        disclaimer=AI_DISCLAIMER,
    )


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
@limiter.limit("20/minute")
async def send_message(
    conversation_id: uuid.UUID,
    body: SendMessageRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get an AI response."""
    # Verify conversation belongs to user
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    response = await process_message(user.id, conversation_id, body.content, db)
    return ChatResponse(**response)


@router.get("/conversations")
async def list_conversations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user's conversations."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.started_at.desc())
        .limit(50)
    )
    convs = result.scalars().all()
    return [
        {"id": str(c.id), "started_at": c.started_at.isoformat()}
        for c in convs
    ]
