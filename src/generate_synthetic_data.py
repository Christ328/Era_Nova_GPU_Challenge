import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict
import random
from datetime import datetime, timedelta

from app.config import config

np.random.seed(42)
random.seed(42)

ACTIVITIES = [
    "alimentation", "restauration", "textile", 
    "transport", "recharge_telephonique", "commerce_detail"
]

ZONES = ["zone_1", "zone_2", "zone_3", "zone_4", "zone_5"]

TRANSACTION_TYPES = [
    "paiement_recu", "depot", "retrait", 
    "achat_fournisseur", "transfert", "recharge", "remboursement"
]

COUNTERPARTY_TYPES = [
    "client_particulier", "client_professionnel", "fournisseur",
    "service_public", "autre_commercant", "inconnu"
]

TX_TYPE_PROBS = [0.35, 0.15, 0.15, 0.15, 0.05, 0.10, 0.05]

ACTIVITY_TX_PER_MONTH = {
    "alimentation": 45, "restauration": 35, "textile": 25,
    "transport": 55, "recharge_telephonique": 80, "commerce_detail": 40
}

BASE_INCOME = {
    "micro": (50000, 200000),
    "small": (200000, 800000),
    "medium": (800000, 3000000)
}

def generate_merchants(n_merchants: int = 10000) -> pd.DataFrame:
    merchant_ids = [f"MCH-{i:06d}" for i in range(n_merchants)]
    activities = np.random.choice(ACTIVITIES, n_merchants)
    zones = np.random.choice(ZONES, n_merchants)
    is_first_time = np.random.choice([True, False], n_merchants, p=[0.35, 0.65])
    
    activity_age_months = np.where(
        is_first_time,
        np.random.randint(1, 12, n_merchants),
        np.random.randint(6, 60, n_merchants)
    )
    
    activity_size = np.random.choice(["micro", "small", "medium"], n_merchants, p=[0.5, 0.35, 0.15])
    
    monthly_income_mean = np.array([
        np.random.uniform(*BASE_INCOME[size]) for size in activity_size
    ])
    
    has_inconsistencies = np.random.choice([True, False], n_merchants, p=[0.08, 0.92])
    data_completeness = np.random.beta(8, 2, n_merchants).round(3)
    expense_documentation_ratio = np.random.beta(5, 3, n_merchants).round(3)
    
    return pd.DataFrame({
        "merchant_id": merchant_ids,
        "activity": activities,
        "zone": zones,
        "is_first_time_borrower": is_first_time,
        "activity_age_months": activity_age_months,
        "activity_size": activity_size,
        "monthly_income_mean": monthly_income_mean,
        "has_inconsistencies": has_inconsistencies,
        "data_completeness": data_completeness,
        "expense_documentation_ratio": expense_documentation_ratio
    })

def generate_transactions(merchants: pd.DataFrame, avg_months: int = 9) -> pd.DataFrame:
    all_tx = []
    
    for _, m in merchants.iterrows():
        merchant_id = m["merchant_id"]
        activity = m["activity"]
        monthly_income = m["monthly_income_mean"]
        activity_age = m["activity_age_months"]
        data_completeness = m["data_completeness"]
        
        n_months = min(activity_age, avg_months)
        base_tx_per_month = ACTIVITY_TX_PER_MONTH[activity]
        
        start_date = datetime.now() - timedelta(days=n_months * 30)
        
        for month in range(n_months):
            month_start = start_date + timedelta(days=month * 30)
            
            seasonal_factor = 1.3 if (activity in ["restauration", "textile"] and month in [11, 0, 1]) else 1.0
            n_tx = max(1, int(base_tx_per_month * seasonal_factor * data_completeness))
            
            tx_types = np.random.choice(TRANSACTION_TYPES, n_tx, p=TX_TYPE_PROBS)
            days = np.random.randint(0, 28, n_tx)
            counterparties = np.random.choice(COUNTERPARTY_TYPES, n_tx)
            is_documented = np.random.choice([True, False], n_tx, p=[0.75, 0.25])
            
            amounts = np.zeros(n_tx)
            for i, tx_type in enumerate(tx_types):
                if tx_type == "paiement_recu":
                    amounts[i] = np.random.lognormal(np.log(monthly_income / base_tx_per_month * 0.8), 0.5)
                elif tx_type == "depot":
                    amounts[i] = np.random.lognormal(np.log(monthly_income * 0.1), 0.7)
                elif tx_type == "retrait":
                    amounts[i] = np.random.lognormal(np.log(monthly_income * 0.08), 0.8)
                elif tx_type == "achat_fournisseur":
                    amounts[i] = np.random.lognormal(np.log(monthly_income * 0.3), 0.6)
                elif tx_type == "recharge":
                    amounts[i] = np.random.uniform(500, 20000)
                else:
                    amounts[i] = np.random.lognormal(10, 1)
            
            amounts = np.round(amounts, 0)
            balance_before = np.random.uniform(0, monthly_income * 2, n_tx)
            balance_after = np.where(
                np.isin(tx_types, ["paiement_recu", "depot"]),
                balance_before + amounts,
                np.maximum(0, balance_before - amounts)
            )
            
            for i in range(n_tx):
                all_tx.append({
                    "merchant_id": merchant_id,
                    "date": month_start + timedelta(days=int(days[i])),
                    "transaction_type": tx_types[i],
                    "amount": amounts[i],
                    "balance_before": round(balance_before[i], 0),
                    "balance_after": round(balance_after[i], 0),
                    "counterparty_type": counterparties[i],
                    "is_documented": is_documented[i]
                })
    
    return pd.DataFrame(all_tx)

