import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import json
import logging

from app.config import config

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self):
        self._merchants: Optional[pd.DataFrame] = None
        self._transactions: Optional[pd.DataFrame] = None
        self._labels: Optional[pd.DataFrame] = None
        self._features: Optional[pd.DataFrame] = None
        self._test_profiles: Optional[pd.DataFrame] = None
        self._data_dictionary: Optional[pd.DataFrame] = None
        self._feature_labels: Optional[Dict] = None
        self._explanation_templates: Optional[Dict] = None
        self._expected_shap: Optional[Dict] = None
    
    def load_merchants(self) -> pd.DataFrame:
        if self._merchants is None:
            self._merchants = pd.read_csv(config.MERCHANTS_CSV)
            logger.info(f"Loaded {len(self._merchants)} merchants")
        return self._merchants
    
    def load_transactions(self) -> pd.DataFrame:
        if self._transactions is None:
            self._transactions = pd.read_csv(config.TRANSACTIONS_CSV)
            if 'date' in self._transactions.columns:
                self._transactions['date'] = pd.to_datetime(self._transactions['date'])
            logger.info(f"Loaded {len(self._transactions)} transactions")
        return self._transactions
    
    def load_labels(self) -> pd.DataFrame:
        if self._labels is None:
            self._labels = pd.read_csv(config.LABELS_CSV)
            logger.info(f"Loaded {len(self._labels)} labels")
        return self._labels
    
    def load_features(self) -> pd.DataFrame:
        if self._features is None:
            self._features = pd.read_csv(config.FEATURES_CSV)
            logger.info(f"Loaded features for {len(self._features)} merchants")
        return self._features
    
    def load_test_profiles(self) -> pd.DataFrame:
        if self._test_profiles is None:
            self._test_profiles = pd.read_csv(config.TEST_PROFILES_CSV)
            logger.info(f"Loaded {len(self._test_profiles)} test profiles")
        return self._test_profiles
    
    def load_data_dictionary(self) -> pd.DataFrame:
        if self._data_dictionary is None:
            self._data_dictionary = pd.read_csv(config.DATA_DICTIONARY_CSV)
            logger.info(f"Loaded data dictionary with {len(self._data_dictionary)} entries")
        return self._data_dictionary
    
    def load_feature_labels(self) -> Dict:
        if self._feature_labels is None:
            with open(config.FEATURE_LABELS_PATH, 'r', encoding='utf-8') as f:
                self._feature_labels = json.load(f)
        return self._feature_labels
    
    def load_explanation_templates(self) -> Dict:
        if self._explanation_templates is None:
            with open(config.EXPLANATION_TEMPLATES_PATH, 'r', encoding='utf-8') as f:
                self._explanation_templates = json.load(f)
        return self._explanation_templates
    
    def load_expected_shap(self) -> Dict:
        if self._expected_shap is None:
            with open(config.EXPECTED_SHAP_PATH, 'r', encoding='utf-8') as f:
                self._expected_shap = json.load(f)
        return self._expected_shap
    
    def get_merchant_by_id(self, merchant_id: str) -> Optional[pd.Series]:
        merchants = self.load_merchants()
        match = merchants[merchants[config.MERCHANT_ID_COLUMN] == merchant_id]
        if len(match) > 0:
            return match.iloc[0]
        return None
    
    def get_merchant_transactions(self, merchant_id: str) -> pd.DataFrame:
        transactions = self.load_transactions()
        return transactions[transactions[config.MERCHANT_ID_COLUMN] == merchant_id].copy()
    
    def get_merchant_features(self, merchant_id: str) -> Optional[pd.Series]:
        features = self.load_features()
        match = features[features[config.MERCHANT_ID_COLUMN] == merchant_id]
        if len(match) > 0:
            return match.iloc[0]
        return None
    
    def get_merchant_label(self, merchant_id: str) -> Optional[int]:
        labels = self.load_labels()
        match = labels[labels[config.MERCHANT_ID_COLUMN] == merchant_id]
        if len(match) > 0:
            return match.iloc[0][config.TARGET_COLUMN]
        return None
    
    def get_all_merchant_ids(self) -> List[str]:
        merchants = self.load_merchants()
        return merchants[config.MERCHANT_ID_COLUMN].tolist()
    
    def get_demo_profiles(self) -> List[Dict]:
        test_profiles = self.load_test_profiles()
        return test_profiles.to_dict('records')

data_manager = DataManager()