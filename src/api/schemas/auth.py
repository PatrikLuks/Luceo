import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: str | None = None  # Optional — anonymity is a feature
    password: str = Field(min_length=8)
    display_name: str | None = None
    gdpr_consent: bool  # Must be True


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    ai_disclaimer: str = (
        "Luceo is an AI-powered wellness tool, not a medical device or therapist replacement."
    )


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str | None
    display_name: str | None
    created_at: datetime
    data_region: str

    model_config = {"from_attributes": True}
