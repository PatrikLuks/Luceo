import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.core.crisis_contacts import CrisisContact


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    message: str
    crisis_detected: bool
    crisis_contacts: list[CrisisContact] | None = None
    disclaimer: str | None = None


class ConversationResponse(BaseModel):
    id: uuid.UUID
    started_at: datetime
    disclaimer_shown: bool
    disclaimer: str

    model_config = {"from_attributes": True}
