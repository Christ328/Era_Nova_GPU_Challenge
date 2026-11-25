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
    "standard_microloan": {"label": "Microcrédit standard", "min": 100000, "max": 300000, "durations": [6, 12, 18]},
    "growth_microloan": {"label": "Microcrédit croissance", "min": 200000, "max": 300000, "durations": [12, 18, 24]},
}

MAX_LOAN_AMOUNT = 300000
SCORE_THRESHOLD = 70

class ScoringService:

    def score(self, features: Dict[str, Any]) -> dict:
        requested_amount = features.get("montant_demande", 0)

        if requested_amount > MAX_LOAN_AMOUNT:
            features = {**features, "montant_demande": MAX_LOAN_AMOUNT}
            requested_amount = MAX_LOAN_AMOUNT

        proba = model_service.predict(features)
        ml_score = int(round((1 - proba) * 100))
        ml_score = max(0, min(100, ml_score))

        business_score_val = rules_service.compute_business_score(features)
        business_score = int(round(business_score_val))

        data_quality = self._get_data_quality(features)

        # Dynamic weighting: trust rules more when data quality is low
        if data_quality < 0.5:
            alpha, beta = 0.35, 0.65
        else:
            alpha, beta = 0.55, 0.45

        score = int(round(alpha * ml_score + beta * business_score))
        score = max(0, min(100, score))

        alerts, adjustments = rules_service.evaluate(features, score, 0.5)
        score = self._apply_score_caps(score, features, adjustments)

        amount, score, iterated = self._iterate_amount(features, score, requested_amount)

        if iterated:
            if score >= SCORE_THRESHOLD:
                alerts.append({
                    "severity": "info",
                    "message": f"Montant adapté à {amount:,.0f} FCFA (score {score}/100 ≥ seuil {SCORE_THRESHOLD})",
                    "rule_name": "amount_adjustment"
                })
            else:
                alerts.append({
                    "severity": "warning",
                    "message": f"Aucun montant ≤ {MAX_LOAN_AMOUNT:,} FCFA n'atteint le seuil de {SCORE_THRESHOLD}. Meilleur score obtenu : {score}/100 pour {amount:,.0f} FCFA.",
                    "rule_name": "amount_adjustment"
                })

        risk_level = self._get_risk_level(score)
        confidence_val = self._get_confidence(features, score)
        confidence_level = self._get_confidence_level(confidence_val)
        # data_quality already computed above for weighting

        product_type, amount_min, amount_max, duration = self._recommend(
            score, risk_level, adjustments, features
        )

        top_factors = shap_service.explain(features)
        explanation = self._build_explanation(score, risk_level, top_factors)

        human_review = adjustments["require_human_review"] or confidence_val < 0.4

        return {
            "score": score,
            "ml_score": ml_score,
            "business_score": business_score,
            "score_weights": {"ml": alpha, "rules": beta},
            "risk_level": risk_level,
            "confidence": confidence_level,
            "confidence_value": confidence_val,
            "data_quality": data_quality,
            "recommended_amount_min": amount_min,
            "recommended_amount_max": min(amount_max, MAX_LOAN_AMOUNT),
            "recommended_duration_months": duration,
            "product_type": product_type,
            "human_review_required": human_review,
            "top_factors": top_factors,
            "alerts": alerts,
            "explanation": explanation,
            "adjustments": adjustments,
        }

    def _iterate_amount(self, features: Dict, initial_score: int, requested: int) -> tuple:
        # Score already acceptable for the requested amount — no adjustment needed
        if initial_score >= SCORE_THRESHOLD:
            return (requested, initial_score, False)

        if requested <= 5000:
            return (requested, initial_score, False)

        # Walk down from requested amount to 50 000 FCFA in 10 000-FCFA steps.
        # Return the first amount where score >= SCORE_THRESHOLD.
        # If none qualifies, return the amount that produced the highest score.
        best_score = initial_score
        best_amount = requested

        for amount in range(requested - 5000, 4999, -5000):
            test_features = {**features, "montant_demande": amount}
            proba = model_service.predict(test_features)
            ml_s = int(round((1 - proba) * 100))
            biz_s = int(round(rules_service.compute_business_score(test_features)))
            dq = self._get_data_quality(test_features)
            a, b = (0.35, 0.65) if dq < 0.5 else (0.55, 0.45)
            score = int(round(a * ml_s + b * biz_s))
            score = max(0, min(100, score))
            if score >= SCORE_THRESHOLD:
                return (amount, score, True)
            if score > best_score:
                best_score = score
                best_amount = amount

        # No amount cleared the threshold — return best found (never force score to 0)
        return (best_amount, best_score, True)

    def _apply_score_caps(self, score: int, features: Dict, adjustments: Dict) -> int:
        revenu = features.get("revenu_mensuel_declare", 0)
        montant = features.get("montant_demande", 0)

        if revenu > 0 and montant > 0:
            ratio = montant / revenu
            if ratio > 50:
                score = min(score, 10)
            elif ratio > 20:
                score = min(score, 20)
            elif ratio > 10:
                score = min(score, 30)
            elif ratio > 5:
                score = min(score, 45)

        if adjustments.get("no_auto_recommendation"):
            score = min(score, 25)
        if adjustments.get("require_human_review") and score > 50:
            score = 50

        return max(0, min(100, score))

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

        # Split top factors into positives and negatives
        positives = [f for f in factors[:6] if f["direction"] == "positive"]
        negatives = [f for f in factors[:6] if f["direction"] == "negative"]

        parts = []
        if positives:
            labels = ", ".join(f["label"] for f in positives[:3])
            parts.append(f"les facteurs favorables sont : {labels}")
        if negatives:
            labels = ", ".join(f["label"] for f in negatives[:3])
            parts.append(f"les facteurs pénalisants sont : {labels}")

        detail = " ; ".join(parts) if parts else ""
        return (f"Score de {score}/100 (risque {risk.value.lower()}). "
                + (f"{detail.capitalize()}." if detail else ""))

scoring_service = ScoringService()