from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.fraud_engine import analisar_fraude, status_modelo

router = APIRouter(prefix="/ml", tags=["machine-learning"])


class ValidarPagamentoIn(BaseModel):
    valor: float = Field(gt=0)
    saldo_conta: float = 500_000
    fornecedor_nao_cadastrado: bool = False
    pf_nao_cadastrado: bool = False


@router.get("/status")
def modelo_status():
    return status_modelo()


@router.post("/validar")
def validar_pagamento(payload: ValidarPagamentoIn, db: Session = Depends(get_db)):
    """Simula análise do modelo sem gravar pagamento (útil para demo/academia)."""
    result = analisar_fraude(
        db,
        valor=payload.valor,
        saldo_conta=payload.saldo_conta,
        heuristic_score=0.1 if payload.fornecedor_nao_cadastrado else 0.0,
        flags_heuristicas=[],
        fornecedor_nao_cad=payload.fornecedor_nao_cadastrado,
        pf_nao_cad=payload.pf_nao_cadastrado,
    )
    return {
        "ml_score": result.ml_score,
        "ml_fraude_detectada": result.ml_fraude_detectada,
        "ml_motivos": result.ml_motivos,
        "modelo_carregado": result.modelo_carregado,
        "features": result.features,
    }
