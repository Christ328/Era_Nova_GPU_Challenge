import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json

@dataclass
class Config:
    PROJECT_ROOT: Path = Path(__file__).parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    MODEL_DIR: Path = PROJECT_ROOT / "model"
    RULES_DIR: Path = PROJECT_ROOT / "rules"
    EXPLANATIONS_DIR: Path = PROJECT_ROOT / "explanations"
    
    MODEL_PATH: Path = MODEL_DIR / "xgboost_model.json"
    MODEL_METADATA_PATH: Path = MODEL_DIR / "model_metadata.json"
    FEATURE_SCHEMA_PATH: Path = MODEL_DIR / "feature_schema.json"
    FEATURE_ORDER_PATH: Path = MODEL_DIR / "feature_order.json"
    
    MERCHANTS_CSV: Path = DATA_DIR / "merchants.csv"
    TRANSACTIONS_CSV: Path = DATA_DIR / "transactions.csv"
    LABELS_CSV: Path = DATA_DIR / "labels.csv"
    FEATURES_CSV: Path = DATA_DIR / "features.csv"
    TEST_PROFILES_CSV: Path = DATA_DIR / "test_profiles.csv"
    DATA_DICTIONARY_CSV: Path = DATA_DIR / "data_dictionary.csv"
    
    BUSINESS_RULES_PATH: Path = RULES_DIR / "business_rules.json"
    FEATURE_LABELS_PATH: Path = EXPLANATIONS_DIR / "feature_labels.json"
    EXPLANATION_TEMPLATES_PATH: Path = EXPLANATIONS_DIR / "explanation_templates.json"
    EXPECTED_SHAP_PATH: Path = EXPLANATIONS_DIR / "expected_shap_results.json"
    
    # Model config
    TARGET_COLUMN: str = "repayment_label"
    MERCHANT_ID_COLUMN: str = "merchant_id"
    
    # Score config
    SCORE_MIN: int = 0
    SCORE_MAX: int = 100
    SCORE_THRESHOLDS: Dict[str, int] = field(default_factory=lambda: {
        "very_low": 30,
        "low": 45,
        "moderate": 60,
        "good": 75,
        "very_good": 85
    })
    
    # Risk levels
    RISK_LEVELS: Dict[str, Dict] = field(default_factory=lambda: {
        "very_high": {"min": 0, "max": 29, "label": "Très élevé", "color": "#dc2626"},
        "high": {"min": 30, "max": 44, "label": "Élevé", "color": "#ea580c"},
        "moderate": {"min": 45, "max": 59, "label": "Modéré", "color": "#ca8a04"},
        "low": {"min": 60, "max": 74, "label": "Faible", "color": "#16a34a"},
        "very_low": {"min": 75, "max": 100, "label": "Très faible", "color": "#059669"}
    })
    
    # Confidence levels
    CONFIDENCE_LEVELS: Dict[str, Dict] = field(default_factory=lambda: {
        "low": {"min": 0, "max": 39, "label": "Faible", "color": "#dc2626"},
        "medium": {"min": 40, "max": 69, "label": "Moyenne", "color": "#ca8a04"},
        "high": {"min": 70, "max": 100, "label": "Élevée", "color": "#059669"}
    })
    
    # Product types
    PRODUCT_TYPES: Dict[str, Dict] = field(default_factory=lambda: {
        "progressive_microloan": {
            "label": "Microcrédit progressif",
            "description": "Montant initial faible, augmentable selon remboursement",
            "min_amount": 50000,
            "max_amount": 200000,
            "duration_months": [3, 6, 9]
        },
        "standard_microloan": {
            "label": "Microcrédit standard",
            "description": "Montant et durée standards",
            "min_amount": 100000,
            "max_amount": 500000,
            "duration_months": [6, 12, 18]
        },
        "growth_microloan": {
            "label": "Microcrédit croissance",
            "description": "Pour activités en expansion",
            "min_amount": 200000,
            "max_amount": 1000000,
            "duration_months": [12, 18, 24]
        }
    })
    
    # Demo profiles
    DEMO_PROFILES: List[str] = field(default_factory=lambda: [
        "MCH-DEMO-01",
        "MCH-DEMO-02", 
        "MCH-DEMO-03"
    ])

config = Config()