import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr | None = None  # Optional — anonymity is a feature
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(None, max_length=100)
    gdpr_consent: bool  # Must be True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    ai_disclaimer: str = (
        "Luceo is an AI-powered wellness tool, not a medical device or therapist replacement."
    )


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str | None
    display_name: str | None
    created_at: datetime
    data_region: str

    model_config = {"from_attributes": True}
