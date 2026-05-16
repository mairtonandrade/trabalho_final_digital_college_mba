import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CadastroSolicitacao, Colaborador
from app.schemas import (
    CadastroSolicitacaoCreate,
    ColaboradorAprovacao,
    ColaboradorCreate,
    ColaboradorDetalhe,
    ColaboradorOut,
    ColaboradorUpdate,
    HistoricoCadastroItem,
    StatusCadastroUpdate,
)
from app.services.cadastro_historico import (
    STATUS_ATIVO,
    STATUS_ELEGIVEL_PAGAMENTO,
    analisar_alertas_cadastro,
    obter_historico_cadastro,
    registrar_cadastro,
)
from app.services.utils import formatar_cpf, validar_cpf

router = APIRouter(prefix="/colaboradores", tags=["colaboradores"])


def _col_out(c: Colaborador) -> ColaboradorOut:
    return ColaboradorOut.model_validate(c)


@router.get("", response_model=list[ColaboradorOut])
def listar(
    status: str | None = None,
    apenas_ativos_pagamento: bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(Colaborador)
    if apenas_ativos_pagamento:
        q = q.filter(Colaborador.status.in_(STATUS_ELEGIVEL_PAGAMENTO))
    elif status:
        q = q.filter(Colaborador.status == status)
    return q.order_by(Colaborador.nome_completo).all()


@router.get("/ativos", response_model=list[ColaboradorOut])
def listar_ativos(db: Session = Depends(get_db)):
    return db.query(Colaborador).filter(Colaborador.status.in_(STATUS_ELEGIVEL_PAGAMENTO)).all()


@router.get("/aprovados", response_model=list[ColaboradorOut])
def listar_aprovados(db: Session = Depends(get_db)):
    return listar_ativos(db)


@router.get("/{colaborador_id}", response_model=ColaboradorDetalhe)
def detalhe(colaborador_id: int, db: Session = Depends(get_db)):
    c = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
    if not c:
        raise HTTPException(404, "Colaborador não encontrado")
    hist = [HistoricoCadastroItem(**h) for h in obter_historico_cadastro(db, "colaborador", c.id)]
    return ColaboradorDetalhe(**_col_out(c).model_dump(), historico=hist)


@router.post("", response_model=ColaboradorOut)
def criar(payload: ColaboradorCreate, db: Session = Depends(get_db)):
    if not validar_cpf(payload.cpf):
        raise HTTPException(400, "CPF inválido")
    cpf_fmt = formatar_cpf(payload.cpf)
    if db.query(Colaborador).filter(Colaborador.cpf == cpf_fmt).first():
        raise HTTPException(400, "CPF já cadastrado como colaborador")
    c = Colaborador(
        cpf=cpf_fmt,
        nome_completo=payload.nome_completo.strip(),
        cargo=payload.cargo,
        banco=payload.banco.strip(),
        agencia=payload.agencia.strip(),
        conta=payload.conta.strip(),
        status="pendente",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    registrar_cadastro(
        db,
        "colaborador",
        c.id,
        "solicitacao_cadastro",
        "analista",
        {
            "cpf": cpf_fmt,
            "nome": c.nome_completo,
            "banco": c.banco,
            "agencia": c.agencia,
            "conta": c.conta,
        },
    )
    return c


@router.patch("/{colaborador_id}/decisao", response_model=ColaboradorOut)
def decisao_aprovacao(
    colaborador_id: int,
    payload: ColaboradorAprovacao,
    db: Session = Depends(get_db),
):
    c = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
    if not c:
        raise HTTPException(404, "Colaborador não encontrado")
    if payload.aprovado:
        c.status = "ativo"
        action = "colaborador_aprovado"
    else:
        c.status = "rejeitado"
        action = "colaborador_rejeitado"
    db.commit()
    db.refresh(c)
    registrar_cadastro(db, "colaborador", c.id, action, "gerente", {"status": c.status})
    return c


@router.patch("/{colaborador_id}/status", response_model=ColaboradorOut)
def alterar_status(
    colaborador_id: int,
    payload: StatusCadastroUpdate,
    db: Session = Depends(get_db),
):
    if payload.user_role != "gerente":
        raise HTTPException(403, "Somente o gerente pode ativar ou inativar cadastros.")
    c = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
    if not c:
        raise HTTPException(404, "Colaborador não encontrado")
    if payload.ativo:
        c.status = "ativo"
        action = "reativado"
    else:
        c.status = "inativo"
        action = "inativado"
    db.commit()
    db.refresh(c)
    registrar_cadastro(
        db,
        "colaborador",
        c.id,
        action,
        "gerente",
        {"status": c.status, "motivo": payload.motivo},
    )
    return c


@router.put("/{colaborador_id}", response_model=ColaboradorOut)
def editar_direto(
    colaborador_id: int,
    payload: ColaboradorUpdate,
    user_role: str = "gerente",
    db: Session = Depends(get_db),
):
    if user_role != "gerente":
        raise HTTPException(403, "Edição direta apenas para gerente. Use solicitação.")
    c = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
    if not c:
        raise HTTPException(404, "Colaborador não encontrado")
    dados = payload.model_dump(exclude_unset=True)
    for k, v in dados.items():
        if v is not None:
            setattr(c, k, v.strip() if isinstance(v, str) else v)
    db.commit()
    db.refresh(c)
    registrar_cadastro(db, "colaborador", c.id, "edicao_direta", "gerente", dados)
    return c


@router.delete("/{colaborador_id}", response_model=ColaboradorOut)
def excluir_direto(
    colaborador_id: int,
    user_role: str = "gerente",
    db: Session = Depends(get_db),
):
    if user_role != "gerente":
        raise HTTPException(403, "Exclusão direta apenas para gerente.")
    c = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
    if not c:
        raise HTTPException(404, "Colaborador não encontrado")
    c.status = "inativo"
    db.commit()
    db.refresh(c)
    registrar_cadastro(db, "colaborador", c.id, "exclusao_direta", "gerente", {"status": "inativo"})
    return c


@router.post("/{colaborador_id}/solicitar", response_model=dict)
def solicitar_alteracao(
    colaborador_id: int,
    payload: CadastroSolicitacaoCreate,
    db: Session = Depends(get_db),
):
    if payload.operacao not in ("editar", "excluir"):
        raise HTTPException(400, "Operação deve ser editar ou excluir")
    c = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
    if not c:
        raise HTTPException(404, "Colaborador não encontrado")
    pendente = (
        db.query(CadastroSolicitacao)
        .filter(
            CadastroSolicitacao.entity_type == "colaborador",
            CadastroSolicitacao.entity_id == colaborador_id,
            CadastroSolicitacao.status == "pendente",
        )
        .first()
    )
    if pendente:
        raise HTTPException(400, "Já existe solicitação pendente para este colaborador.")

    alertas = analisar_alertas_cadastro(
        f"solicitacao_{payload.operacao}",
        payload.dados or {"operacao": payload.operacao},
    )
    sol = CadastroSolicitacao(
        entity_type="colaborador",
        entity_id=colaborador_id,
        operacao=payload.operacao,
        dados_json=json.dumps(payload.dados or {}, ensure_ascii=False),
        motivo=payload.motivo,
        alertas_ia="; ".join(alertas) if alertas else None,
        solicitado_por=payload.user_role,
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)
    registrar_cadastro(
        db,
        "colaborador",
        colaborador_id,
        f"solicitacao_{payload.operacao}",
        payload.user_role,
        {"solicitacao_id": sol.id, "motivo": payload.motivo, "alertas_ia": alertas},
    )
    return {"id": sol.id, "status": "pendente", "alertas_ia": alertas}
