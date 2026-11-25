import logging
from typing import Dict, Any
from app.services.model_service import model_service
from app.services.shap_service import shap_service
from app.services.rules_service import rules_service
from app.schemas import RiskLevel, ConfidenceLevel

logger = logging.getLogger(__name__)

RISK_LEVELS = [
    (0, 299, RiskLevel.VERY_HIGH, "#C2414B"),
    (300, 449, RiskLevel.HIGH, "#C47B12"),
    (450, 599, RiskLevel.MODERATE, "#C47B12"),
    (600, 749, RiskLevel.LOW, "#168A62"),
    (750, 1000, RiskLevel.VERY_LOW, "#168A62"),
]

CONFIDENCE_LEVELS = [
    (0, 39, ConfidenceLevel.LOW),
    (40, 69, ConfidenceLevel.MEDIUM),
    (70, 100, ConfidenceLevel.HIGH),
]

MAX_LOAN_AMOUNT = 300000
SCORE_THRESHOLD = 700


class ScoringService:

    def score(self, features: Dict[str, Any]) -> dict:
        requested_amount = features.get("montant_demande", 0)

        if requested_amount > MAX_LOAN_AMOUNT:
            features = {**features, "montant_demande": MAX_LOAN_AMOUNT}
            requested_amount = MAX_LOAN_AMOUNT

        proba = model_service.predict(features)
        ml_score = int(round((1 - proba) * 1000))
        ml_score = max(0, min(1000, ml_score))

        # rules_service.compute_business_score returns 0-100; scale to 1000
        business_score_val = rules_service.compute_business_score(features)
        business_score = int(round(business_score_val * 10))
        business_score = max(0, min(1000, business_score))

        data_quality = self._get_data_quality(features)

        # Dynamic weighting:
        # - Low data quality → trust rules more (0.35/0.65)
        # - ML score looks anomalous (very low despite decent rules) → trust rules more
        # - Normal → balanced (0.55/0.45)
        ml_anomalous = ml_score < 200 and business_score > 400
        if data_quality < 0.5 or ml_anomalous:
            alpha, beta = 0.35, 0.65
        else:
            alpha, beta = 0.55, 0.45

        score = int(round(alpha * ml_score + beta * business_score))
        score = max(0, min(1000, score))

        alerts, adjustments = rules_service.evaluate(features, score, 0.5)
        score = self._apply_score_caps(score, features, adjustments)

        amount, score, iterated = self._iterate_amount(features, score, requested_amount)

        if iterated:
            if score >= SCORE_THRESHOLD:
                alerts.append({
                    "severity": "info",
                    "message": f"Montant adapté à {amount:,.0f} FCFA (score {score}/1000 ≥ seuil {SCORE_THRESHOLD})",
                    "rule_name": "amount_adjustment"
                })
            else:
                alerts.append({
                    "severity": "warning",
                    "message": f"Aucun montant ≤ {MAX_LOAN_AMOUNT:,} FCFA n'atteint le seuil de {SCORE_THRESHOLD}. Meilleur score obtenu : {score}/1000 pour {amount:,.0f} FCFA.",
                    "rule_name": "amount_adjustment"
                })

        risk_level = self._get_risk_level(score)
        confidence_val = self._get_confidence(features, score)
        confidence_level = self._get_confidence_level(confidence_val)

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

        # Walk down from requested amount to 5 000 FCFA in 5 000-FCFA steps.
        # Return the first amount where score >= SCORE_THRESHOLD.
        # If none qualifies, return the amount that produced the highest score.
        best_score = initial_score
        best_amount = requested

        # data_quality depends only on fields that do not change as montant_demande decrements
        dq = self._get_data_quality(features)
        a, b = (0.35, 0.65) if dq < 0.5 else (0.55, 0.45)

        for amount in range(requested - 5000, 4999, -5000):
            test_features = {**features, "montant_demande": amount}
            proba = model_service.predict(test_features)
            ml_s = int(round((1 - proba) * 1000))
            ml_s = max(0, min(1000, ml_s))
            biz_s = int(round(rules_service.compute_business_score(test_features) * 10))
            biz_s = max(0, min(1000, biz_s))
            score = int(round(a * ml_s + b * biz_s))
            score = max(0, min(1000, score))
            if score >= SCORE_THRESHOLD:
                return (amount, score, True)
            if score > best_score:
                best_score = score
                best_amount = amount

        return (best_amount, best_score, True)

    def _apply_score_caps(self, score: int, features: Dict, adjustments: Dict) -> int:
        revenu = features.get("revenu_mensuel_declare", 0)
        montant = features.get("montant_demande", 0)

        if revenu > 0 and montant > 0:
            ratio = montant / revenu
            if ratio > 50:
                score = min(score, 100)
            elif ratio > 20:
                score = min(score, 200)
            elif ratio > 10:
                score = min(score, 300)
            elif ratio > 5:
                score = min(score, 450)

        if adjustments.get("no_auto_recommendation"):
            score = min(score, 250)
        if adjustments.get("require_human_review") and score > 500:
            score = 500

        return max(0, min(1000, score))

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
        if score < 200 or score > 950:
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

    def _build_explanation(self, score: int, risk: RiskLevel,
                           factors: list) -> str:
        if not factors:
            return f"Score de {score}/1000. Niveau de risque: {risk.value}."

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
        return (f"Score de {score}/1000 (risque {risk.value.lower()}). "
                + (f"{detail.capitalize()}." if detail else ""))

    def generate_counter_proposals(self, features: dict, imf_config) -> list:
        """Generate up to 3 counter-proposals when the score is below auto-accept threshold."""
        montant = features.get("montant_demande", 0)
        duree = features.get("duree_credit_mois", 12)
        revenu = max(features.get("revenu_mensuel_declare", 1), 1)
        depenses = features.get("depenses_mensuelles", 0)
        net_income = max(revenu - depenses, 1)

        scenarios = [
            ("M-10%",       int(montant * 0.9), duree),
            ("M-20%",       int(montant * 0.8), duree),
            ("M + n+3",     montant,            duree + 3),
            ("M + n+6",     montant,            duree + 6),
            ("M-10% + n+3", int(montant * 0.9), duree + 3),
            ("M + garantie", montant,           duree),
        ]

        results = []
        for label, amount, duration in scenarios:
            if amount <= 0 or duration <= 0:
                continue
            test_features = {**features, "montant_demande": amount, "duree_credit_mois": duration}
            if label == "M + garantie":
                test_features["garantie"] = 1
            try:
                result = self.score(test_features)
            except Exception:
                continue

            scenario_score = result["score"]
            if scenario_score < imf_config.auto_accept_score:
                continue

            monthly_payment = amount / max(duration, 1)
            effort_rate = monthly_payment / net_income

            results.append({
                "amount": amount,
                "duration": duration,
                "score": scenario_score,
                "effort_rate": round(effort_rate, 4),
                "label": label,
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:3]


scoring_service = ScoringService()
