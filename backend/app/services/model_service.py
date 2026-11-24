import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import xgboost as xgb
import pandas as pd
import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

class ModelService:
    _instance: Optional["ModelService"] = None
    _model: Optional[xgb.XGBClassifier] = None
    _feature_order: Optional[list] = None
    _metadata: Optional[dict] = None

    @classmethod
    def get_instance(cls) -> "ModelService":
        if cls._instance is None:
            cls._instance = ModelService()
        return cls._instance

    def load(self) -> None:
        if self._model is not None:
            return

        if settings.MODEL_PATH.exists():
            try:
                self._model = xgb.XGBClassifier()
                self._model.load_model(str(settings.MODEL_PATH))
                logger.info("XGBoost model loaded")
            except Exception as e:
                logger.warning(f"Could not load model: {e}")
                self._model = None
        else:
            logger.warning("Model file not found, using mock predictions")
            self._model = None

        if settings.FEATURE_ORDER_PATH.exists():
            with open(settings.FEATURE_ORDER_PATH) as f:
                self._feature_order = json.load(f)
        else:
            self._feature_order = []

        if settings.MODEL_METADATA_PATH.exists():
            with open(settings.MODEL_METADATA_PATH) as f:
                self._metadata = json.load(f)
        else:
            self._metadata = {}

    def predict(self, features: Dict[str, Any]) -> float:
        self.load()

        if self._model is None or not self._feature_order:
            return self._mock_predict(features)

        X = pd.DataFrame([features])
        for col in self._feature_order:
            if col not in X.columns:
                X[col] = 0
        X = X[self._feature_order].fillna(0)
        proba = self._model.predict_proba(X)[0, 1]
        return float(proba)

    def _mock_predict(self, features: Dict[str, Any]) -> float:
        score = 0.5

        revenu = features.get("revenu_mensuel_declare", 0)
        depenses = features.get("depenses_mensuelles", 1)
        if revenu > 0 and depenses > 0:
            ratio = depenses / revenu
            if ratio < 0.3:
                score += 0.25
            elif ratio < 0.5:
                score += 0.15
            elif ratio < 0.7:
                score += 0.05
            elif ratio < 0.9:
                score -= 0.1
            else:
                score -= 0.25

        anciennete = features.get("anciennete_activite_mois", 0)
        if anciennete >= 36:
            score += 0.2
        elif anciennete >= 24:
            score += 0.15
        elif anciennete >= 12:
            score += 0.05
        elif anciennete < 6:
            score -= 0.2
        else:
            score -= 0.1

        solde = features.get("solde_moyen_compte", 0)
        if revenu > 0:
            solde_ratio = solde / revenu
            if solde_ratio > 1.0:
                score += 0.15
            elif solde_ratio > 0.5:
                score += 0.1
            elif solde_ratio < 0.1:
                score -= 0.15

        if features.get("premiere_fois", 0):
            score -= 0.1

        nb_echouees = features.get("nb_transactions_echouees", 0)
        if nb_echouees > 10:
            score -= 0.15
        elif nb_echouees > 5:
            score -= 0.1
        elif nb_echouees == 0:
            score += 0.05

        integrite = features.get("score_integrite", 0.5)
        if integrite > 0.7:
            score += 0.15
        elif integrite > 0.5:
            score += 0.05
        elif integrite < 0.3:
            score -= 0.2

        aptitude = features.get("score_aptitude_entrepreneuriale", 50)
        if aptitude > 70:
            score += 0.1
        elif aptitude < 30:
            score -= 0.1

        tontine = features.get("membre_tontine", 0)
        if tontine:
            score += 0.05

        groupement = features.get("membre_groupement_pro", 0)
        if groupement:
            score += 0.05

        tendance = features.get("tendance_solde_3m", 0)
        if tendance > 0.2:
            score += 0.1
        elif tendance < -0.3:
            score -= 0.1

        montant_demande = features.get("montant_demande", 0)
        if revenu > 0:
            loan_ratio = montant_demande / revenu
            if loan_ratio > 10:
                score -= 0.3
            elif loan_ratio > 5:
                score -= 0.2
            elif loan_ratio > 3:
                score -= 0.1
            elif loan_ratio < 1:
                score += 0.1
            elif loan_ratio < 2:
                score += 0.05

        duree = features.get("duree_credit_mois", 6)
        if duree > 18:
            score -= 0.1
        elif duree > 12:
            score -= 0.05

        garantie = features.get("garantie", 0)
        if garantie > 0.5:
            score += 0.1
        elif garantie < 0.1:
            score -= 0.1

        score += np.random.normal(0, 0.03)
        return float(np.clip(score, 0.02, 0.98))

    def get_feature_names(self) -> list:
        self.load()
        return self._feature_order or []

    def get_metadata(self) -> dict:
        self.load()
        return self._metadata or {}

model_service = ModelService.get_instance()