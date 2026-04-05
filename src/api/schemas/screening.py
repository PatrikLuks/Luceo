from pydantic import BaseModel, Field


class AuditSubmission(BaseModel):
    answers: list[int] = Field(min_length=10, max_length=10)


class AuditResultResponse(BaseModel):
    total_score: int
    risk_level: str
    recommendation: str
