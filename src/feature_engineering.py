import pandas as pd
import numpy as np
from typing import List, Dict
from pathlib import Path

from app.config import config

def load_raw_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    merchants = pd.read_csv(config.MERCHANTS_CSV)
    transactions = pd.read_csv(config.TRANSACTIONS_CSV)
    if 'date' in transactions.columns:
        transactions['date'] = pd.to_datetime(transactions['date'])
    return merchants, transactions

def compute_merchant_features(merchants: pd.DataFrame, 
                             transactions: pd.DataFrame) -> pd.DataFrame:
    features = merchants[["merchant_id"]].copy()
    
    tx_income = transactions[transactions["transaction_type"].isin(["paiement_recu", "depot"])]
    tx_expenses = transactions[transactions["transaction_type"].isin(["retrait", "achat_fournisseur"])]
    
    agg_income = tx_income.groupby("merchant_id").agg(
        total_income=("amount", "sum"),
        n_income_tx=("amount", "count"),
        avg_income_tx=("amount", "mean"),
        std_income_tx=("amount", "std")
    ).reset_index()
    
    agg_expenses = tx_expenses.groupby("merchant_id").agg(
        total_expenses=("amount", "sum"),
        n_expense_tx=("amount", "count"),
        avg_expense_tx=("amount", "mean"),
        std_expense_tx=("amount", "std")
    ).reset_index()
    
    tx_all = transactions.groupby("merchant_id").agg(
        total_transactions=("amount", "count"),
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
    
    features = features.merge(tx_all, on="merchant_id", how="left")
    features = features.merge(agg_income, on="merchant_id", how="left")
    features = features.merge(agg_expenses, on="merchant_id", how="left")
    
    for col in features.columns:
        if col != "merchant_id":
            features[col] = features[col].fillna(0)
    
    features["monthly_income"] = features["total_income"] / features["n_months_active"].replace(0, 1)
    features["monthly_expenses"] = features["total_expenses"] / features["n_months_active"].replace(0, 1)
    features["expense_income_ratio"] = features["monthly_expenses"] / features["monthly_income"].replace(0, 1)
    features["margin_ratio"] = 1 - features["expense_income_ratio"]
    features["avg_balance_income_ratio"] = features["avg_balance"] / features["monthly_income"].replace(0, 1)
    features["min_balance_income_ratio"] = features["min_balance"] / features["monthly_income"].replace(0, 1)
    features["transactions_per_day"] = features["total_transactions"] / features["n_active_days"].replace(0, 1)
    features["counterparty_diversity"] = features["n_counterparties"]
    features["documentation_quality"] = features["documented_ratio"]
    
    income_by_month = tx_income.groupby(
        ["merchant_id", tx_income["date"].dt.to_period("M")]
    )["amount"].sum().reset_index()
    
    income_volatility = income_by_month.groupby("merchant_id")["amount"].std() / (
        income_by_month.groupby("merchant_id")["amount"].mean() + 1
    ).reset_index()
    income_volatility.columns = ["merchant_id", "income_volatility"]
    
    features = features.merge(income_volatility, on="merchant_id", how="left")
    features["income_volatility"] = features["income_volatility"].fillna(0.3)
    
    growth = income_by_month.groupby("merchant_id")["amount"].apply(
        lambda x: (x.iloc[-1] - x.iloc[0]) / (x.iloc[0] + 1) if len(x) > 1 else 0
    ).reset_index()
    growth.columns = ["merchant_id", "income_growth"]
    features = features.merge(growth, on="merchant_id", how="left")
    features["income_growth"] = features["income_growth"].fillna(0)
    
    features["regularity_score"] = features["n_active_days"] / (features["n_months_active"] * 30)
    features["regularity_score"] = features["regularity_score"].clip(0, 1)
    
    concentration = transactions.groupby("merchant_id")["amount"].apply(
        lambda x: (x.nlargest(5).sum() / x.sum()) if x.sum() > 0 else 0
    ).reset_index()
    concentration.columns = ["merchant_id", "concentration_ratio"]
    features = features.merge(concentration, on="merchant_id", how="left")
    features["concentration_ratio"] = features["concentration_ratio"].fillna(0)
    
    return features

def prepare_model_features(features: pd.DataFrame) -> pd.DataFrame:
    feature_cols = [c for c in features.columns if c not in ["merchant_id", "repayment_label", "repayment_score"]]
    
    X = features[feature_cols].copy()
    X = X.fillna(0)
    X = X.replace([np.inf, -np.inf], 0)
    
    return X, feature_cols

if __name__ == "__main__":
    from app.config import config
    import numpy as np
    
    merchants, transactions = load_raw_data()
    features = compute_merchant_features(merchants, transactions)
    
    labels = pd.read_csv(config.LABELS_CSV)
    features = features.merge(labels[["merchant_id", "repayment_label", "repayment_score"]], 
                             on="merchant_id", how="left")
    
    features.to_csv(config.FEATURES_CSV, index=False)
    print(f"Saved features: {features.shape}")