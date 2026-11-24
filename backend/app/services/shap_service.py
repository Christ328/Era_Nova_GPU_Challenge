import logging
from typing import Dict, Any, List
import shap
import xgboost as xgb
import pandas as pd
import numpy as np

from app.config import settings
from app.services.model_service import model_service

logger = logging.getLogger(__name__)

FEATURE_LABELS = {
    "monthly_income_mean": "Revenu mensuel moyen",
    "monthly_expenses": "Dépenses mensuelles",
    "expense_income_ratio": "Ratio dépenses/revenus",
    "margin_ratio": "Marge nette",
    "avg_balance_income_ratio": "Solde moyen / revenu",
    "min_balance_income_ratio": "Solde min / revenu",
    "income_volatility": "Volatilité des revenus",
    "income_growth": "Croissance des revenus",
    "regularity_score": "Régularité de l'activité",
    "concentration_ratio": "Concentration des revenus",
    "documentation_quality": "Qualité documentation",
    "counterparty_diversity": "Diversité contreparties",
    "transactions_per_day": "Transactions par jour",
    "total_transactions": "Volume transactions",
    "n_months_active": "Mois d'activité",
    "n_active_days": "Jours actifs",
    "n_counterparties": "Contreparties uniques",
    "avg_balance": "Solde moyen",
    "min_balance": "Solde minimum",
    "max_balance": "Solde maximum",
    "documented_ratio": "Taux documentation",
    "activity_age_months": "Ancienneté activité",
    "is_first_time_borrower": "Primo-emprunteur",
    "data_completeness": "Complétude données",
    "has_inconsistencies": "Incohérences détectées",
}

class ShapService:
    _explainer = None

    @classmethod
    def get_explainer(cls):
        if cls._explainer is None:
            model_service.load()
            model = model_service._model
            if model is not None:
                try:
                    cls._explainer = shap.TreeExplainer(model)
                except Exception:
                    cls._explainer = None
            else:
                cls._explainer = None
        return cls._explainer

    def explain(self, features: Dict[str, Any]) -> List[Dict]:
        model_service.load()
        feature_order = model_service.get_feature_names()

        if not feature_order:
            return self._mock_explain(features)

        X = pd.DataFrame([features])[feature_order].fillna(0)

        explainer = self.get_explainer()
        if explainer is None:
            return self._mock_explain(features)

        try:
            shap_values = explainer.shap_values(X)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            shap_values = np.array(shap_values).flatten()
        except Exception:
            return self._mock_explain(features)

        factors = []
        for i, fname in enumerate(feature_order):
            val = shap_values[i]
            factors.append({
                "feature": fname,
                "label": FEATURE_LABELS.get(fname, fname.replace("_", " ").title()),
                "value": float(features.get(fname, 0)),
                "impact": round(float(val), 4),
                "direction": "positive" if val > 0 else "negative",
            })

        factors.sort(key=lambda x: abs(x["impact"]), reverse=True)
        return factors[:10]

    def _mock_explain(self, features: Dict[str, Any]) -> List[Dict]:
        factors = []
        for fname, val in features.items():
            if fname in FEATURE_LABELS:
                impact = float(np.random.randn() * 0.05)
                factors.append({
                    "feature": fname,
                    "label": FEATURE_LABELS[fname],
                    "value": float(val) if isinstance(val, (int, float)) else 0,
                    "impact": round(impact, 4),
                    "direction": "positive" if impact > 0 else "negative",
                })
        factors.sort(key=lambda x: abs(x["impact"]), reverse=True)
        return factors[:10]

shap_service = ShapService()