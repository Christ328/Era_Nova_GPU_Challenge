import uuid
from fastapi import APIRouter, HTTPException
from app.models import AssessmentResponse, DecisionRequest, DecisionResponse
from app.services.scoring_service import scoring_service
from app.services.decision_service import decision_service
from app.config import settings
import pandas as pd

router = APIRouter()

@router.post("/assessments", response_model=AssessmentResponse)
def create_assessment(merchant_id: str):
    if not settings.DEMO_PROFILES_PATH.exists():
        raise HTTPException(status_code=404, detail="Demo profiles not found")

    df = pd.read_csv(settings.DEMO_PROFILES_PATH)
    match = df[df["id_commercant"] == merchant_id]
    if len(match) == 0:
        raise HTTPException(status_code=404, detail=f"Merchant {merchant_id} not found")

    row = match.iloc[0]
    features = {}
    for col in df.columns:
        if col == "id_commercant":
            continue
        val = row[col]
        if pd.isna(val):
            features[col] = 0
        elif isinstance(val, (int, float)):
            features[col] = float(val)
        elif isinstance(val, bool):
            features[col] = bool(val)
        else:
            features[col] = val

    result = scoring_service.score(features)

    return AssessmentResponse(
        merchant_id=merchant_id,
        score=result["score"],
        risk_level=result["risk_level"],
        confidence=result["confidence"],
        data_quality=result["data_quality"],
        recommended_amount_min=result["recommended_amount_min"],
        recommended_amount_max=result["recommended_amount_max"],
        recommended_duration_months=result["recommended_duration_months"],
        product_type=result["product_type"],
        human_review_required=result["human_review_required"],
        top_factors=result["top_factors"],
        alerts=result["alerts"],
        explanation=result["explanation"],
    )

@router.post("/assessments/score", response_model=AssessmentResponse)
def score_custom(features: dict):
    result = scoring_service.score(features)

    return AssessmentResponse(
        merchant_id=features.get("id_commercant", "CUSTOM"),
        score=result["score"],
        risk_level=result["risk_level"],
        confidence=result["confidence"],
        data_quality=result["data_quality"],
        recommended_amount_min=result["recommended_amount_min"],
        recommended_amount_max=result["recommended_amount_max"],
        recommended_duration_months=result["recommended_duration_months"],
        product_type=result["product_type"],
        human_review_required=result["human_review_required"],
        top_factors=result["top_factors"],
        alerts=result["alerts"],
        explanation=result["explanation"],
    )

@router.post("/assessments/{assessment_id}/decision", response_model=DecisionResponse)
def submit_decision(assessment_id: str, body: DecisionRequest):
    result = decision_service.save_decision(
        assessment_id=assessment_id,
        merchant_id=body.assessment_id.split("_")[0] if "_" in body.assessment_id else "unknown",
        score=0,
        risk_level="UNKNOWN",
        decision=body.decision,
        adjusted_amount=body.adjusted_amount,
        adjusted_duration=body.adjusted_duration,
        comments=body.comments,
    )
    return DecisionResponse(**result)