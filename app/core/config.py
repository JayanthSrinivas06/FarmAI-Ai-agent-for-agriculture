"""
RakiCrops AI – Application Configuration
"""
import os
from pathlib import Path

# Raki_crops/ (three levels up from app/core/config.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ── Paths ──────────────────────────────────────────────────────────────────
MODEL_PATH   = PROJECT_ROOT / "model" / "best_model.pkl"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# ── ML Constants ───────────────────────────────────────────────────────────
# Districts exactly as they appear in the dataset (LabelEncoder sorts alphabetically)
DISTRICTS = sorted([
    "Adilabad", "Anantapur", "Chittoor", "Cuddapah", "East Godavari",
    "Guntur", "Karimnagar", "Khammam", "Krishna", "Kurnool",
    "Mahbubnagar", "Medak", "Nalgonda", "Nellore", "Nizamabad",
    "Prakasam", "Rangareddi", "Srikakulam", "Vishakhapatnam",
    "Vizianagaram", "Warangal", "West Godavari",
])

DISTRICT_MAP = {d: i for i, d in enumerate(DISTRICTS)}

# Alphabetical order produced by sklearn LabelEncoder during training
CROP_LABELS = [
    "Arhar/Tur", "Bajra", "Castor seed", "Coriander", "Cotton",
    "Cowpea", "Dry chillies", "Gram", "Green Gram", "Groundnut",
    "Guar", "Horse gram", "Jowar", "Maize", "Niger seed",
    "Onion", "Potato", "Ragi", "Rapeseed mustard", "Rice",
    "Safflower", "Sesamum", "Small millets", "Soyabean", "Sunflower",
    "Sweet potato", "Tapioca", "Tobacco", "Urad", "Wheat",
]

FEATURE_COLS = [
    "NDVI_mean", "elevation", "evapotranspiration", "rain",
    "slope", "soil_carbon", "soil_ph", "soil_texture", "temp", "year",
    "season", "district",
]

# ── External API ────────────────────────────────────────────────────────────
# Read lazily via property so .env loaded in main.py is always picked up

def get_gemini_api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", "")

# Convenience alias (evaluated at runtime, not import time)
GEMINI_API_KEY: str = ""   # placeholder – use get_gemini_api_key() where freshness matters
GEMINI_MODEL   = "gemini-2.5-flash"   # free-tier supported model
