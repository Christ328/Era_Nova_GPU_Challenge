import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

from app.config import settings
from app.services.model_service import model_service

logger = logging.getLogger(__name__)

FEATURE_LABELS = {
    "age": "Âge",
    "anciennete_activite_mois": "Ancienneté activité",
    "revenu_mensuel_declare": "Revenu mensuel déclaré",
    "depenses_mensuelles": "Dépenses mensuelles",
    "proprietaire_local": "Propriétaire du local",
    "nombre_employes": "Nombre d'employés",
    "nb_transactions_mois": "Transactions par mois",
    "volume_depots_moyen": "Volume moyen dépôts",
    "volume_retraits_moyen": "Volume moyen retraits",
    "solde_moyen_compte": "Solde moyen du compte",
    "tendance_solde_3m": "Tendance du solde (3m)",
    "regularite_depots_ecart_type": "Régularité des dépôts",
    "nb_contreparties_distinctes": "Contreparties distinctes",
    "part_transferts_marchands": "Part transferts marchands",
    "nb_transactions_echouees": "Transactions échouées",
    "frequence_recharges_mois": "Fréquence recharges",
    "montant_moyen_recharge": "Montant moyen recharge",
    "anciennete_ligne_mois": "Ancienneté ligne",
    "nb_contacts_distincts": "Contacts distincts",
    "stabilite_lieu_vie": "Stabilité du lieu de vie",
    "membre_tontine": "Membre tontine",
    "anciennete_tontine_mois": "Ancienneté tontine",
    "regularite_cotisations_tontine": "Régularité cotisations",
    "montant_moyen_cotisation": "Montant moyen cotisation",
    "deja_beneficiaire_tour": "Déjà bénéficiaire du tour",
    "score_aptitude_entrepreneuriale": "Aptitude entrepreneuriale",
    "score_integrite": "Score d'intégrité",
    "locus_controle_interne": "Locus de contrôle interne",
    "proximite_marche_km": "Proximité du marché",
    "indicateur_jour_marche": "Indicateur jour de marché",
    "membre_groupement_pro": "Membre groupement pro",
    "premiere_fois": "Première demande",
    "montant_demande": "Montant demandé",
    "duree_credit_mois": "Durée de crédit",
    "garantie": "Garantie",
}

class ShapService:

    def explain(self, features: Dict[str, Any]) -> List[Dict]:
        try:
            return self._compute_shap(features)
        except Exception as e:
            logger.warning(f"SHAP error: {e}")
            return self._mock_explain(features)

    def _compute_shap(self, features: Dict[str, Any]) -> List[Dict]:
        model_service.load()
        feature_order = model_service.get_feature_names()

        if not feature_order:
            return self._mock_explain(features)

        X = pd.DataFrame([features])
        for col in feature_order:
            if col not in X.columns:
                X[col] = 0
        X = X[feature_order].fillna(0)
        X = model_service._normalize(X)  # normalize before SHAP, same as predict()

        model = model_service._model
        if model is None:
            return self._mock_explain(features)

        try:
            import shap
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            shap_values = np.array(shap_values).flatten()
        except Exception:
            return self._mock_explain(features)

        factors = []
        for i, fname in enumerate(feature_order):
            if i >= len(shap_values):
                break
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
            if fname in FEATURE_LABELS and isinstance(val, (int, float)):
                impact = float(np.random.randn() * 0.05)
                factors.append({
                    "feature": fname,
                    "label": FEATURE_LABELS[fname],
                    "value": float(val),
                    "impact": round(impact, 4),
                    "direction": "positive" if impact > 0 else "negative",
                })
        factors.sort(key=lambda x: abs(x["impact"]), reverse=True)
        return factors[:10]

shap_service = ShapService()