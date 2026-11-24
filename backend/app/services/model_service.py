import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import xgboost as xgb
import pandas as pd
import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

class ModelService:
    _instance: Optional["ModelService"] = None
    _model: Optional[xgb.XGBClassifier] = None
    _feature_order: Optional[list] = None
    _metadata: Optional[dict] = None

    @classmethod
    def get_instance(cls) -> "ModelService":
        if cls._instance is None:
            cls._instance = ModelService()
        return cls._instance

    def load(self) -> None:
        if self._model is not None:
            return

        if settings.MODEL_PATH.exists():
            self._model = xgb.XGBClassifier()
            self._model.load_model(str(settings.MODEL_PATH))
            logger.info("XGBoost model loaded")
        else:
            logger.warning("Model file not found, using mock predictions")
            self._model = None

        if settings.FEATURE_ORDER_PATH.exists():
            with open(settings.FEATURE_ORDER_PATH) as f:
                self._feature_order = json.load(f)
        else:
            self._feature_order = []

        if settings.MODEL_METADATA_PATH.exists():
            with open(settings.MODEL_METADATA_PATH) as f:
                self._metadata = json.load(f)
        else:
            self._metadata = {}

    def predict(self, features: Dict[str, Any]) -> float:
        self.load()

        if self._model is None or not self._feature_order:
            return self._mock_predict(features)

        X = pd.DataFrame([features])[self._feature_order].fillna(0)
        proba = self._model.predict_proba(X)[0, 1]
        return float(proba)

    def _mock_predict(self, features: Dict[str, Any]) -> float:
        score = 0.5
        if features.get("margin_ratio", 0) > 0.2:
            score += 0.2
        if features.get("regularity_score", 0) > 0.5:
            score += 0.15
        if features.get("data_completeness", 1) < 0.5:
            score -= 0.2
        if features.get("has_inconsistencies", False):
            score -= 0.15
        return float(np.clip(score, 0, 1))

    def get_feature_names(self) -> list:
        self.load()
        return self._feature_order or []

    def get_metadata(self) -> dict:
        self.load()
        return self._metadata or {}

model_service = ModelService.get_instance()