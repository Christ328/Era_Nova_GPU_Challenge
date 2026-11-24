from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

from app.config import config
from app.database import data_manager

logger = logging.getLogger(__name__)

class ReviewReason(Enum):
    PRIMO_EMPRUNTEUR = "primo_emprunteur"
    SHORT_HISTORY = "historique_court"
    INCOMPLETE_DATA = "donnees_incompletes"
    UNDOCUMENTED_EXPENSES = "depenses_non_documentees"
    INCONSISTENCIES = "incoherences_detectees"
    LOW_CONFIDENCE = "confiance_faible"
    UNSTABLE_ACTIVITY = "activite_instable"
    HIGH_SCORE_LOW_MARGIN = "score_eleve_marge_faible"
    MANUAL_REVIEW_REQUIRED = "revue_manuelle_requise"

@dataclass
class BusinessRule:
    name: str
    description: str
    condition: str
    action: str
    severity: str
    review_reason: Optional[ReviewReason] = None

@dataclass
class RuleResult:
    rule_name: str
    triggered: bool
    message: str
    severity: str
    review_reason: Optional[ReviewReason] = None

class RulesEngine:
    def __init__(self):
        self.rules = self._load_rules()
    
    def _load_rules(self) -> List[BusinessRule]:
        try:
            with open(config.BUSINESS_RULES_PATH, 'r', encoding='utf-8') as f:
                rules_data = json.load(f)
            rules = []
            for r in rules_data:
                rule = BusinessRule(**r)
                # Convert review_reason string to enum if needed
                if rule.review_reason and isinstance(rule.review_reason, str):
                    try:
                        rule.review_reason = ReviewReason(rule.review_reason)
                    except ValueError:
                        rule.review_reason = None
                rules.append(rule)
            return rules
        except FileNotFoundError:
            logger.warning("Business rules file not found, using defaults")
            return self._default_rules()
    
    def _default_rules(self) -> List[BusinessRule]:
        return [
            BusinessRule(
                name="primo_emprunteur_plafond",
                description="Plafond de montant pour primo-emprunteur",
                condition="merchant.get('is_first_time_borrower', False)",
                action="limit_amount",
                severity="warning",
                review_reason=ReviewReason.PRIMO_EMPRUNTEUR
            ),
            BusinessRule(
                name="short_history_review",
                description="Revue humaine pour historique court (< 6 mois)",
                condition="merchant.get('activity_age_months', 0) < 6",
                action="require_human_review",
                severity="warning",
                review_reason=ReviewReason.SHORT_HISTORY
            ),
            BusinessRule(
                name="incomplete_data",
                description="Données incomplètes - pas de recommandation auto",
                condition="merchant.get('data_completeness', 1.0) < 0.7",
                action="no_auto_recommendation",
                severity="error",
                review_reason=ReviewReason.INCOMPLETE_DATA
            ),
            BusinessRule(
                name="undocumented_expenses",
                description="Dépenses non documentées - réduire montant",
                condition="merchant.get('expense_documentation_ratio', 1.0) < 0.5",
                action="reduce_amount",
                severity="warning",
                review_reason=ReviewReason.UN_DOCUMENTED_EXPENSES
            ),
            BusinessRule(
                name="inconsistencies",
                description="Incohérences détectées - revue manuelle",
                condition="merchant.get('has_inconsistencies', False)",
                action="require_human_review",
                severity="error",
                review_reason=ReviewReason.INCONSISTENCIES
            ),
            BusinessRule(
                name="low_confidence",
                description="Confiance faible - informations complémentaires",
                condition="confidence < 40",
                action="request_additional_info",
                severity="warning",
                review_reason=ReviewReason.LOW_CONFIDENCE
            ),
            BusinessRule(
                name="unstable_activity",
                description="Activité instable - montant progressif",
                condition="merchant.get('income_volatility', 0) > 0.5",
                action="progressive_amount",
                severity="warning",
                review_reason=ReviewReason.UNSTABLE_ACTIVITY
            ),
            BusinessRule(
                name="high_score_low_margin",
                description="Score élevé mais marge faible - limiter recommandation",
                condition="score >= 75 and merchant.get('margin_ratio', 1.0) < 0.15",
                action="limit_amount",
                severity="warning",
                review_reason=ReviewReason.HIGH_SCORE_LOW_MARGIN
            )
        ]
    
    def evaluate(self, merchant: Dict, score: int, confidence: float, 
                 proba: float, features: Dict) -> Tuple[List[RuleResult], Dict]:
        results = []
        adjustments = {
            "amount_multiplier": 1.0,
            "require_human_review": False,
            "no_auto_recommendation": False,
            "progressive_amount": False,
            "request_additional_info": False,
            "review_reasons": []
        }
        
        for rule in self.rules:
            try:
                context = {
                    "merchant": merchant,
                    "score": score,
                    "confidence": confidence,
                    "proba": proba,
                    "features": features
                }
                triggered = eval(rule.condition, {"__builtins__": {}}, context)
            except Exception as e:
                logger.warning(f"Rule {rule.name} evaluation failed: {e}")
                triggered = False
            
            if triggered:
                results.append(RuleResult(
                    rule_name=rule.name,
                    triggered=True,
                    message=rule.description,
                    severity=rule.severity,
                    review_reason=rule.review_reason
                ))
                
                if rule.action == "limit_amount":
                    adjustments["amount_multiplier"] *= 0.7
                elif rule.action == "reduce_amount":
                    adjustments["amount_multiplier"] *= 0.8
                elif rule.action == "require_human_review":
                    adjustments["require_human_review"] = True
                    if rule.review_reason:
                        adjustments["review_reasons"].append(rule.review_reason.value)
                elif rule.action == "no_auto_recommendation":
                    adjustments["no_auto_recommendation"] = True
                elif rule.action == "progressive_amount":
                    adjustments["progressive_amount"] = True
                elif rule.action == "request_additional_info":
                    adjustments["request_additional_info"] = True
        
        return results, adjustments

rules_engine = RulesEngine()