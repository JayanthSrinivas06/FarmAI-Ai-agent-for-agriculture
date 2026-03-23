from fastapi import APIRouter
from app.api.routes import districts, predict, farming_plan

api_router = APIRouter(prefix="/api")
api_router.include_router(districts.router)
api_router.include_router(predict.router)
api_router.include_router(farming_plan.router)

__all__ = ["api_router"]
