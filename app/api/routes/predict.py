from fastapi import APIRouter
from app.api.schemas.predict import PredictRequest, PredictResponse
from app.ml.predictor import predictor

router = APIRouter(prefix="/predict", tags=["Predict"])


@router.post("", response_model=PredictResponse, summary="Predict top-5 crops")
def predict(req: PredictRequest) -> PredictResponse:
    """
    Accepts field parameters and returns the top-5 recommended crops
    with probability scores using the trained Random Forest model.
    """
    features = predictor.encode_inputs(
        district          = req.district,
        season            = req.season,
        year              = req.year,
        NDVI_mean         = req.NDVI_mean,
        elevation         = req.elevation,
        evapotranspiration= req.evapotranspiration,
        rain              = req.rain,
        slope             = req.slope,
        soil_carbon       = req.soil_carbon,
        soil_ph           = req.soil_ph,
        soil_texture      = req.soil_texture,
        temp              = req.temp,
    )
    top5 = predictor.predict_top_n(features, n=5)
    return PredictResponse(top5=top5, inputs=req.model_dump())
