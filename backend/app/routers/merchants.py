import pandas as pd
from fastapi import APIRouter, Query
from typing import Optional
from app.config import settings
from app.models import MerchantListResponse, MerchantSummary

router = APIRouter()

@router.get("/merchants", response_model=MerchantListResponse)
def list_merchants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
):
    if not settings.DEMO_PROFILES_PATH.exists():
        return MerchantListResponse(merchants=[], total=0, page=page, page_size=page_size)

    df = pd.read_csv(settings.DEMO_PROFILES_PATH)

    if search:
        mask = df["merchant_id"].str.contains(search, case=False, na=False)
        if "activity" in df.columns:
            mask = mask | df["activity"].str.contains(search, case=False, na=False)
        df = df[mask]

    total = len(df)
    start = (page - 1) * page_size
    page_df = df.iloc[start:start + page_size]

    merchants = []
    for _, row in page_df.iterrows():
        merchants.append(MerchantSummary(
            merchant_id=str(row.get("merchant_id", "")),
            activity=str(row.get("activity", "")) if pd.notna(row.get("activity")) else None,
            zone=str(row.get("zone", "")) if pd.notna(row.get("zone")) else None,
            is_first_time_borrower=bool(row.get("is_first_time_borrower", False)) if pd.notna(row.get("is_first_time_borrower")) else None,
            activity_age_months=int(row.get("activity_age_months", 0)) if pd.notna(row.get("activity_age_months")) else None,
            data_completeness=float(row.get("data_completeness", 0)) if pd.notna(row.get("data_completeness")) else None,
        ))

    return MerchantListResponse(merchants=merchants, total=total, page=page, page_size=page_size)

@router.get("/merchants/{merchant_id}")
def get_merchant(merchant_id: str):
    if not settings.DEMO_PROFILES_PATH.exists():
        return {"error": "Merchant not found"}

    df = pd.read_csv(settings.DEMO_PROFILES_PATH)
    match = df[df["merchant_id"] == merchant_id]
    if len(match) == 0:
        return {"error": "Merchant not found"}

    row = match.iloc[0]
    result = {}
    for col in df.columns:
        val = row[col]
        if pd.isna(val):
            result[col] = None
        elif isinstance(val, (int, float)):
            result[col] = float(val)
        else:
            result[col] = str(val)
    return result