import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    BACKEND_DIR: Path = Path(__file__).parent.parent
    MODEL_DIR: Path = BACKEND_DIR / "model"
    RULES_DIR: Path = BACKEND_DIR / "rules"
    DATA_DIR: Path = BACKEND_DIR / "data"

    MODEL_PATH: Path = MODEL_DIR / "xgboost_model.json"
    MODEL_METADATA_PATH: Path = MODEL_DIR / "model_metadata.json"
    FEATURE_SCHEMA_PATH: Path = MODEL_DIR / "feature_schema.json"
    FEATURE_ORDER_PATH: Path = MODEL_DIR / "feature_order.json"

    BUSINESS_RULES_PATH: Path = RULES_DIR / "business_rules.json"
    DEMO_PROFILES_PATH: Path = DATA_DIR / "demo_profiles.csv"

    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()