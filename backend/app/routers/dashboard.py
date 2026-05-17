from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, ContaBancaria, Fornecedor, Pagamento, PagamentoAnaliseIA, Remessa
from app.schemas import AuditLogOut, DashboardKPIs, PontoAtencaoOut
from app.services.dashboard_historico import historico_controle_ia
from app.services.dashboard_ia_metrics import metricas_ia_diretoria
from app.services.pagamento_out import build_pagamento_out

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=DashboardKPIs)
def kpis(db: Session = Depends(get_db)):
    total_remessas = db.query(Remessa).count()
    total_pagamentos = db.query(Pagamento).count()
    aprovadas = (
        db.query(Remessa).filter(Remessa.status.in_(["aprovada", "liberada_banco"])).all()
    )
    valor_aprovado = 0.0
    for r in aprovadas:
        valor_aprovado += sum(
            p.valor
            for p in db.query(Pagamento).filter(Pagamento.remessa_id == r.id).all()
        )
    valor_bloqueado = (
        db.query(func.coalesce(func.sum(Pagamento.valor), 0))
        .filter(Pagamento.risk_level == "alto")
        .scalar()
        or 0
    )
    fraudes = db.query(Pagamento).filter(
        (Pagamento.risk_score >= 0.7) | (Pagamento.ml_fraude_detectada == 1)
    ).count()
    nao_cad = db.query(Pagamento).filter(Pagamento.fornecedor_nao_cadastrado == 1).count()
    pf_nao_cad = db.query(Pagamento).filter(Pagamento.pf_nao_cadastrado == 1).count()
    saldo_total = (
        db.query(func.coalesce(func.sum(ContaBancaria.saldo), 0)).scalar() or 0
    )

    return DashboardKPIs(
        total_remessas=total_remessas,
        total_pagamentos=total_pagamentos,
        valor_total_aprovado=float(valor_aprovado),
        valor_bloqueado_ia=float(valor_bloqueado),
        fraudes_detectadas=fraudes,
        tempo_medio_aprovacao_horas=4.5,
        pagamentos_nao_cadastrados=nao_cad,
        pagamentos_pf_nao_cadastrados=pf_nao_cad,
        saldo_total_contas=float(saldo_total),
    )


