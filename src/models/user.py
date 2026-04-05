from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    # Email is OPTIONAL — Karel persona needs anonymity
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    # GDPR consent tracking (Article 7)
    gdpr_consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    gdpr_consent_version: Mapped[str | None] = mapped_column(String(20))
    data_region: Mapped[str] = mapped_column(String(20), default="eu-central")

    # Profile (minimal — data minimization principle)
    display_name: Mapped[str | None] = mapped_column(String(100))

    # Soft delete for GDPR Article 17 (right to erasure)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
