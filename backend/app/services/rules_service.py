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
            {"name": "premiere_fois", "description": "Première demande - plafond réduit",
             "condition": "premiere_fois == 1", "action": "limit_amount",
             "severity": "warning", "multiplier": 0.7},
            {"name": "short_history", "description": "Activité récente (< 6 mois) - revue humaine",
             "condition": "anciennete_activite_mois < 6", "action": "require_human_review",
             "severity": "warning"},
            {"name": "high_expense_ratio", "description": "Dépenses élevées vs revenus",
             "condition": "depenses_mensuelles / (revenu_mensuel_declare + 1) > 0.8",
             "action": "reduce_amount", "severity": "warning", "multiplier": 0.8},
            {"name": "failed_transactions", "description": "Transactions échouées nombreuses",
             "condition": "nb_transactions_echouees > 5", "action": "require_human_review",
             "severity": "warning"},
            {"name": "low_integrity", "description": "Score d'intégrité faible",
             "condition": "score_integrite < 0.3", "action": "require_human_review",
             "severity": "error"},
            {"name": "no_tontine", "description": "Pas de tontine - historique limité",
             "condition": "membre_tontine == 0 and anciennete_activite_mois < 12",
             "action": "progressive_amount", "severity": "info"},
            {"name": "high_loan_amount", "description": "Montant demandé élevé vs revenu",
             "condition": "montant_demande / (revenu_mensuel_declare + 1) > 5",
             "action": "limit_amount", "severity": "warning", "multiplier": 0.6},
            {"name": "unstable_balance", "description": "Solde instable ou négatif",
             "condition": "solde_moyen_compte < 0 or tendance_solde_3m < -0.5",
             "action": "reduce_amount", "severity": "warning", "multiplier": 0.7},
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