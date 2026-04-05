"""Chat orchestration service — the core product logic.

Flow for every user message:
1. Crisis detection (BEFORE anything else)
2. If crisis HIGH+ → predefined response, no LLM call
3. If crisis MEDIUM → flag to append crisis resources
4. Load conversation history
5. RAG: retrieve relevant clinical docs
6. Build system prompt
7. Call Claude API
8. Check output guardrails
9. Encrypt & store messages
10. Return response
"""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.audit import log_audit_event
from src.core.crisis import CrisisLevel, detect_crisis, get_crisis_response
from src.core.guardrails import SAFE_FALLBACK, check_response_guardrails
from src.core.prompts import DISCLAIMER_REMINDER, LUCEO_SYSTEM_PROMPT
from src.core.security import decrypt_field, encrypt_field
from src.models.conversation import Message
from src.services.anthropic_client import generate_response
from src.services.rag import format_context, retrieve_context

logger = logging.getLogger("luceo.chat")

MAX_HISTORY_MESSAGES = 20
DISCLAIMER_INTERVAL = 10  # Remind every N messages


async def process_message(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    content: str,
    db: AsyncSession,
) -> dict:
    """Process a user message and return assistant response.

    Returns dict with: message, crisis_detected, crisis_contacts, disclaimer.
    """
    # 1. Crisis detection — BEFORE anything else
    crisis_result = detect_crisis(content)

    # Store user message (encrypted)
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content_encrypted=encrypt_field(content),
        crisis_level=crisis_result.level.value,
    )
    db.add(user_msg)

    # 2. If crisis HIGH or CRITICAL → predefined response, NO LLM call
    if crisis_result.level in (CrisisLevel.HIGH, CrisisLevel.CRITICAL):
        response_text = get_crisis_response(crisis_result)
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content_encrypted=encrypt_field(response_text),
            crisis_level=crisis_result.level.value,
        )
        db.add(assistant_msg)
        await db.commit()

        return {
            "message": response_text,
            "crisis_detected": True,
            "crisis_contacts": [c.model_dump() for c in crisis_result.crisis_contacts],
            "disclaimer": None,
        }

    # 3. Load conversation history
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(MAX_HISTORY_MESSAGES)
    )
    history_msgs = list(reversed(result.scalars().all()))

    messages = []
    for msg in history_msgs:
        try:
            decrypted = decrypt_field(msg.content_encrypted)
        except Exception:
            decrypted = "[encrypted message]"
        messages.append({"role": msg.role, "content": decrypted})

    # Add current message
    messages.append({"role": "user", "content": content})

    # 4. RAG: retrieve relevant clinical docs
    docs = await retrieve_context(content, db)
    rag_context = format_context(docs)

    # 5. Build system prompt
    user_context = ""  # TODO: inject sobriety streak, mood data
    system_prompt = LUCEO_SYSTEM_PROMPT.format(
        rag_context=rag_context,
        user_context=user_context,
    )

    # 6. Call Claude API
    response_text, token_count = await generate_response(system_prompt, messages)

    # 7. Check output guardrails
    is_safe, reason = check_response_guardrails(response_text)
    if not is_safe:
        logger.warning("Guardrail triggered: %s", reason)
        response_text = SAFE_FALLBACK

    # 8. Append crisis resources for MEDIUM level
    if crisis_result.level == CrisisLevel.MEDIUM:
        response_text += get_crisis_response(crisis_result)

    # 9. Determine if disclaimer reminder is needed
    msg_count = len(history_msgs)
    disclaimer = DISCLAIMER_REMINDER if msg_count > 0 and msg_count % DISCLAIMER_INTERVAL == 0 else None

    # 10. Store assistant message
    assistant_msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content_encrypted=encrypt_field(response_text),
        crisis_level=crisis_result.level.value,
        token_count=token_count,
    )
    db.add(assistant_msg)

    await log_audit_event(
        db, "chat_message",
        user_id=user_id,
        details={"crisis_level": crisis_result.level.value},
    )

    await db.commit()

    return {
        "message": response_text,
        "crisis_detected": crisis_result.level != CrisisLevel.NONE,
        "crisis_contacts": (
            [c.model_dump() for c in crisis_result.crisis_contacts]
            if crisis_result.level == CrisisLevel.MEDIUM
            else None
        ),
        "disclaimer": disclaimer,
    }
