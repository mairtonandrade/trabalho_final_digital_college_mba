"""Compatibilidade — use fraud_engine para análise completa."""
from app.services.fraud_engine import FraudAnalysisResult, analisar_fraude, status_modelo

__all__ = ["FraudAnalysisResult", "analisar_fraude", "status_modelo", "predict_fraud_score", "score_final"]


def predict_fraud_score(valor: float, heuristic_score: float = 0.0) -> float:
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        r = analisar_fraude(db, valor, 500_000, heuristic_score)
        return r.ml_score
    finally:
        db.close()


def score_final(heuristic_score: float, ml_score: float, dados_conferem: bool) -> float:
    gen_penalty = 0.0 if dados_conferem else 0.25
    combined = 0.30 * heuristic_score + 0.50 * ml_score + gen_penalty
    return min(max(combined, 0.0), 1.0)
