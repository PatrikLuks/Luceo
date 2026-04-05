import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class ScreeningResult(BaseModel):
    __tablename__ = "screening_results"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    questionnaire_type: Mapped[str] = mapped_column(String(20), default="AUDIT")
    answers: Mapped[dict] = mapped_column(JSON)
    total_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(30))
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
