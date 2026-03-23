from fastapi import APIRouter, HTTPException
from google.genai import errors as genai_errors
from app.api.schemas.plan import PlanRequest, PlanResponse
from app.core.config import GEMINI_MODEL, get_gemini_api_key
from app.core.gemini_client import get_gemini_client

router = APIRouter(prefix="/farming-plan", tags=["Farming Plan"])


def _build_prompt(crop: str, inp: dict) -> str:
    return f"""
You are an expert agricultural advisor for Andhra Pradesh / Telangana, India.

A farmer wants to grow **{crop}** under these environmental and soil conditions:

| Parameter            | Value |
|----------------------|-------|
| District             | {inp.get('district', 'N/A')} |
| Season               | {inp.get('season', 'N/A')} |
| Year                 | {inp.get('year', 'N/A')} |
| NDVI (mean)          | {inp.get('NDVI_mean', 'N/A')} |
| Elevation (m)        | {inp.get('elevation', 'N/A')} |
| Evapotranspiration   | {inp.get('evapotranspiration', 'N/A')} |
| Rainfall (mm)        | {inp.get('rain', 'N/A')} |
| Slope                | {inp.get('slope', 'N/A')} |
| Soil Carbon          | {inp.get('soil_carbon', 'N/A')} |
| Soil pH              | {inp.get('soil_ph', 'N/A')} |
| Soil Texture (1-5)   | {inp.get('soil_texture', 'N/A')} |
| Temperature (°C)     | {inp.get('temp', 'N/A')} |

Please provide a detailed response with these three sections:

## 1. 🌾 Complete Agriculture Plan
Step-by-step farming guide from land preparation to harvest, covering:
- Land preparation
- Seed selection & treatment
- Sowing method & spacing
- Irrigation schedule (based on rainfall & evapotranspiration values)
- Fertilizer & nutrient management (account for soil pH and carbon)
- Pest & disease management
- Harvesting method & timing

## 2. 📅 Month-by-Month Timeline
A clear timeline for the **{inp.get('season', 'Kharif')} season**, listing farmer tasks for each month.

## 3. 💰 Market Price Forecast (per KG after harvest)
Based on current Indian agricultural market trends for **{crop}** in **{inp.get('district', 'N/A')}**:
- Estimated selling price per KG (₹)
- Price-influencing factors (demand, quality grade, season, MSP, etc.)
- Key price risks to watch

Keep the response practical and farmer-friendly. Use clear headings, bullet points, and emojis.
"""


@router.post("", response_model=PlanResponse, summary="Generate AI farming plan")
async def farming_plan(req: PlanRequest) -> PlanResponse:
    """
    Uses Gemini AI to generate a complete agriculture plan, timeline,
    and market price forecast for a selected crop and field conditions.
    """
    if not get_gemini_api_key():
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not set. Add it to your .env file."
        )

    prompt = _build_prompt(req.crop, req.inputs)
    client = get_gemini_client()

    try:
        response = client.models.generate_content(
            model    = GEMINI_MODEL,
            contents = prompt,
        )
        return PlanResponse(plan=response.text)

    except genai_errors.ClientError as e:
        status = e.status_code if hasattr(e, "status_code") else 500
        # Friendly messages for common error codes
        if status == 429:
            detail = (
                "Gemini API quota exceeded (free tier limit reached). "
                "Please wait a minute and try again, or upgrade your Google AI plan."
            )
        elif status == 401 or status == 403:
            detail = "Invalid or unauthorised GEMINI_API_KEY. Please check your .env file."
        else:
            detail = f"Gemini API error ({status}): {str(e)}"
        raise HTTPException(status_code=status if status < 600 else 500, detail=detail)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

