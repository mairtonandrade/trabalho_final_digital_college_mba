"""
Motor de detecção de fraude — integra XGBoost treinado + regras de negócio.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from sqlalchemy.orm import Session

from app.models import Pagamento

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODEL_PATH = BASE_DIR / "ai_models" / "detector_fraudes_v1.pkl"
META_PATH = BASE_DIR / "ai_models" / "model_metadata.json"

# Limiar calibrado: acima disso o modelo classifica como FRAUDE
THRESHOLD_FRAUDE = 0.55

_model = None
_metadata: dict | None = None


@dataclass
class FraudAnalysisResult:
    ml_score: float
    ml_fraude_detectada: bool
    ml_motivos: list[str] = field(default_factory=list)
    modelo_carregado: bool = False
    modelo_fonte: str = "fallback"
    f1_score: float | None = None
    features: dict = field(default_factory=dict)


def _load_model():
    global _model, _metadata
    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    if _metadata is None and META_PATH.exists():
        _metadata = json.loads(META_PATH.read_text(encoding="utf-8"))
    return _model, _metadata or {}


def _velocity_score(db: Session, documento: str, fornecedor_id: int | None) -> float:
    hoje = datetime.utcnow().date()
    q = db.query(Pagamento)
    if fornecedor_id:
        q = q.filter(Pagamento.fornecedor_id == fornecedor_id)
    pagamentos = q.all()
    count_hoje = sum(1 for p in pagamentos if p.created_at.date() == hoje)
    if count_hoje >= 3:
        return 0.45
    if count_hoje >= 2:
        return 0.28
    return 0.08


def extrair_features(
    db: Session,
    valor: float,
    saldo_conta: float | None,
    heuristic_score: float,
    fornecedor_nao_cad: bool,
    pf_nao_cad: bool,
    fornecedor_id: int | None = None,
) -> dict[str, float]:
    amount = float(valor)
    saldo = float(saldo_conta or 500_000)
    pct_saldo = min(amount / max(saldo, 1), 1.0)
    # Simula inconsistência de saldo (padrão do dataset Kaggle: diff alto = suspeito)
    balance_diff = amount * (0.05 + pct_saldo * 0.15)
    hour = datetime.utcnow().hour
    hour_risk = 0.35 if hour < 6 or hour > 22 else (0.2 if amount > 80_000 else 0.08)
    velocity_proxy = max(heuristic_score, _velocity_score(db, "", fornecedor_id))
    nao_cadastrado = 1.0 if (fornecedor_nao_cad or pf_nao_cad) else 0.0
    valor_alto = 1.0 if amount > 200_000 else 0.0
    return {
        "amount": amount,
        "balance_diff": balance_diff,
        "hour_risk": hour_risk,
        "velocity_proxy": velocity_proxy,
        "nao_cadastrado": nao_cadastrado,
        "valor_sobre_saldo": pct_saldo,
        "valor_alto": valor_alto,
    }


def analisar_fraude(
    db: Session,
    valor: float,
    saldo_conta: float | None,
    heuristic_score: float,
    flags_heuristicas: list[str],
    fornecedor_nao_cad: bool = False,
    pf_nao_cad: bool = False,
    fornecedor_id: int | None = None,
    tipo_despesa: str = "fornecedor",
) -> FraudAnalysisResult:
    """Executa o modelo XGBoost e enriquece com regras explicáveis."""
    model, meta = _load_model()
    feats = extrair_features(
        db, valor, saldo_conta, heuristic_score, fornecedor_nao_cad, pf_nao_cad, fornecedor_id
    )
    feature_names = meta.get("features", ["amount", "balance_diff", "hour_risk", "velocity_proxy"])
    X = np.array([[feats.get(f, 0.0) for f in feature_names]])

    motivos: list[str] = []
    ml_score = 0.0
    modelo_carregado = model is not None

    if modelo_carregado:
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(X)[0]
                ml_score = float(proba[1]) if len(proba) > 1 else float(proba[0])
            else:
                ml_score = float(model.predict(X)[0])
            pred = int(model.predict(X)[0]) if hasattr(model, "predict") else int(ml_score >= THRESHOLD_FRAUDE)
            if pred == 1:
                motivos.append(
                    f"Modelo XGBoost classificou FRAUDE (probabilidade {ml_score:.0%})."
                )
        except Exception as e:
            motivos.append(f"Fallback heurístico: modelo indisponível ({e}).")
            modelo_carregado = False

    if not modelo_carregado:
        ml_score = min(
            feats["amount"] / 400_000
            + feats["velocity_proxy"]
            + feats["nao_cadastrado"] * 0.25
            + feats["valor_sobre_saldo"] * 0.2,
            0.95,
        )
        motivos.append("Score calculado por regras (treine o modelo com ai_models/train_model.py).")

    # Regras explicáveis alinhadas ao treinamento Kaggle
    if feats["amount"] > 150_000:
        motivos.append(f"Valor elevado: R$ {valor:,.2f} acima do padrão operacional.")
    if feats["valor_sobre_saldo"] > 0.4:
        motivos.append(
            f"Pagamento consome {feats['valor_sobre_saldo']:.0%} do saldo da conta — risco de liquidez."
        )
    if feats["velocity_proxy"] > 0.25:
        motivos.append("Velocity rule: múltiplos pagamentos ao mesmo beneficiário no dia.")
    if fornecedor_nao_cad:
        motivos.append("Beneficiário PJ fora da whitelist de fornecedores.")
    if pf_nao_cad:
        motivos.append("CPF não cadastrado como colaborador no RH.")
    if tipo_despesa == "salario" and feats["amount"] > 50_000:
        motivos.append("Salário com valor atípico para validação de competência.")

    for f in flags_heuristicas:
        if "Benford" in f or "fracionamento" in f or "ALERTA" in f:
            motivos.append(f"Regra heurística: {f}")

    fraude = ml_score >= THRESHOLD_FRAUDE
    if fraude and not any("Modelo XGBoost" in m for m in motivos):
        motivos.insert(0, f"Score ML {ml_score:.0%} ≥ limiar {THRESHOLD_FRAUDE:.0%} → suspeita de fraude.")

    return FraudAnalysisResult(
        ml_score=round(ml_score, 4),
        ml_fraude_detectada=fraude,
        ml_motivos=list(dict.fromkeys(motivos)),
        modelo_carregado=modelo_carregado,
        modelo_fonte=meta.get("source", "desconhecido"),
        f1_score=meta.get("f1_score"),
        features=feats,
    )


def status_modelo() -> dict:
    model, meta = _load_model()
    return {
        "modelo_disponivel": model is not None,
        "caminho": str(MODEL_PATH),
        "features": meta.get("features", []),
        "f1_score": meta.get("f1_score"),
        "fonte_treino": meta.get("source"),
        "limiar_fraude": THRESHOLD_FRAUDE,
        "algoritmo": "XGBoost",
    }
