from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from app.config import config
from app.database import data_manager
from src.prediction_service import prediction_service
from src.explain import explanation_service
from src.rules_engine import rules_engine, RuleResult

logger = logging.getLogger(__name__)

@dataclass
class ScoringResult:
    merchant_id: str
    score: int
    proba: float
    risk_level: Dict
    confidence: float
    confidence_level: Dict
    recommended_amount_min: int
    recommended_amount_max: int
    recommended_duration_months: int
    product_type: str
    product_info: Dict
    top_factors: List[Dict]
    alerts: List[RuleResult]
    human_review_required: bool
    explanation: str
    adjustments: Dict

class ScoringEngine:
    def __init__(self):
        self.prediction_service = prediction_service
        self.explanation_service = explanation_service
        self.rules_engine = rules_engine
    
    def calculate_confidence(self, merchant: Dict, features: Dict, proba: float) -> float:
        completeness = merchant.get('data_completeness', 1.0)
        history_months = merchant.get('activity_age_months', 12)
        volatility = features.get('income_volatility', 0.3)
        
        base_confidence = 70
        if completeness > 0.9:
            base_confidence += 15
        elif completeness < 0.7:
            base_confidence -= 20
        
        if history_months >= 12:
            base_confidence += 10
        elif history_months < 6:
            base_confidence -= 15
        
        if volatility < 0.3:
            base_confidence += 10
        elif volatility > 0.5:
            base_confidence -= 10
        
        if proba > 0.8 or proba < 0.2:
            base_confidence += 5
        
        return max(0, min(100, base_confidence))
    
    def recommend_amount(self, merchant: Dict, score: int, adjustments: Dict) -> Tuple[int, int]:
        base_min = config.PRODUCT_TYPES["progressive_microloan"]["min_amount"]
        base_max = config.PRODUCT_TYPES["progressive_microloan"]["max_amount"]
        
        if merchant.get('is_first_time_borrower', False):
            base_min = 50000
            base_max = 150000
        elif score >= 75:
            base_min = 200000
            base_max = 1000000
        elif score >= 60:
            base_min = 100000
            base_max = 500000
        
        multiplier = adjustments.get("amount_multiplier", 1.0)
        base_min = int(base_min * multiplier)
        base_max = int(base_max * multiplier)
        
        return base_min, base_max
    
    def recommend_duration(self, merchant: Dict, score: int, adjustments: Dict) -> int:
        if merchant.get('is_first_time_borrower', False):
            return 6
        elif score >= 75:
            return 18
        elif score >= 60:
            return 12
        else:
            return 6
    
    def recommend_product(self, merchant: Dict, score: int) -> str:
        if merchant.get('is_first_time_borrower', False):
            return "progressive_microloan"
        elif score >= 75:
            return "growth_microloan"
        else:
            return "standard_microloan"
    
    def score_merchant(self, merchant_id: str) -> ScoringResult:
        merchant = data_manager.get_merchant_by_id(merchant_id)
        if merchant is None:
            raise ValueError(f"Merchant {merchant_id} not found")
        
        merchant_dict = merchant.to_dict()
        features = data_manager.get_merchant_features(merchant_id)
        if features is None:
            raise ValueError(f"Features for {merchant_id} not found")
        features_dict = features.to_dict()
        
        proba, score = self.prediction_service.predict(features)
        
        risk_level = self.prediction_service.get_risk_level(score)
        
        confidence = self.calculate_confidence(merchant_dict, features_dict, proba)
        confidence_level = self.prediction_service.get_confidence_level(confidence)
        
        explanation_result = self.explanation_service.explain(features)
        top_factors = explanation_result["top_factors"]
        
        rule_results, adjustments = self.rules_engine.evaluate(
            merchant_dict, score, confidence, proba, features_dict
        )
        
        alerts = [r for r in rule_results if r.severity in ["warning", "error"]]
        
        human_review = adjustments.get("require_human_review", False) or \
                      adjustments.get("no_auto_recommendation", False)
        
        recommended_min, recommended_max = self.recommend_amount(
            merchant_dict, score, adjustments
        )
        recommended_duration = self.recommend_duration(merchant_dict, score, adjustments)
        product_type = self.recommend_product(merchant_dict, score)
        product_info = config.PRODUCT_TYPES.get(product_type, {})
        
        if top_factors:
            top_factor = top_factors[0]
            explanation = f"{top_factor['explanation']} Le score de {score}/100 indique un risque {risk_level['label'].lower()}."
        else:
            explanation = f"Score de {score}/100 basé sur les données disponibles. Risque {risk_level['label'].lower()}."
        
        if adjustments.get("progressive_amount"):
            explanation += " Montant progressif recommandé compte tenu de l'instabilité de l'activité."
        if adjustments.get("request_additional_info"):
            explanation += " Informations complémentaires demandées pour affiner l'évaluation."
        
        return ScoringResult(
            merchant_id=merchant_id,
            score=score,
            proba=proba,
            risk_level=risk_level,
            confidence=confidence,
            confidence_level=confidence_level,
            recommended_amount_min=recommended_min,
            recommended_amount_max=recommended_max,
            recommended_duration_months=recommended_duration,
            product_type=product_type,
            product_info=product_info,
            top_factors=top_factors,
            alerts=alerts,
            human_review_required=human_review,
            explanation=explanation,
            adjustments=adjustments
        )

scoring_engine = ScoringEngine()