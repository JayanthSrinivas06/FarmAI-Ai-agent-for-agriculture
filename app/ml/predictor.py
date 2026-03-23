"""ML model loading and inference."""
import numpy as np
import pandas as pd
import joblib

from app.core.config import MODEL_PATH, CROP_LABELS, DISTRICT_MAP, FEATURE_COLS


class CropPredictor:
    def __init__(self):
        self._model = joblib.load(MODEL_PATH)

    def predict_top_n(self, features: dict, n: int = 5) -> list[dict]:
        """Return top-n crops with their probability percentages."""
        df = pd.DataFrame([features])[FEATURE_COLS]
        probs = self._model.predict_proba(df)[0]
        top_idx = np.argsort(probs)[::-1][:n]
        return [
            {"crop": CROP_LABELS[i], "probability": round(float(probs[i]) * 100, 2)}
            for i in top_idx
        ]

    @staticmethod
    def encode_inputs(district: str, season: str, year: int, **kwargs) -> dict:
        district_enc = DISTRICT_MAP.get(district, 0)
        season_enc   = 0 if season == "Kharif" else 1
        return {
            "district":           district_enc,
            "season":             season_enc,
            "year":               year,
            **kwargs,
        }


# Module-level singleton
predictor = CropPredictor()

__all__ = ["predictor"]
