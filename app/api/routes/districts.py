from fastapi import APIRouter
from app.core.config import DISTRICTS

router = APIRouter(prefix="/districts", tags=["Districts"])


@router.get("", summary="List all available districts")
def get_districts() -> list[str]:
    """Return alphabetically sorted list of districts in the dataset."""
    return DISTRICTS
