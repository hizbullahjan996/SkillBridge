"""Career prediction model loader and predictor."""
import json
import logging
from pathlib import Path

import joblib
import numpy as np

logger = logging.getLogger("skillbridge.ml")

_ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
_MODEL_PATH = _ARTIFACTS_DIR / "skillbridge_career_classifier.joblib"
_METADATA_PATH = _ARTIFACTS_DIR / "model_metadata.json"

_predictor_instance: "CareerPredictor | None" = None


class CareerPredictor:
    """Loads the trained model and provides career predictions."""

    def __init__(self) -> None:
        self.pipeline = None
        self.model = None
        self.encoders = None
        self.target_encoder = None
        self.feature_columns = None
        self.categorical_columns = None
        self.skill_columns = None
        self.metadata = None
        self._loaded = False

    def load(self) -> None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(f"Model artifact not found: {_MODEL_PATH}")

        self.pipeline = joblib.load(_MODEL_PATH)
        self.model = self.pipeline["model"]
        self.encoders = self.pipeline["encoders"]
        self.target_encoder = self.pipeline["target_encoder"]
        self.feature_columns = self.pipeline["feature_columns"]
        self.categorical_columns = self.pipeline["categorical_columns"]
        self.skill_columns = self.pipeline["skill_columns"]

        if _METADATA_PATH.exists():
            with open(_METADATA_PATH) as f:
                self.metadata = json.load(f)

        self._loaded = True
        logger.info(
            "Model loaded: %s (v%s, %d classes)",
            _MODEL_PATH.name,
            self.metadata.get("model_version", "unknown") if self.metadata else "unknown",
            len(self.target_encoder.classes_),
        )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def model_version(self) -> str:
        if self.metadata:
            return self.metadata.get("model_version", "1.0.0")
        return "1.0.0"

    @property
    def classes(self) -> list[str]:
        if self.target_encoder is None:
            return []
        return self.target_encoder.classes_.tolist()

    def predict_top_k(self, feature_dict: dict, k: int = 3) -> list[dict]:
        """Predict top-k career recommendations from a feature dictionary.

        Args:
            feature_dict: Dictionary with feature names as keys and values.
                Must include all features expected by the model.
            k: Number of top predictions to return.

        Returns:
            List of dicts with 'rank', 'career', and 'probability' keys.
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call load() first.")

        feature_array = self._prepare_features(feature_dict)
        probabilities = self.model.predict_proba(feature_array)[0]

        top_indices = np.argsort(probabilities)[::-1][:k]
        results = []
        for rank, idx in enumerate(top_indices, start=1):
            career_name = self.target_encoder.inverse_transform([idx])[0]
            prob = float(probabilities[idx])
            results.append({
                "rank": rank,
                "career": career_name,
                "probability": round(prob, 4),
            })

        return results

    def _prepare_features(self, feature_dict: dict) -> np.ndarray:
        """Convert a feature dictionary into the model's expected numpy array."""
        row = []
        for col in self.feature_columns:
            value = feature_dict.get(col, 0)
            if col in self.categorical_columns:
                encoder = self.encoders.get(col)
                if encoder is not None:
                    value_str = str(value)
                    if value_str in encoder.classes_:
                        value = int(encoder.transform([value_str])[0])
                    else:
                        value = -1
                else:
                    value = 0
            row.append(value)

        return np.array([row])


def get_predictor() -> CareerPredictor:
    """Get or create the singleton predictor instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = CareerPredictor()
    return _predictor_instance


def load_model() -> CareerPredictor:
    """Load the model into the singleton predictor."""
    predictor = get_predictor()
    if not predictor.is_loaded:
        predictor.load()
    return predictor
