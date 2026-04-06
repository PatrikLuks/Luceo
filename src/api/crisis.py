from fastapi import APIRouter

from src.api.schemas.crisis import CrisisContactsResponse
from src.core.crisis_contacts import CZECH_CRISIS_CONTACTS

router = APIRouter(prefix="/api/v1/crisis", tags=["crisis"])


@router.get("/contacts", response_model=CrisisContactsResponse)
async def get_crisis_contacts():
    """Public endpoint — no auth required. Crisis contacts are life-critical."""
    return CrisisContactsResponse(contacts=CZECH_CRISIS_CONTACTS)
