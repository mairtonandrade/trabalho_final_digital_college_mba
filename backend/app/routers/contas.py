from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ContaBancaria, MovimentoConta
from app.schemas import ContaBancariaOut, MovimentoContaOut, ReceitaCreate
from app.services.conta_service import creditar_receita

router = APIRouter(prefix="/contas", tags=["contas"])


@router.get("", response_model=list[ContaBancariaOut])
def listar_contas(db: Session = Depends(get_db)):
    return (
        db.query(ContaBancaria)
        .filter(ContaBancaria.ativa == 1)
        .order_by(ContaBancaria.nome)
        .all()
    )


@router.get("/{conta_id}/movimentos", response_model=list[MovimentoContaOut])
def movimentos_conta(conta_id: int, db: Session = Depends(get_db)):
    return (
        db.query(MovimentoConta)
        .filter(MovimentoConta.conta_id == conta_id)
        .order_by(MovimentoConta.created_at.desc())
        .limit(50)
        .all()
    )


@router.post("/{conta_id}/receita", response_model=ContaBancariaOut)
def registrar_receita(
    conta_id: int,
    payload: ReceitaCreate,
    db: Session = Depends(get_db),
):
    try:
        return creditar_receita(db, conta_id, payload.valor, payload.descricao)
    except ValueError as e:
        raise HTTPException(400, str(e))
