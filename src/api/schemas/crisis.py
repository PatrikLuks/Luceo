"""Crisis endpoint response schemas."""

from pydantic import BaseModel

from src.core.crisis_contacts import CrisisContact


class CrisisContactsResponse(BaseModel):
    contacts: list[CrisisContact]
