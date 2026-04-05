import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class CheckinRequest(BaseModel):
    is_sober: bool
    mood: int | None = Field(None, ge=1, le=5)
    energy_level: int | None = Field(None, ge=1, le=5)
    notes: str | None = Field(None, max_length=2000)


class CheckinResponse(BaseModel):
    date: date
    is_sober: bool
    mood: int | None
    streak: int


class CravingRequest(BaseModel):
    intensity: int = Field(ge=1, le=10)
    trigger_category: str = Field(pattern="^(stress|social|emotional|habitual|environmental|other)$")
    trigger_notes: str | None = Field(None, max_length=2000)
    coping_strategy_used: str | None = Field(None, max_length=200)
    outcome: str | None = Field(None, pattern="^(resisted|gave_in)$")


class CravingResponse(BaseModel):
    id: uuid.UUID
    intensity: int
    trigger_category: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TrackingSummary(BaseModel):
    sober_days: int
    total_days: int
    average_mood: float | None
    total_cravings: int
    top_trigger: str | None
    current_streak: int
