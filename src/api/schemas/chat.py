import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.core.crisis_contacts import CrisisContact


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime
    crisis_detected: bool = False


class ChatResponse(BaseModel):
    message: str
    crisis_detected: bool
    crisis_contacts: list[dict] | None = None
    disclaimer: str | None = None


class ConversationResponse(BaseModel):
    id: uuid.UUID
    started_at: datetime
    disclaimer: str

    model_config = {"from_attributes": True}
