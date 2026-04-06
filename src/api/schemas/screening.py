import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AuditSubmission(BaseModel):
    answers: list[int] = Field(min_length=10, max_length=10)


class AuditResultResponse(BaseModel):
    total_score: int
    risk_level: str
    recommendation: str


class AuditOptionResponse(BaseModel):
    text_cs: str
    text_en: str
    value: int

    model_config = {"from_attributes": True}


class AuditQuestionResponse(BaseModel):
    number: int
    text_cs: str
    text_en: str
    options: list[AuditOptionResponse]

    model_config = {"from_attributes": True}


class AuditQuestionsResponse(BaseModel):
    questions: list[AuditQuestionResponse]


class ScreeningResultItem(BaseModel):
    id: uuid.UUID
    type: str
    total_score: int
    risk_level: str
    completed_at: datetime | None

    model_config = {"from_attributes": True}
