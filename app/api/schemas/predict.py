from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    district: str
    season: str = "Kharif"          # "Kharif" | "Rabi"
    year: int = 2024
    NDVI_mean: float = Field(..., ge=-1, le=1)
    elevation: float = Field(..., ge=0)
    evapotranspiration: float = Field(..., ge=0)
    rain: float = Field(..., ge=0)
    slope: float = Field(..., ge=0)
    soil_carbon: float = Field(..., ge=0)
    soil_ph: float = Field(..., ge=0, le=14)
    soil_texture: int = Field(..., ge=1, le=5)
    temp: float = Field(..., ge=0)


class CropResult(BaseModel):
    crop: str
    probability: float


class PredictResponse(BaseModel):
    top5: list[CropResult]
    inputs: dict