def generate_labels(merchants: pd.DataFrame, transactions: pd.DataFrame) -> pd.DataFrame:
    income_mask = transactions["transaction_type"].isin(["paiement_recu", "depot"])
    expense_mask = transactions["transaction_type"].isin(["retrait", "achat_fournisseur"])
    
    tx_summary = transactions.groupby("merchant_id").agg(
        total_income=("amount", lambda x: x[income_mask.loc[x.index]].sum()),
        total_expenses=("amount", lambda x: x[expense_mask.loc[x.index]].sum()),
        n_transactions=("amount", "count"),
        n_months=("date", lambda x: x.dt.to_period("M").nunique()),
        avg_balance=("balance_after", "mean"),
        min_balance=("balance_after", "min"),
        income_volatility=("amount", lambda x: x[income_mask.loc[x.index]].std() / (x[income_mask.loc[x.index]].mean() + 1))
    ).reset_index()
    
    merchants_with_tx = merchants.merge(tx_summary, on="merchant_id", how="left")
    
    labels = []
    for _, m in merchants_with_tx.iterrows():
        income = m.get("total_income", m["monthly_income_mean"] * m.get("n_months", 9))
        expenses = m.get("total_expenses", income * 0.6)
        n_months = m.get("n_months", 9)
        avg_balance = m.get("avg_balance", 0)
        min_balance = m.get("min_balance", 0)
        volatility = m.get("income_volatility", 0.3)
        
        margin = (income - expenses) / (income + 1)
        
        repayment_score = 0.5
        
        if margin > 0.2:
            repayment_score += 0.25
        elif margin > 0:
            repayment_score += 0.1
        else:
            repayment_score -= 0.2
        
        if n_months >= 9:
            repayment_score += 0.1
        elif n_months < 3:
            repayment_score -= 0.15
        
        if avg_balance > income / 12:
            repayment_score += 0.1
        
        if min_balance < 0:
            repayment_score -= 0.1
        
        if volatility < 0.3:
            repayment_score += 0.1
        elif volatility > 0.6:
            repayment_score -= 0.1
        
        if m.get("is_first_time_borrower", False):
            repayment_score -= 0.05
        
        if m.get("has_inconsistencies", False):
            repayment_score -= 0.15
        
        if m.get("data_completeness", 1.0) < 0.7:
            repayment_score -= 0.1
        
        repayment_score += np.random.normal(0, 0.1)
        repayment_score = np.clip(repayment_score, 0, 1)
        
        label = 1 if repayment_score > 0.5 else 0
        
        labels.append({
            "merchant_id": m["merchant_id"],
            "repayment_label": label,
            "repayment_score": round(repayment_score, 4),
            "margin_ratio": round(margin, 4),
            "income_volatility": round(volatility, 4)
        })
    
    return pd.DataFrame(labels)

