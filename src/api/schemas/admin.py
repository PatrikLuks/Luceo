"""GDPR export response schemas."""

from pydantic import BaseModel


class ExportUserData(BaseModel):
    id: str
    email: str | None
    display_name: str | None
    created_at: str
    data_region: str
    gdpr_consent_at: str | None
    gdpr_consent_version: str | None


class ExportCheckin(BaseModel):
    date: str
    is_sober: bool
    mood: int | None
    energy_level: int | None
    notes: str | None


class ExportCraving(BaseModel):
    intensity: int
    trigger_category: str
    trigger_notes: str | None
    coping_strategy_used: str | None
    outcome: str | None
    created_at: str


class ExportScreening(BaseModel):
    type: str
    total_score: int
    risk_level: str
    completed_at: str | None


class ExportMessage(BaseModel):
    role: str
    content: str
    created_at: str


class ExportConversation(BaseModel):
    started_at: str
    messages: list[ExportMessage]


class GDPRExportResponse(BaseModel):
    user: ExportUserData
    checkins: list[ExportCheckin]
    cravings: list[ExportCraving]
    screenings: list[ExportScreening]
    conversations: list[ExportConversation]
