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
        mask = df["id_commercant"].str.contains(search, case=False, na=False)
        if "secteur_activite" in df.columns:
            mask = mask | df["secteur_activite"].str.contains(search, case=False, na=False)
        df = df[mask]

    total = len(df)
    start = (page - 1) * page_size
    page_df = df.iloc[start:start + page_size]

    merchants = []
    for _, row in page_df.iterrows():
        merchants.append(MerchantSummary(
            merchant_id=str(row.get("id_commercant", "")),
            activity=str(row.get("secteur_activite", "")) if pd.notna(row.get("secteur_activite")) else None,
            zone=str(row.get("departement", "")) if pd.notna(row.get("departement")) else None,
            is_first_time_borrower=bool(row.get("premiere_fois", 0)) if pd.notna(row.get("premiere_fois")) else None,
            activity_age_months=int(row.get("anciennete_activite_mois", 0)) if pd.notna(row.get("anciennete_activite_mois")) else None,
            data_completeness=float(row.get("score_integrite", 0)) if pd.notna(row.get("score_integrite")) else None,
        ))

    return MerchantListResponse(merchants=merchants, total=total, page=page, page_size=page_size)

@router.get("/merchants/{merchant_id}")
def get_merchant(merchant_id: str):
    if not settings.DEMO_PROFILES_PATH.exists():
        return {"error": "Merchant not found"}

    df = pd.read_csv(settings.DEMO_PROFILES_PATH)
    match = df[df["id_commercant"] == merchant_id]
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