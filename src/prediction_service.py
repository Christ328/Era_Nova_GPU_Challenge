import xgboost as xgb
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

from app.config import config
from src.model_loader import model_loader

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        self._model = None
        self._feature_order = None
        self._feature_schema = None
    
    def _ensure_loaded(self):
        if self._model is None:
            self._model = model_loader.load_model()
            self._feature_order = model_loader.load_feature_order()
            self._feature_schema = model_loader.load_feature_schema()
    
    def prepare_features(self, merchant_features: pd.Series) -> np.ndarray:
        self._ensure_loaded()
        
        feature_vector = []
        for feature_name in self._feature_order:
            if feature_name in merchant_features.index:
                value = merchant_features[feature_name]
                if pd.isna(value):
                    value = 0.0
                feature_vector.append(float(value))
            else:
                feature_vector.append(0.0)
        
        return np.array(feature_vector).reshape(1, -1)
    
    def predict_proba(self, merchant_features: pd.Series) -> float:
        self._ensure_loaded()
        
        X = self.prepare_features(merchant_features)
        dmatrix = xgb.DMatrix(X, feature_names=self._feature_order)
        proba = self._model.predict(dmatrix)[0]
        
        return float(proba)
    
    def predict(self, merchant_features: pd.Series) -> Tuple[float, int]:
        proba = self.predict_proba(merchant_features)
        score = int(round(proba * 100))
        return proba, score
    
    def get_risk_level(self, score: int) -> Dict:
        for level, info in config.RISK_LEVELS.items():
            if info["min"] <= score <= info["max"]:
                return {"level": level, **info}
        return {"level": "unknown", "label": "Inconnu", "color": "#6b7280"}
    
    def get_confidence_level(self, confidence: float) -> Dict:
        for level, info in config.CONFIDENCE_LEVELS.items():
            if info["min"] <= confidence <= info["max"]:
                return {"level": level, **info}
        return {"level": "unknown", "label": "Inconnue", "color": "#6b7280"}

prediction_service = PredictionService()