@router.get("/auditoria", response_model=list[AuditLogOut])
def logs_auditoria(db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()


@router.get("/metricas-ia")
def metricas_ia_endpoint(db: Session = Depends(get_db), meses: int = 6):
    """Gráficos executivos: detecções IA por perfil, mês e tipo."""
    return metricas_ia_diretoria(db, meses=min(max(meses, 3), 12))


@router.get("/historico-controle-ia")
def historico_controle_ia_endpoint(db: Session = Depends(get_db), limit: int = 150):
    """
    Histórico completo para a Diretoria: detecções IA + fluxo Analista/Gerente/Sistema
    por pagamento, com linha do tempo e versões de reanálise.
    """
    return historico_controle_ia(db, limit=min(limit, 300))


@router.get("/deteccoes-ia")
def deteccoes_ia(db: Session = Depends(get_db)):
    """Detecções da IA para a diretoria (após análise no envio ao gerente)."""
    pagamentos = (
        db.query(Pagamento)
        .filter(
            Pagamento.ia_analisado == 1,
            (Pagamento.ml_fraude_detectada == 1)
            | (Pagamento.risk_score >= 0.4)
            | (Pagamento.fornecedor_nao_cadastrado == 1)
            | (Pagamento.pf_nao_cadastrado == 1),
        )
        .order_by(Pagamento.created_at.desc())
        .limit(150)
        .all()
    )
    result = []
    for p in pagamentos:
        rem = db.query(Remessa).filter(Remessa.id == p.remessa_id).first()
        historico = (
            db.query(PagamentoAnaliseIA)
            .filter(PagamentoAnaliseIA.pagamento_id == p.id)
            .order_by(PagamentoAnaliseIA.versao.desc())
            .all()
        )
        result.append(
            {
                "pagamento_id": p.id,
                "codigo_pagamento": f"PAY-{p.id:06d}",
                "remessa_id": p.remessa_id,
                "remessa_titulo": rem.titulo if rem else None,
                "remessa_status": rem.status if rem else None,
                "valor": p.valor,
                "beneficiario_nome": p.beneficiario_nome,
                "risk_score": p.risk_score,
                "risk_level": p.risk_level,
                "ml_fraude_detectada": bool(p.ml_fraude_detectada),
                "ml_motivos": p.ml_motivos,
                "genai_parecer": p.genai_parecer,
                "gerente_justificativa": rem.gerente_justificativa if rem else None,
                "motivo_devolucao": rem.motivo_devolucao if rem else None,
                "revisado_observacao": p.revisado_observacao,
                "historico_analises": [
                    {
                        "versao": h.versao,
                        "triggered_by": h.triggered_by,
                        "ml_fraude_detectada": bool(h.ml_fraude_detectada),
                        "ml_score": h.ml_score,
                        "risk_level": h.risk_level,
                        "genai_parecer": h.genai_parecer,
                        "created_at": h.created_at.isoformat(),
                    }
                    for h in historico
                ],
            }
        )
    return result


@router.get("/alertas")
def alertas_fraude(db: Session = Depends(get_db)):
    pagamentos = (
        db.query(Pagamento)
        .filter(
            Pagamento.ia_analisado == 1,
            (Pagamento.risk_score >= 0.4)
            | (Pagamento.fornecedor_nao_cadastrado == 1)
            | (Pagamento.pf_nao_cadastrado == 1)
            | (Pagamento.ml_fraude_detectada == 1),
        )
        .order_by(Pagamento.risk_score.desc())
        .limit(30)
        .all()
    )
    result = []
    for p in pagamentos:
        f = db.query(Fornecedor).filter(Fornecedor.id == p.fornecedor_id).first()
        result.append(
            {
                "id": p.id,
                "remessa_id": p.remessa_id,
                "valor": p.valor,
                "risk_score": p.risk_score,
                "risk_level": p.risk_level,
                "genai_parecer": p.genai_parecer,
                "heuristic_flags": p.heuristic_flags,
                "fornecedor_nao_cadastrado": bool(p.fornecedor_nao_cadastrado),
                "pf_nao_cadastrado": bool(p.pf_nao_cadastrado),
                "tipo_despesa": p.tipo_despesa,
                "competencia": p.competencia,
                "beneficiario_nome": p.beneficiario_nome,
                "beneficiario_documento": p.beneficiario_documento,
                "ml_fraude_detectada": bool(p.ml_fraude_detectada),
                "ml_motivos": p.ml_motivos,
                "fornecedor_razao_social": f.razao_social if f else p.beneficiario_nome,
                "fornecedor_status": f.status if f else None,
            }
        )
    return result


@router.get("/pagamentos-pf-nao-cadastrados")
def pagamentos_pf_nao_cadastrados(db: Session = Depends(get_db)):
    pagamentos = (
        db.query(Pagamento)
        .filter(Pagamento.pf_nao_cadastrado == 1)
        .order_by(Pagamento.created_at.desc())
        .limit(50)
        .all()
    )
    out = []
    for p in pagamentos:
        rem = db.query(Remessa).filter(Remessa.id == p.remessa_id).first()
        out.append(
            {
                "pagamento_id": p.id,
                "remessa_id": p.remessa_id,
                "remessa_status": rem.status if rem else None,
                "nome": p.beneficiario_nome,
                "cpf": p.beneficiario_documento,
                "valor": p.valor,
                "tipo_despesa": p.tipo_despesa,
                "competencia": p.competencia,
                "risk_score": p.risk_score,
                "gerente_justificativa": rem.gerente_justificativa if rem else None,
                "genai_parecer": p.genai_parecer,
            }
        )
    return out


@router.get("/pagamentos-nao-cadastrados")
def pagamentos_nao_cadastrados(db: Session = Depends(get_db)):
    pagamentos = (
        db.query(Pagamento)
        .filter(Pagamento.fornecedor_nao_cadastrado == 1)
        .order_by(Pagamento.created_at.desc())
        .limit(50)
        .all()
    )
    out = []
    for p in pagamentos:
        f = db.query(Fornecedor).filter(Fornecedor.id == p.fornecedor_id).first()
        rem = db.query(Remessa).filter(Remessa.id == p.remessa_id).first()
        out.append(
            {
                "pagamento_id": p.id,
                "remessa_id": p.remessa_id,
                "remessa_status": rem.status if rem else None,
                "valor": p.valor,
                "fornecedor": f.razao_social if f else None,
                "cnpj": f.cnpj if f else None,
                "status_fornecedor": f.status if f else None,
                "risk_score": p.risk_score,
                "gerente_justificativa": rem.gerente_justificativa if rem else None,
                "genai_parecer": p.genai_parecer,
            }
        )
    return out


@router.get("/pontos-atencao", response_model=list[PontoAtencaoOut])
def pontos_atencao(db: Session = Depends(get_db)):
    pagamentos = (
        db.query(Pagamento)
        .filter(Pagamento.ponto_atencao_diretoria == 1)
        .order_by(Pagamento.created_at.desc())
        .limit(80)
        .all()
    )
    out = []
    for p in pagamentos:
        rem = db.query(Remessa).filter(Remessa.id == p.remessa_id).first()
        out.append(
            PontoAtencaoOut(
                pagamento_id=p.id,
                remessa_id=p.remessa_id,
                remessa_status=rem.status if rem else None,
                remessa_titulo=rem.titulo if rem else None,
                tipo_beneficiario=p.tipo_beneficiario or "pj",
                tipo_despesa=p.tipo_despesa or "fornecedor",
                beneficiario_nome=p.beneficiario_nome,
                beneficiario_documento=p.beneficiario_documento,
                valor=p.valor,
                revisado_gerente=bool(p.revisado_gerente),
                revisado_observacao=p.revisado_observacao,
                gerente_justificativa=rem.gerente_justificativa if rem else None,
                risk_score=p.risk_score,
                risk_level=p.risk_level,
                ml_fraude_detectada=bool(p.ml_fraude_detectada),
                pf_nao_cadastrado=bool(p.pf_nao_cadastrado),
                fornecedor_nao_cadastrado=bool(p.fornecedor_nao_cadastrado),
            )
        )
    return out


@router.get("/pagamentos/{pagamento_id}/detalhe")
def pagamento_detalhe_executivo(pagamento_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException

    p = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not p:
        raise HTTPException(404, "Pagamento não encontrado")
    rem = db.query(Remessa).filter(Remessa.id == p.remessa_id).first()
    return {
        "pagamento": build_pagamento_out(db, p),
        "remessa": {
            "id": rem.id if rem else p.remessa_id,
            "titulo": rem.titulo if rem else None,
            "status": rem.status if rem else None,
            "gerente_justificativa": rem.gerente_justificativa if rem else None,
        },
    }
