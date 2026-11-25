from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RiskLevel(str, Enum):
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"

class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ProductType(str, Enum):
    PROGRESSIVE_MICROLOAN = "progressive_microloan"
    STANDARD_MICROLOAN = "standard_microloan"
    GROWTH_MICROLOAN = "growth_microloan"

class Direction(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"

class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# --- IMF Pydantic schemas ---

class IMFConfigBase(BaseModel):
    name: str
    interest_rate_annual: float = 0.15
    processing_fee: float = 0.01
    insurance_rate: float = 0.005
    max_amount_first_borrower: int = 50000
    max_amount_regular: int = 500000
    min_duration_months: int = 3
    max_duration_months: int = 24
    auto_accept_score: int = 700
    manual_review_score: int = 500
    max_effort_rate: float = 0.45
    guarantee_required_above: int = 200000
    bonus_tontine: int = 40
    bonus_guarantee: int = 30
    malus_first_borrower: int = -50
    malus_fraud: int = -80
    trend_weight: float = 0.20


class IMFConfigCreate(IMFConfigBase):
    pass


class IMFConfigUpdate(IMFConfigBase):
    name: Optional[str] = None
    interest_rate_annual: Optional[float] = None
    processing_fee: Optional[float] = None
    insurance_rate: Optional[float] = None
    max_amount_first_borrower: Optional[int] = None
    max_amount_regular: Optional[int] = None
    min_duration_months: Optional[int] = None
    max_duration_months: Optional[int] = None
    auto_accept_score: Optional[int] = None
    manual_review_score: Optional[int] = None
    max_effort_rate: Optional[float] = None
    guarantee_required_above: Optional[int] = None
    bonus_tontine: Optional[int] = None
    bonus_guarantee: Optional[int] = None
    malus_first_borrower: Optional[int] = None
    malus_fraud: Optional[int] = None
    trend_weight: Optional[float] = None


class IMFConfigResponse(IMFConfigBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}