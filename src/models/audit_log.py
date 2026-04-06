import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action: Mapped[str] = mapped_column(String(50), index=True)
    # e.g. "chat_message", "crisis_detected", "login", "gdpr_deletion"
    details: Mapped[dict | None] = mapped_column(JSON)
    ip_hash: Mapped[str | None] = mapped_column(String(64))  # SHA-256 of IP (GDPR)
    # Timestamp is inherited from BaseModel.created_at
