from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas import RiskLevel, ConfidenceLevel, ProductType, Direction, Severity

class ShapFactor(BaseModel):
    feature: str
    label: str
    value: float
    impact: float
    direction: Direction

class Alert(BaseModel):
    severity: Severity
    message: str
    rule_name: str

class AssessmentResponse(BaseModel):
    merchant_id: str
    score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    confidence: ConfidenceLevel
    data_quality: float = Field(ge=0, le=1)
    recommended_amount_min: int
    recommended_amount_max: int
    recommended_duration_months: int
    product_type: ProductType
    human_review_required: bool
    top_factors: List[ShapFactor]
    alerts: List[Alert]
    explanation: str

class MerchantSummary(BaseModel):
    merchant_id: str
    activity: Optional[str] = None
    zone: Optional[str] = None
    is_first_time_borrower: Optional[bool] = None
    activity_age_months: Optional[int] = None
    data_completeness: Optional[float] = None

class MerchantListResponse(BaseModel):
    merchants: List[MerchantSummary]
    total: int
    page: int
    page_size: int

class DecisionRequest(BaseModel):
    assessment_id: str
    decision: str
    adjusted_amount: Optional[int] = None
    adjusted_duration: Optional[int] = None
    comments: Optional[str] = None

class DecisionResponse(BaseModel):
    assessment_id: str
    decision: str
    message: str

class BenchmarkResponse(BaseModel):
    dataset_size: int
    n_features: int
    cpu_time: float
    gpu_time: float
    speedup: float
    cpu_auc: float
    gpu_auc: float
    gpu_type: str
    xgboost_version: str