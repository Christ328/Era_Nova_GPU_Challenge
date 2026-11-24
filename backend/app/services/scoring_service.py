import logging
from typing import Dict, Any
from app.services.model_service import model_service
from app.services.shap_service import shap_service
from app.services.rules_service import rules_service
from app.schemas import RiskLevel, ConfidenceLevel, ProductType

logger = logging.getLogger(__name__)

RISK_LEVELS = [
    (0, 29, RiskLevel.VERY_HIGH, "#C2414B"),
    (30, 44, RiskLevel.HIGH, "#C47B12"),
    (45, 59, RiskLevel.MODERATE, "#C47B12"),
    (60, 74, RiskLevel.LOW, "#168A62"),
    (75, 100, RiskLevel.VERY_LOW, "#168A62"),
]

CONFIDENCE_LEVELS = [
    (0, 39, ConfidenceLevel.LOW),
    (40, 69, ConfidenceLevel.MEDIUM),
    (70, 100, ConfidenceLevel.HIGH),
]

PRODUCT_TYPES = {
    "progressive_microloan": {"label": "Microcrédit progressif", "min": 50000, "max": 200000, "durations": [3, 6, 9]},
    "standard_microloan": {"label": "Microcrédit standard", "min": 100000, "max": 500000, "durations": [6, 12, 18]},
    "growth_microloan": {"label": "Microcrédit croissance", "min": 200000, "max": 1000000, "durations": [12, 18, 24]},
}

class ScoringService:

    def score(self, features: Dict[str, Any]) -> dict:
        proba = model_service.predict(features)
        score = int(round(proba * 100))
        score = max(0, min(100, score))

        risk_level = self._get_risk_level(score)
        confidence_val = self._get_confidence(features, score)
        confidence_level = self._get_confidence_level(confidence_val)
        data_quality = self._get_data_quality(features)

        alerts, adjustments = rules_service.evaluate(features, score, confidence_val)

        product_type, amount_min, amount_max, duration = self._recommend(
            score, risk_level, adjustments, features
        )

        top_factors = shap_service.explain(features)

        explanation = self._build_explanation(score, risk_level, top_factors)

        human_review = adjustments["require_human_review"] or confidence_val < 0.4

        return {
            "score": score,
            "risk_level": risk_level,
            "confidence": confidence_level,
            "confidence_value": confidence_val,
            "data_quality": data_quality,
            "recommended_amount_min": amount_min,
            "recommended_amount_max": amount_max,
            "recommended_duration_months": duration,
            "product_type": product_type,
            "human_review_required": human_review,
            "top_factors": top_factors,
            "alerts": alerts,
            "explanation": explanation,
            "adjustments": adjustments,
        }

    def _get_risk_level(self, score: int) -> RiskLevel:
        for min_s, max_s, level, _ in RISK_LEVELS:
            if min_s <= score <= max_s:
                return level
        return RiskLevel.MODERATE

    def _get_confidence(self, features: Dict, score: int) -> float:
        anciennete = features.get("anciennete_activite_mois", 0)
        nb_tx = features.get("nb_transactions_mois", 0)
        integrite = features.get("score_integrite", 0.5)

        conf = min(anciennete / 24, 1.0) * 0.3
        conf += min(nb_tx / 50, 1.0) * 0.2
        conf += integrite * 0.3

        if features.get("premiere_fois", 0):
            conf *= 0.7
        if score < 20 or score > 95:
            conf *= 0.8

        return float(max(0, min(1, conf)))

    def _get_data_quality(self, features: Dict) -> float:
        quality = 1.0
        if features.get("premiere_fois", 0):
            quality -= 0.2
        if features.get("anciennete_activite_mois", 0) < 6:
            quality -= 0.3
        if features.get("nb_transactions_mois", 0) < 10:
            quality -= 0.2
        if features.get("score_integrite", 0.5) < 0.3:
            quality -= 0.2
        return float(max(0, min(1, quality)))

    def _get_confidence_level(self, val: float) -> ConfidenceLevel:
        pct = val * 100
        for min_c, max_c, level in CONFIDENCE_LEVELS:
            if min_c <= pct <= max_c:
                return level
        return ConfidenceLevel.MEDIUM

    def _recommend(self, score: int, risk: RiskLevel,
                   adjustments: Dict, features: Dict) -> tuple:
        if adjustments.get("no_auto_recommendation"):
            return ("progressive_microloan", 50000, 100000, 3)

        if score >= 75:
            pt = "growth_microloan"
        elif score >= 45:
            pt = "standard_microloan"
        else:
            pt = "progressive_microloan"

        if adjustments.get("progressive_amount"):
            pt = "progressive_microloan"

        info = PRODUCT_TYPES[pt]
        multiplier = adjustments.get("amount_multiplier", 1.0)

        amount_min = int(info["min"] * multiplier)
        amount_max = int(info["max"] * multiplier)
        duration = info["durations"][0]

        return (pt, amount_min, amount_max, duration)

    def _build_explanation(self, score: int, risk: RiskLevel,
                           factors: list) -> str:
        if not factors:
            return f"Score de {score}/100. Niveau de risque: {risk.value}."

        top = factors[0]
        direction = "améliore" if top["direction"] == "positive" else "réduit"
        return (f"Score de {score}/100 (risque {risk.value.lower()}). "
                f"Le facteur principal ({top['label']}) {direction} le score estimé.")

scoring_service = ScoringService()