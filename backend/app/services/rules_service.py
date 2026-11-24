import json
import logging
from typing import Dict, Any, List, Tuple
from app.config import settings

logger = logging.getLogger(__name__)

class RulesService:
    _rules: List[dict] = []

    @classmethod
    def load(cls) -> List[dict]:
        if cls._rules:
            return cls._rules
        try:
            with open(settings.BUSINESS_RULES_PATH, "r", encoding="utf-8") as f:
                cls._rules = json.load(f)
        except FileNotFoundError:
            cls._rules = cls._default_rules()
        return cls._rules

    @classmethod
    def _default_rules(cls) -> List[dict]:
        return [
            {"name": "primo_emprunteur", "description": "Plafond montant primo-emprunteur",
             "condition": "is_first_time_borrower", "action": "limit_amount",
             "severity": "warning", "multiplier": 0.7},
            {"name": "short_history", "description": "Historique court - revue humaine",
             "condition": "activity_age_months < 6", "action": "require_human_review",
             "severity": "warning"},
            {"name": "incomplete_data", "description": "Données incomplètes",
             "condition": "data_completeness < 0.7", "action": "no_auto_recommendation",
             "severity": "error"},
            {"name": "undocumented_expenses", "description": "Dépenses non documentées",
             "condition": "expense_documentation_ratio < 0.3", "action": "reduce_amount",
             "severity": "warning", "multiplier": 0.8},
            {"name": "inconsistencies", "description": "Incohérences détectées",
             "condition": "has_inconsistencies", "action": "require_human_review",
             "severity": "error"},
            {"name": "low_confidence", "description": "Confiance faible",
             "condition": "confidence < 0.5", "action": "request_additional_info",
             "severity": "warning"},
            {"name": "unstable_activity", "description": "Activité irrégulière",
             "condition": "regularity_score < 0.3", "action": "progressive_amount",
             "severity": "info"},
            {"name": "high_score_low_margin", "description": "CA élevé mais marge faible",
             "condition": "margin_ratio < 0.05 and monthly_income_mean > 500000",
             "action": "limit_amount", "severity": "warning", "multiplier": 0.6},
        ]

    def evaluate(self, features: Dict[str, Any], score: int,
                 confidence: float) -> Tuple[List[dict], Dict[str, Any]]:
        rules = self.load()
        alerts = []
        adjustments = {
            "amount_multiplier": 1.0,
            "require_human_review": False,
            "no_auto_recommendation": False,
            "progressive_amount": False,
            "request_additional_info": False,
            "review_reasons": [],
        }

        for rule in rules:
            triggered = self._check_condition(rule["condition"], features, score, confidence)
            if not triggered:
                continue

            alerts.append({
                "severity": rule["severity"],
                "message": rule["description"],
                "rule_name": rule["name"],
            })

            action = rule["action"]
            if action == "limit_amount":
                adjustments["amount_multiplier"] *= rule.get("multiplier", 0.7)
            elif action == "reduce_amount":
                adjustments["amount_multiplier"] *= rule.get("multiplier", 0.8)
            elif action == "require_human_review":
                adjustments["require_human_review"] = True
                adjustments["review_reasons"].append(rule["name"])
            elif action == "no_auto_recommendation":
                adjustments["no_auto_recommendation"] = True
                adjustments["require_human_review"] = True
                adjustments["review_reasons"].append(rule["name"])
            elif action == "progressive_amount":
                adjustments["progressive_amount"] = True
            elif action == "request_additional_info":
                adjustments["request_additional_info"] = True

        return alerts, adjustments

    def _check_condition(self, condition: str, features: Dict,
                         score: int, confidence: float) -> bool:
        try:
            local_vars = {**features, "score": score, "confidence": confidence}
            return bool(eval(condition, {"__builtins__": {}}, local_vars))
        except Exception:
            return False

rules_service = RulesService()