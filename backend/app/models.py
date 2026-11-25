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
    score: int = Field(ge=0, le=1000)
    ml_score: Optional[int] = None
    business_score: Optional[int] = None
    score_weights: Optional[dict] = None
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

class CounterProposal(BaseModel):
    amount: int
    duration: int
    score: int
    effort_rate: float
    label: str

class ScoringResponse(BaseModel):
    merchant_id: str
    score: int = Field(ge=0, le=1000)
    score_max: int = 1000
    risk_level: RiskLevel
    decision: str
    ml_score: Optional[int] = None
    business_score: Optional[int] = None
    score_weights: Optional[dict] = None
    teg: Optional[float] = None
    teg_blocked: bool = False
    fraud_detected: bool = False
    counter_proposals: List[CounterProposal] = []
    top_factors: List[ShapFactor]
    explanation: str
    alerts: List[Alert]
    confidence: ConfidenceLevel
    data_quality: float = Field(ge=0, le=1)
    recommended_amount_min: int
    recommended_amount_max: int
    recommended_duration_months: int
    product_type: ProductType
    human_review_required: bool

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


# --- SQLAlchemy models ---
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class IMFConfig(Base):
    __tablename__ = "imf_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    interest_rate_annual = Column(Float, default=0.15)
    processing_fee = Column(Float, default=0.01)
    insurance_rate = Column(Float, default=0.005)
    max_amount_first_borrower = Column(Integer, default=50000)
    max_amount_regular = Column(Integer, default=500000)
    min_duration_months = Column(Integer, default=3)
    max_duration_months = Column(Integer, default=24)
    auto_accept_score = Column(Integer, default=700)
    manual_review_score = Column(Integer, default=500)
    max_effort_rate = Column(Float, default=0.45)
    guarantee_required_above = Column(Integer, default=200000)
    bonus_tontine = Column(Integer, default=40)
    bonus_guarantee = Column(Integer, default=30)
    malus_first_borrower = Column(Integer, default=-50)
    malus_fraud = Column(Integer, default=-80)
    trend_weight = Column(Float, default=0.20)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
