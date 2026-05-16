"""
Treina o detector de fraudes (XGBoost) — dataset Kaggle ou sintético.
Execute: python ai_models/train_model.py
"""
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parent.parent
OUT_MODEL = ROOT / "ai_models" / "detector_fraudes_v1.pkl"
OUT_META = ROOT / "ai_models" / "model_metadata.json"

FEATURES = [
    "amount",
    "balance_diff",
    "hour_risk",
    "velocity_proxy",
    "nao_cadastrado",
    "valor_sobre_saldo",
]


def load_kaggle_data() -> pd.DataFrame | None:
    try:
        import kagglehub

        path = kagglehub.dataset_download("rupakroy/online-payments-fraud-detection-dataset")
        csvs = list(Path(path).rglob("*.csv"))
        if csvs:
            return pd.read_csv(csvs[0], nrows=200_000)
    except Exception as e:
        print(f"Kaggle indisponível ({e}). Usando dados sintéticos.")
    return None


def build_synthetic(n: int = 60000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    amount = rng.lognormal(8, 1.2, n)
    saldo_sim = rng.uniform(100_000, 2_000_000, n)
    pct = np.clip(amount / saldo_sim, 0, 1)
    balance_diff = amount * (0.02 + pct * 0.2)
    hour_risk = rng.uniform(0.05, 0.45, n)
    velocity_proxy = rng.uniform(0, 0.5, n)
    nao_cadastrado = (rng.random(n) < 0.12).astype(float)
    valor_sobre_saldo = pct
    is_fraud = (
        (amount > 120_000)
        | (balance_diff > amount * 0.08)
        | (velocity_proxy > 0.38)
        | (nao_cadastrado > 0)
        | (valor_sobre_saldo > 0.5)
    ).astype(int)
    is_fraud = (is_fraud & (rng.random(n) > 0.25)).astype(int)
    return pd.DataFrame(
        {
            "amount": amount,
            "balance_diff": balance_diff,
            "hour_risk": hour_risk,
            "velocity_proxy": velocity_proxy,
            "nao_cadastrado": nao_cadastrado,
            "valor_sobre_saldo": valor_sobre_saldo,
            "isFraud": is_fraud,
        }
    )


def prepare(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    target = "isFraud" if "isFraud" in df.columns else "isfraud"
    if "amount" not in df.columns and "Amount" in df.columns:
        df["amount"] = df["Amount"]
    if "oldbalanceOrg" in df.columns and "newbalanceOrig" in df.columns:
        df["balance_diff"] = (df["oldbalanceOrg"] - df["newbalanceOrig"]).abs()
        df["valor_sobre_saldo"] = df["balance_diff"] / (df["amount"] + 1)
    else:
        df["balance_diff"] = df.get("balance_diff", df["amount"] * 0.03)
        df["valor_sobre_saldo"] = df.get("valor_sobre_saldo", 0.1)
    df["hour_risk"] = df.get("hour_risk", 0.15)
    df["velocity_proxy"] = df.get("velocity_proxy", 0.1)
    df["nao_cadastrado"] = df.get("nao_cadastrado", 0)
    for c in FEATURES:
        if c not in df.columns:
            df[c] = 0
    X = df[FEATURES].fillna(0)
    y = df[target].astype(int)
    return X, y


def main():
    df = load_kaggle_data()
    source = "kaggle"
    if df is None:
        df = build_synthetic()
        source = "synthetic"

    print(f"Registros: {len(df)} | Fonte: {source}")
    X, y = prepare(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    try:
        from imblearn.over_sampling import SMOTE

        X_train, y_train = SMOTE(random_state=42).fit_resample(X_train, y_train)
        print("SMOTE aplicado.")
    except Exception:
        pass

    model = XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.08,
        scale_pos_weight=2,
        random_state=42,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    f1 = f1_score(y_test, pred)
    try:
        auc = roc_auc_score(y_test, proba)
    except Exception:
        auc = 0.0

    print(classification_report(y_test, pred, zero_division=0))
    print(f"F1: {f1:.4f} | AUC: {auc:.4f}")

    OUT_MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUT_MODEL)
    OUT_META.write_text(
        json.dumps(
            {
                "features": FEATURES,
                "f1_score": float(f1),
                "auc_score": float(auc),
                "source": source,
                "threshold_fraude": 0.55,
                "algoritmo": "XGBoost",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Modelo salvo: {OUT_MODEL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
