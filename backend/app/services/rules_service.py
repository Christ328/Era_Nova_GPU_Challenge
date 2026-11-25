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

    def compute_business_score(self, features: Dict[str, Any]) -> float:
        revenu = features.get('revenu_mensuel_declare', 0)
        depenses = features.get('depenses_mensuelles', 0)
        solde = features.get('solde_moyen_compte', 0)
        membre_tontine = int(features.get('membre_tontine', 0))
        regularite_tontine = features.get('regularite_cotisations_tontine', 0)
        anciennete_tontine = features.get('anciennete_tontine_mois', 0)
        deja_beneficiaire = int(features.get('deja_beneficiaire_tour', 0))
        volume_depots = features.get('volume_depots_moyen', 0)
        volume_retraits = features.get('volume_retraits_moyen', 0)
        nb_transactions = features.get('nb_transactions_mois', 1)
        nb_echouees = features.get('nb_transactions_echouees', 0)
        montant_demande = features.get('montant_demande', 0)
        duree = max(features.get('duree_credit_mois', 1), 1)
        garantie = features.get('garantie', 0)
        premiere_fois = int(features.get('premiere_fois', 0))
        anciennete = features.get('anciennete_activite_mois', 0)
        regularite_cotisations = features.get('regularite_cotisations_tontine', 0)
        tendance = features.get('tendance_solde_3m', 0)
        membre_groupement = int(features.get('membre_groupement_pro', 0))
        jour_marche = int(features.get('indicateur_jour_marche', 0))

        raw = 0

        # R1 — Survival ratio
        if solde > 2 * depenses:
            raw += 12
        elif solde > depenses:
            raw += 6
        elif depenses > 0 and solde < 0.5 * depenses:
            raw -= 15
        else:
            raw -= 5

        # R3 — Deposit/withdrawal conversion rate
        ratio_dw = volume_retraits / max(volume_depots, 1)
        if ratio_dw > 1.1:
            raw -= 20
        elif ratio_dw < 0.6:
            raw += 10
        else:
            raw += 3

        # R5 — Composite tontine score
        if membre_tontine:
            tontine_score = (regularite_tontine * 0.5
                             + min(anciennete_tontine / 60.0, 1.0) * 0.3
                             + deja_beneficiaire * 0.2)
            raw += tontine_score * 20

        # R10 — Revenue coherence with mobile flows
        flux_total = volume_depots + volume_retraits
        coherence = flux_total / max(revenu * 2, 1)
        if 0.5 <= coherence <= 2.0:
            raw += 12
        elif coherence < 0.2:
            raw -= 8
        else:
            raw += 4

        # R11 — Transaction failure rate
        tx_rate = nb_echouees / max(nb_transactions, 1)
        if tx_rate < 0.03:
            raw += 5
        elif tx_rate < 0.08:
            pass  # 0 pts
        elif tx_rate < 0.15:
            raw -= 10
        else:
            raw -= 20

        # R13 — Monthly repayment burden
        mensualite = (montant_demande / duree) * 1.1
        surplus = revenu - depenses
        if surplus <= 0:
            raw -= 15
        else:
            burden = mensualite / surplus
            if burden < 0.2:
                raw += 10
            elif burden < 0.4:
                raw += 3
            elif burden < 0.6:
                raw -= 8
            else:
                raw -= 15

        # R14 — Real guarantee leverage
        real_guarantee = garantie * solde
        leverage = real_guarantee / max(montant_demande, 1)
        if leverage > 0.5:
            raw += 12
        elif leverage > 0.25:
            raw += 6

        # R16 — First loan paradox
        if premiere_fois:
            if anciennete >= 24 and regularite_cotisations >= 0.8:
                raw += 5
            elif anciennete < 6:
                raw -= 10
            else:
                raw -= 3

        # R18 — Balance momentum
        if tendance > 0.15:
            raw += 10
        elif tendance > 0:
            raw += 3
        elif tendance > -0.1:
            raw -= 5
        else:
            raw -= 15

        # R8 — Professional integration
        if membre_groupement and jour_marche:
            raw += 8
        elif membre_groupement or jour_marche:
            raw += 3

        # Normalize to 0-100
        RAW_MIN = -88
        RAW_MAX = 104
        business_score = (raw - RAW_MIN) / (RAW_MAX - RAW_MIN) * 100
        return float(max(0.0, min(100.0, business_score)))


rules_service = RulesService()