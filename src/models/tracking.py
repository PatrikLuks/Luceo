import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel


class SobrietyCheckin(BaseModel):
    __tablename__ = "sobriety_checkins"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    is_sober: Mapped[bool] = mapped_column(Boolean)
    mood: Mapped[int | None] = mapped_column(Integer)  # 1-5
    energy_level: Mapped[int | None] = mapped_column(Integer)  # 1-5
    notes_encrypted: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_checkin_user_date"),
    )


class CravingEvent(BaseModel):
    __tablename__ = "craving_events"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    intensity: Mapped[int] = mapped_column(Integer)  # 1-10
    trigger_category: Mapped[str] = mapped_column(
        String(30)
    )  # stress, social, emotional, habitual, environmental, other
    trigger_notes_encrypted: Mapped[str | None] = mapped_column(Text)
    coping_strategy_used: Mapped[str | None] = mapped_column(String(200))
    outcome: Mapped[str | None] = mapped_column(String(20))  # resisted, gave_in
