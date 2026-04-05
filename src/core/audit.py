"""Audit trail logging for AI Act and GDPR compliance."""

import hashlib
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditLog

logger = logging.getLogger("luceo.audit")


async def log_audit_event(
    db: AsyncSession,
    action: str,
    *,
    user_id: uuid.UUID | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """Log an auditable event. IP is hashed (GDPR — no raw IPs stored)."""
    ip_hash = hashlib.sha256(ip_address.encode()).hexdigest() if ip_address else None

    entry = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_hash=ip_hash,
    )
    db.add(entry)
    # Caller is responsible for db.commit() — usually happens at request end
