import shap
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

from app.config import config
from src.model_loader import model_loader
from src.prediction_service import prediction_service
from app.database import data_manager

logger = logging.getLogger(__name__)

class ExplanationService:
    _instance = None
    _explainer = None
    _background_data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _ensure_explainer(self):
        if self._explainer is None:
            model = model_loader.load_model()
            feature_order = model_loader.load_feature_order()
            
            background_features = data_manager.load_features()
            X_background = background_features[feature_order].fillna(0).head(100).values
            
            self._explainer = shap.TreeExplainer(
                model,
                data=X_background,
                model_output="probability",
                feature_perturbation="interventional"
            )
            logger.info("SHAP explainer initialized")
    
    def explain(self, merchant_features: pd.Series, top_n: int = 10) -> Dict:
        self._ensure_explainer()
        
        feature_order = model_loader.load_feature_order()
        X = prediction_service.prepare_features(merchant_features)
        
        shap_values = self._explainer.shap_values(X)
        
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        shap_values = shap_values.flatten()
        
        feature_contributions = []
        for i, fname in enumerate(feature_order):
            feature_contributions.append({
                "feature": fname,
                "value": float(X[0, i]),
                "shap_value": float(shap_values[i]),
                "abs_shap": float(abs(shap_values[i])),
                "direction": "positive" if shap_values[i] > 0 else "negative"
            })
        
        feature_contributions.sort(key=lambda x: x["abs_shap"], reverse=True)
        top_factors = feature_contributions[:top_n]
        
        feature_labels = data_manager.load_feature_labels()
        
        explanations = []
        for factor in top_factors:
            fname = factor["feature"]
            label_info = feature_labels.get(fname, {})
            
            explanations.append({
                "feature": fname,
                "label": label_info.get("label", fname),
                "value": factor["value"],
                "contribution": factor["shap_value"],
                "direction": factor["direction"],
                "unit": label_info.get("unit", ""),
                "explanation": self._generate_explanation(fname, factor["shap_value"], factor["value"])
            })
        
        return {
            "top_factors": explanations,
            "all_contributions": feature_contributions,
            "expected_value": float(self._explainer.expected_value)
        }
    
    def _generate_explanation(self, feature: str, shap_value: float, value: float) -> str:
        direction = "améliore" if shap_value > 0 else "réduit"
        feature_labels = data_manager.load_feature_labels()
        label = feature_labels.get(feature, {}).get("label", feature)
        
        templates = data_manager.load_explanation_templates()
        template = templates.get(feature, "{direction} le score estimé.")
        
        try:
            return template.format(
                label=label,
                value=value,
                direction=direction,
                contribution=abs(shap_value)
            )
        except (ValueError, KeyError):
            # Fallback for templates that don't use format placeholders
            return f"{direction} le score estimé ({label}: {value:.2f})."

explanation_service = ExplanationService()