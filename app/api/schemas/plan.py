from pydantic import BaseModel


class PlanRequest(BaseModel):
    crop: str
    inputs: dict


class PlanResponse(BaseModel):
    plan: str
