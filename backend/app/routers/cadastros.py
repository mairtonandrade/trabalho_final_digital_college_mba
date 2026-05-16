import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CadastroSolicitacao, Colaborador, Fornecedor
from app.schemas import CadastroSolicitacaoDecisao, CadastroSolicitacaoOut
from app.services.cadastro_historico import analisar_alertas_cadastro, registrar_cadastro

router = APIRouter(prefix="/cadastros", tags=["cadastros"])


def _nome_entidade(db: Session, entity_type: str, entity_id: int) -> str:
    if entity_type == "colaborador":
        c = db.query(Colaborador).filter(Colaborador.id == entity_id).first()
        return c.nome_completo if c else f"#{entity_id}"
    f = db.query(Fornecedor).filter(Fornecedor.id == entity_id).first()
    return f.razao_social if f else f"#{entity_id}"


def _sol_out(db: Session, s: CadastroSolicitacao) -> CadastroSolicitacaoOut:
    return CadastroSolicitacaoOut(
        id=s.id,
        entity_type=s.entity_type,
        entity_id=s.entity_id,
        operacao=s.operacao,
        dados_json=s.dados_json,
        motivo=s.motivo,
        status=s.status,
        alertas_ia=s.alertas_ia,
        solicitado_por=s.solicitado_por,
        created_at=s.created_at,
        entidade_nome=_nome_entidade(db, s.entity_type, s.entity_id),
    )


@router.get("/solicitacoes", response_model=list[CadastroSolicitacaoOut])
def listar_solicitacoes(status: str = "pendente", db: Session = Depends(get_db)):
    rows = (
        db.query(CadastroSolicitacao)
        .filter(CadastroSolicitacao.status == status)
        .order_by(CadastroSolicitacao.created_at.desc())
        .all()
    )
    return [_sol_out(db, s) for s in rows]


@router.patch("/solicitacoes/{solicitacao_id}", response_model=CadastroSolicitacaoOut)
def decidir_solicitacao(
    solicitacao_id: int,
    payload: CadastroSolicitacaoDecisao,
    db: Session = Depends(get_db),
):
    sol = db.query(CadastroSolicitacao).filter(CadastroSolicitacao.id == solicitacao_id).first()
    if not sol or sol.status != "pendente":
        raise HTTPException(404, "Solicitação não encontrada ou já decidida")

    if not payload.aprovada:
        sol.status = "rejeitada"
        db.commit()
        registrar_cadastro(
            db,
            sol.entity_type,
            sol.entity_id,
            "solicitacao_rejeitada",
            payload.user_role,
            {"operacao": sol.operacao, "motivo": payload.motivo_rejeicao},
        )
        return _sol_out(db, sol)

    dados = json.loads(sol.dados_json) if sol.dados_json else {}

    if sol.entity_type == "colaborador":
        ent = db.query(Colaborador).filter(Colaborador.id == sol.entity_id).first()
    else:
        ent = db.query(Fornecedor).filter(Fornecedor.id == sol.entity_id).first()
    if not ent:
        raise HTTPException(404, "Cadastro não encontrado")

    if sol.operacao == "excluir":
        ent.status = "inativo"
        action = "exclusao_aprovada"
    else:
        for k, v in dados.items():
            if v is not None and hasattr(ent, k):
                setattr(ent, k, v.strip() if isinstance(v, str) else v)
        action = "edicao_aprovada"

    sol.status = "aprovada"
    db.commit()
    registrar_cadastro(
        db, sol.entity_type, sol.entity_id, action, payload.user_role, dados
    )
    return _sol_out(db, sol)
