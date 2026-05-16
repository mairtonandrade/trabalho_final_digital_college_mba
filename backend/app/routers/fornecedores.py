import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CadastroSolicitacao, Fornecedor
from app.schemas import (
    CadastroSolicitacaoCreate,
    FornecedorAprovacao,
    FornecedorCreate,
    FornecedorDetalhe,
    FornecedorOut,
    FornecedorUpdate,
    HistoricoCadastroItem,
    StatusCadastroUpdate,
)
from app.services.cadastro_historico import (
    STATUS_ELEGIVEL_PAGAMENTO,
    obter_historico_cadastro,
    registrar_cadastro,
    analisar_alertas_cadastro,
)
from app.services.utils import formatar_cnpj, validar_cnpj

router = APIRouter(prefix="/fornecedores", tags=["fornecedores"])


@router.get("", response_model=list[FornecedorOut])
def listar(
    status: str | None = None,
    apenas_ativos_pagamento: bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(Fornecedor)
    if apenas_ativos_pagamento:
        q = q.filter(Fornecedor.status.in_(STATUS_ELEGIVEL_PAGAMENTO))
    elif status:
        q = q.filter(Fornecedor.status == status)
    return q.order_by(Fornecedor.created_at.desc()).all()


@router.get("/ativos", response_model=list[FornecedorOut])
def listar_ativos(db: Session = Depends(get_db)):
    return db.query(Fornecedor).filter(Fornecedor.status.in_(STATUS_ELEGIVEL_PAGAMENTO)).all()


@router.get("/aprovados", response_model=list[FornecedorOut])
def listar_aprovados(db: Session = Depends(get_db)):
    return listar_ativos(db)


@router.get("/{fornecedor_id}", response_model=FornecedorDetalhe)
def detalhe_fornecedor(fornecedor_id: int, db: Session = Depends(get_db)):
    f = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not f:
        raise HTTPException(404, "Fornecedor não encontrado")
    historico = [
        HistoricoCadastroItem(**h) for h in obter_historico_cadastro(db, "fornecedor", f.id)
    ]
    return FornecedorDetalhe(
        id=f.id,
        cnpj=f.cnpj,
        razao_social=f.razao_social,
        banco=f.banco,
        agencia=f.agencia,
        conta=f.conta,
        status=f.status,
        motivo_rejeicao=f.motivo_rejeicao,
        created_at=f.created_at,
        historico=historico,
    )


@router.post("", response_model=FornecedorOut)
def criar(payload: FornecedorCreate, db: Session = Depends(get_db)):
    if not validar_cnpj(payload.cnpj):
        raise HTTPException(400, "CNPJ inválido")
    cnpj_fmt = formatar_cnpj(payload.cnpj)
    if db.query(Fornecedor).filter(Fornecedor.cnpj == cnpj_fmt).first():
        raise HTTPException(400, "CNPJ já cadastrado")
    f = Fornecedor(
        cnpj=cnpj_fmt,
        razao_social=payload.razao_social.strip(),
        banco=payload.banco.strip(),
        agencia=payload.agencia.strip(),
        conta=payload.conta.strip(),
        status="pendente",
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    registrar_cadastro(
        db,
        "fornecedor",
        f.id,
        "solicitacao_cadastro",
        "analista",
        {"cnpj": cnpj_fmt, "razao_social": f.razao_social},
    )
    return f


@router.patch("/{fornecedor_id}/decisao", response_model=FornecedorOut)
def decisao_gerente(
    fornecedor_id: int,
    payload: FornecedorAprovacao,
    db: Session = Depends(get_db),
):
    f = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not f:
        raise HTTPException(404, "Fornecedor não encontrado")
    if payload.aprovado:
        f.status = "ativo"
        f.motivo_rejeicao = None
        action = "fornecedor_aprovado"
    else:
        f.status = "rejeitado"
        f.motivo_rejeicao = payload.motivo_rejeicao or "Rejeitado pela gerência"
        action = "fornecedor_rejeitado"
    db.commit()
    db.refresh(f)
    registrar_cadastro(
        db,
        "fornecedor",
        f.id,
        action,
        "gerente",
        {"status": f.status, "motivo": f.motivo_rejeicao},
    )
    return f


@router.patch("/{fornecedor_id}/status", response_model=FornecedorOut)
def alterar_status(
    fornecedor_id: int,
    payload: StatusCadastroUpdate,
    db: Session = Depends(get_db),
):
    if payload.user_role != "gerente":
        raise HTTPException(403, "Somente o gerente pode ativar ou inativar cadastros.")
    f = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not f:
        raise HTTPException(404, "Fornecedor não encontrado")
    f.status = "ativo" if payload.ativo else "inativo"
    db.commit()
    db.refresh(f)
    registrar_cadastro(
        db,
        "fornecedor",
        f.id,
        "reativado" if payload.ativo else "inativado",
        "gerente",
        {"status": f.status, "motivo": payload.motivo},
    )
    return f


@router.put("/{fornecedor_id}", response_model=FornecedorOut)
def editar_direto(
    fornecedor_id: int,
    payload: FornecedorUpdate,
    user_role: str = "gerente",
    db: Session = Depends(get_db),
):
    if user_role != "gerente":
        raise HTTPException(403, "Edição direta apenas para gerente.")
    f = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not f:
        raise HTTPException(404, "Fornecedor não encontrado")
    dados = payload.model_dump(exclude_unset=True)
    for k, v in dados.items():
        if v is not None:
            setattr(f, k, v.strip() if isinstance(v, str) else v)
    db.commit()
    db.refresh(f)
    registrar_cadastro(db, "fornecedor", f.id, "edicao_direta", "gerente", dados)
    return f


@router.delete("/{fornecedor_id}", response_model=FornecedorOut)
def excluir_direto(
    fornecedor_id: int,
    user_role: str = "gerente",
    db: Session = Depends(get_db),
):
    if user_role != "gerente":
        raise HTTPException(403, "Exclusão direta apenas para gerente.")
    f = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not f:
        raise HTTPException(404, "Fornecedor não encontrado")
    f.status = "inativo"
    db.commit()
    db.refresh(f)
    registrar_cadastro(db, "fornecedor", f.id, "exclusao_direta", "gerente", {"status": "inativo"})
    return f


@router.post("/{fornecedor_id}/solicitar", response_model=dict)
def solicitar_alteracao(
    fornecedor_id: int,
    payload: CadastroSolicitacaoCreate,
    db: Session = Depends(get_db),
):
    if payload.operacao not in ("editar", "excluir"):
        raise HTTPException(400, "Operação deve ser editar ou excluir")
    f = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not f:
        raise HTTPException(404, "Fornecedor não encontrado")
    pendente = (
        db.query(CadastroSolicitacao)
        .filter(
            CadastroSolicitacao.entity_type == "fornecedor",
            CadastroSolicitacao.entity_id == fornecedor_id,
            CadastroSolicitacao.status == "pendente",
        )
        .first()
    )
    if pendente:
        raise HTTPException(400, "Já existe solicitação pendente para este fornecedor.")

    alertas = analisar_alertas_cadastro(
        f"solicitacao_{payload.operacao}", payload.dados or {}
    )
    sol = CadastroSolicitacao(
        entity_type="fornecedor",
        entity_id=fornecedor_id,
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
        "fornecedor",
        fornecedor_id,
        f"solicitacao_{payload.operacao}",
        payload.user_role,
        {"solicitacao_id": sol.id, "alertas_ia": alertas},
    )
    return {"id": sol.id, "status": "pendente", "alertas_ia": alertas}
