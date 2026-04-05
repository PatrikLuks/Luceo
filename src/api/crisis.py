from fastapi import APIRouter

from src.core.crisis_contacts import CZECH_CRISIS_CONTACTS

router = APIRouter(prefix="/api/v1/crisis", tags=["crisis"])


@router.get("/contacts")
async def get_crisis_contacts():
    """Public endpoint — no auth required. Crisis contacts are life-critical."""
    return {"contacts": [c.model_dump() for c in CZECH_CRISIS_CONTACTS]}
