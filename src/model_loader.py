import xgboost as xgb
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from app.config import config

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    _model = None
    _metadata = None
    _feature_schema = None
    _feature_order = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_model(self) -> xgb.Booster:
        if self._model is None:
            self._model = xgb.Booster()
            self._model.load_model(str(config.MODEL_PATH))
            logger.info("XGBoost model loaded")
        return self._model
    
    def load_metadata(self) -> Dict:
        if self._metadata is None:
            with open(config.MODEL_METADATA_PATH, 'r', encoding='utf-8') as f:
                self._metadata = json.load(f)
        return self._metadata
    
    def load_feature_schema(self) -> Dict:
        if self._feature_schema is None:
            with open(config.FEATURE_SCHEMA_PATH, 'r', encoding='utf-8') as f:
                self._feature_schema = json.load(f)
        return self._feature_schema
    
    def load_feature_order(self) -> List[str]:
        if self._feature_order is None:
            with open(config.FEATURE_ORDER_PATH, 'r', encoding='utf-8') as f:
                self._feature_order = json.load(f)
        return self._feature_order
    
    def get_model_info(self) -> Dict:
        metadata = self.load_metadata()
        return {
            "model_type": "XGBoost",
            "version": metadata.get("version", "1.0"),
            "training_date": metadata.get("training_date", "unknown"),
            "features_count": metadata.get("n_features", "unknown"),
            "best_iteration": metadata.get("best_iteration", "unknown"),
            "train_auc": metadata.get("train_auc", "unknown"),
            "test_auc": metadata.get("test_auc", "unknown"),
            "params": metadata.get("params", {}),
            "gpu_trained": metadata.get("gpu_trained", False),
            "benchmark": metadata.get("benchmark", {})
        }

model_loader = ModelLoader()