def generate_features(merchants: pd.DataFrame, 
                     transactions: pd.DataFrame,
                     labels: pd.DataFrame) -> pd.DataFrame:
    income_mask = transactions["transaction_type"].isin(["paiement_recu", "depot"])
    expense_mask = transactions["transaction_type"].isin(["retrait", "achat_fournisseur"])
    
    tx_summary = transactions.groupby("merchant_id").agg(
        total_transactions=("amount", "count"),
        total_income=("amount", lambda x: x[income_mask.loc[x.index]].sum()),
        total_expenses=("amount", lambda x: x[expense_mask.loc[x.index]].sum()),
        avg_transaction=("amount", "mean"),
        std_transaction=("amount", "std"),
        n_months_active=("date", lambda x: x.dt.to_period("M").nunique()),
        n_active_days=("date", lambda x: x.dt.date.nunique()),
        n_counterparties=("counterparty_type", "nunique"),
        documented_ratio=("is_documented", "mean"),
        avg_balance=("balance_after", "mean"),
        min_balance=("balance_after", "min"),
        max_balance=("balance_after", "max")
    ).reset_index()
    
    features = merchants[["merchant_id"]].copy()
    features = features.merge(tx_summary, on="merchant_id", how="left")
    
    for col in tx_summary.columns:
        if col != "merchant_id":
            features[col] = features[col].fillna(0)
    
    features["monthly_income_mean"] = features["total_income"] / features["n_months_active"].replace(0, 1)
    features["monthly_expenses_mean"] = features["total_expenses"] / features["n_months_active"].replace(0, 1)
    features["expense_income_ratio"] = features["monthly_expenses_mean"] / features["monthly_income_mean"].replace(0, 1)
    features["margin_ratio"] = 1 - features["expense_income_ratio"]
    features["avg_balance_income_ratio"] = features["avg_balance"] / features["monthly_income_mean"].replace(0, 1)
    features["min_balance_income_ratio"] = features["min_balance"] / features["monthly_income_mean"].replace(0, 1)
    features["transactions_per_day"] = features["total_transactions"] / (features["n_active_days"].replace(0, 1))
    features["counterparty_diversity"] = features["n_counterparties"]
    features["documentation_quality"] = features["documented_ratio"]
    
    income_by_month = transactions[income_mask].groupby(
        ["merchant_id", transactions["date"].dt.to_period("M")]
    )["amount"].sum().reset_index()
    
    income_volatility = income_by_month.groupby("merchant_id")["amount"].agg(['std', 'mean']).reset_index()
    income_volatility["income_volatility"] = income_volatility["std"] / (income_volatility["mean"] + 1)
    income_volatility = income_volatility[["merchant_id", "income_volatility"]]
    
    features = features.merge(income_volatility, on="merchant_id", how="left")
    features["income_volatility"] = features["income_volatility"].fillna(0.3)
    
    growth = income_by_month.groupby("merchant_id")["amount"].apply(
        lambda x: (x.iloc[-1] - x.iloc[0]) / (x.iloc[0] + 1) if len(x) > 1 else 0
    ).reset_index()
    growth.columns = ["merchant_id", "income_growth"]
    features = features.merge(growth, on="merchant_id", how="left")
    features["income_growth"] = features["income_growth"].fillna(0)
    
    features["regularity_score"] = (features["n_active_days"] / (features["n_months_active"] * 30)).clip(0, 1)
    
    conc = transactions.groupby("merchant_id")["amount"].apply(
        lambda x: (x.nlargest(5).sum() / x.sum()) if x.sum() > 0 else 0
    ).reset_index()
    conc.columns = ["merchant_id", "concentration_ratio"]
    features = features.merge(conc, on="merchant_id", how="left")
    features["concentration_ratio"] = features["concentration_ratio"].fillna(0)
    
    features = features.merge(
        labels[["merchant_id", "repayment_label", "repayment_score"]], 
        on="merchant_id", how="left"
    )
    
    return features

def save_all_data():
    print("Generating merchants...")
    merchants = generate_merchants(10000)
    
    # Prepend demo profiles to ensure they exist in merchants
    demo_merchants = pd.DataFrame({
        "merchant_id": config.DEMO_PROFILES,
        "activity": ["alimentation", "restauration", "commerce_detail"],
        "zone": ["zone_1", "zone_2", "zone_3"],
        "is_first_time_borrower": [False, True, True],
        "activity_age_months": [36, 8, 3],
        "activity_size": ["small", "micro", "micro"],
        "monthly_income_mean": [800000, 150000, 90000],
        "has_inconsistencies": [False, False, True],
        "data_completeness": [0.95, 0.65, 0.45],
        "expense_documentation_ratio": [0.85, 0.40, 0.20]
    })
    merchants = pd.concat([demo_merchants, merchants], ignore_index=True)
    
    print("Generating transactions...")
    transactions = generate_transactions(merchants)
    
    print("Generating labels...")
    labels = generate_labels(merchants, transactions)
    
    print("Generating features...")
    features = generate_features(merchants, transactions, labels)
    
    print("Saving data...")
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    merchants.to_csv(config.MERCHANTS_CSV, index=False)
    transactions.to_csv(config.TRANSACTIONS_CSV, index=False)
    labels.to_csv(config.LABELS_CSV, index=False)
    features.to_csv(config.FEATURES_CSV, index=False)
    
    demo_merchants.to_csv(config.TEST_PROFILES_CSV, index=False)
    
    data_dict = []
    for col in features.columns:
        if col not in ["merchant_id", "repayment_label", "repayment_score"]:
            data_dict.append({
                "feature": col,
                "label": col.replace("_", " ").title(),
                "type": str(features[col].dtype),
                "unit": "",
                "definition": f"Feature: {col}",
                "formula": "",
                "missing_treatment": "fillna(0)"
            })
    
    pd.DataFrame(data_dict).to_csv(config.DATA_DICTIONARY_CSV, index=False)
    
    print(f"Saved {len(merchants)} merchants")
    print(f"Saved {len(transactions)} transactions")
    print(f"Saved {len(features)} feature rows")
    print("Done!")

if __name__ == "__main__":
    save_all_data()