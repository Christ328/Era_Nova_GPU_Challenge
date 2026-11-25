import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import AssessmentResponse, DecisionRequest, DecisionResponse, ScoringResponse, CounterProposal, IMFConfig
from app.services.scoring_service import scoring_service
from app.services.decision_service import decision_service
from app.services.teg_service import compute_teg, TEGExceededException
from app.services.fraud_service import detect_circular_transactions
from app.database import get_db
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
        ml_score=result.get("ml_score"),
        business_score=result.get("business_score"),
        score_weights=result.get("score_weights"),
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


@router.post("/assessments/score", response_model=ScoringResponse)
def score_custom(features: dict, imf_id: int = 1, db: Session = Depends(get_db)):
    # Load IMF config; fall back to a default object if not found
    imf = db.query(IMFConfig).filter(IMFConfig.id == imf_id).first()
    if imf is None:
        imf = IMFConfig(
            name="IMF_DEFAULT",
            interest_rate_annual=0.15,
            processing_fee=0.01,
            insurance_rate=0.005,
            auto_accept_score=700,
            manual_review_score=500,
            bonus_tontine=40,
            bonus_guarantee=30,
            malus_first_borrower=-50,
            malus_fraud=-80,
        )

    try:
        result = scoring_service.score(features)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    score = result["score"]
    alerts = list(result["alerts"])

    # Apply IMF bonus/malus
    if features.get("membre_tontine"):
        score += imf.bonus_tontine
    if features.get("garantie"):
        score += imf.bonus_guarantee
    if features.get("premiere_fois"):
        score += imf.malus_first_borrower
    score = max(0, min(1000, score))

    # Fraud detection
    fraud_detected = False
    transactions = features.get("transactions", [])
    if isinstance(transactions, list) and len(transactions) > 0:
        fraud_detected = detect_circular_transactions(transactions)
        if fraud_detected:
            score += imf.malus_fraud
            score = max(0, min(1000, score))
            alerts.append({
                "severity": "error",
                "message": "Transactions circulaires détectées — risque de fraude élevé.",
                "rule_name": "fraud_detection",
            })

    # TEG computation
    teg = None
    teg_blocked = False
    montant = features.get("montant_demande", 0)
    duree = max(features.get("duree_credit_mois", 1), 1)
    mensualite = features.get(
        "mensualite",
        (montant / duree) * (1 + imf.interest_rate_annual / 12) if montant and duree else 0,
    )
    if montant and mensualite:
        try:
            teg = compute_teg(
                principal=float(montant),
                monthly_payment=float(mensualite),
                n_months=int(duree),
                fees_rate=float(imf.processing_fee),
                insurance_rate=float(imf.insurance_rate),
            )
        except TEGExceededException as exc:
            teg = exc.teg
            teg_blocked = True
            alerts.append({
                "severity": "error",
                "message": str(exc),
                "rule_name": "teg_regulatory_cap",
            })

    # Decision logic (teg_blocked overrides ACCEPTED)
    if teg_blocked:
        decision = "REFUSED_REGULATORY"
    elif score >= imf.auto_accept_score:
        decision = "ACCEPTED"
    elif score >= imf.manual_review_score:
        decision = "MANUAL_REVIEW"
    else:
        decision = "REFUSED_RISK"

    # Counter-proposals when not accepted
    counter_proposals_raw: list = []
    if decision != "ACCEPTED":
        counter_proposals_raw = scoring_service.generate_counter_proposals(features, imf)

    counter_proposals = [CounterProposal(**cp) for cp in counter_proposals_raw]

    return ScoringResponse(
        merchant_id=features.get("id_commercant", "CUSTOM"),
        score=score,
        score_max=1000,
        risk_level=result["risk_level"],
        decision=decision,
        ml_score=result.get("ml_score"),
        business_score=result.get("business_score"),
        score_weights=result.get("score_weights"),
        teg=teg,
        teg_blocked=teg_blocked,
        fraud_detected=fraud_detected,
        counter_proposals=counter_proposals,
        top_factors=result["top_factors"],
        explanation=result["explanation"],
        alerts=alerts,
        confidence=result["confidence"],
        data_quality=result["data_quality"],
        recommended_amount_min=result["recommended_amount_min"],
        recommended_amount_max=result["recommended_amount_max"],
        recommended_duration_months=result["recommended_duration_months"],
        product_type=result["product_type"],
        human_review_required=result["human_review_required"],
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
