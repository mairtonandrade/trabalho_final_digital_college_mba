"""Histórico executivo: detecções IA + fluxo analista/gerente para a Diretoria."""

import json
from sqlalchemy.orm import Session

from app.models import AuditLog, Pagamento, PagamentoAnaliseIA, Remessa

ACAO_LABEL = {
    "remessa_criada": "Remessa criada (Analista)",
    "remessa_enviada_ia": "Envio para análise IA em lote (Analista)",
    "ia_analise_concluida": "Análise IA concluída — ML + GenAI (Sistema)",
    "aguardando_aprovacao_gerente": "Aguardando revisão do Gerente",
    "remessa_liberada": "Remessa liberada para banco (Gerente)",
    "remessa_devolvida": "Devolvida ao Analista para correção (Gerente)",
    "remessa_rejeitada": "Remessa rejeitada (Gerente)",
    "visao_diretoria": "Registro de acompanhamento (Diretoria)",
    "catalogo_fraude_registrado": "Cenário de fraude catalogado (Sistema)",
    "fornecedor_cadastrado": "Cadastro de fornecedor (Analista)",
    "fornecedor_aprovado": "Fornecedor aprovado na whitelist (Gerente)",
    "colaborador_aprovado": "Colaborador aprovado (Gerente)",
    "solicitacao_edicao": "Solicitação de alteração cadastral (Analista)",
}


def _parse_details(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"texto": raw}


def _eventos_fluxo(db: Session, remessa_id: int, pagamento_id: int) -> list[dict]:
    logs_rem = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == "remessa", AuditLog.entity_id == remessa_id)
        .order_by(AuditLog.created_at.asc())
        .all()
    )
    logs_pag = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == "pagamento", AuditLog.entity_id == pagamento_id)
        .order_by(AuditLog.created_at.asc())
        .all()
    )
    eventos = []
    for log in list(logs_rem) + list(logs_pag):
        det = _parse_details(log.details)
        eventos.append(
            {
                "data": log.created_at.isoformat() if log.created_at else None,
                "perfil": log.user_role,
                "acao": log.action,
                "acao_label": ACAO_LABEL.get(log.action, log.action.replace("_", " ").title()),
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "detalhes": det,
            }
        )
    eventos.sort(key=lambda e: e["data"] or "")
    return eventos


def historico_controle_ia(db: Session, limit: int = 150) -> dict:
    """Todos os pagamentos com IA analisada + linha do tempo do fluxo financeiro."""
    pagamentos = (
        db.query(Pagamento)
        .filter(Pagamento.ia_analisado == 1)
        .order_by(Pagamento.created_at.desc())
        .limit(limit)
        .all()
    )

    itens = []
    fraudes = 0
    por_perfil_evento: dict[str, int] = {}

    for p in pagamentos:
        rem = db.query(Remessa).filter(Remessa.id == p.remessa_id).first()
        analises = (
            db.query(PagamentoAnaliseIA)
            .filter(PagamentoAnaliseIA.pagamento_id == p.id)
            .order_by(PagamentoAnaliseIA.versao.asc())
            .all()
        )
        eventos = _eventos_fluxo(db, p.remessa_id, p.id)
        for ev in eventos:
            por_perfil_evento[ev["perfil"]] = por_perfil_evento.get(ev["perfil"], 0) + 1

        if p.ml_fraude_detectada:
            fraudes += 1

        ml_motivos = p.ml_motivos
        if ml_motivos and ml_motivos.startswith("["):
            try:
                ml_motivos = ", ".join(json.loads(ml_motivos))
            except json.JSONDecodeError:
                pass

        itens.append(
            {
                "pagamento_id": p.id,
                "codigo_pagamento": f"PAY-{p.id:06d}",
                "remessa_id": p.remessa_id,
                "remessa_titulo": rem.titulo if rem else None,
                "remessa_status": rem.status if rem else None,
                "valor": p.valor,
                "beneficiario_nome": p.beneficiario_nome,
                "beneficiario_documento": p.beneficiario_documento,
                "tipo_beneficiario": p.tipo_beneficiario,
                "tipo_despesa": p.tipo_despesa,
                "risk_score": p.risk_score,
                "risk_level": p.risk_level,
                "ml_score": p.ml_score,
                "ml_fraude_detectada": bool(p.ml_fraude_detectada),
                "ml_motivos": ml_motivos,
                "genai_parecer": p.genai_parecer,
                "heuristic_flags": p.heuristic_flags,
                "fornecedor_nao_cadastrado": bool(p.fornecedor_nao_cadastrado),
                "pf_nao_cadastrado": bool(p.pf_nao_cadastrado),
                "dados_conferem": bool(p.dados_conferem),
                "revisado_gerente": bool(p.revisado_gerente),
                "revisado_observacao": p.revisado_observacao,
                "gerente_justificativa": rem.gerente_justificativa if rem else None,
                "motivo_devolucao": rem.motivo_devolucao if rem else None,
                "ponto_atencao_diretoria": bool(p.ponto_atencao_diretoria),
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "analises_ia": [
                    {
                        "id": a.id,
                        "versao": a.versao,
                        "triggered_by": a.triggered_by,
                        "triggered_label": _triggered_label(a.triggered_by),
                        "risk_score": a.risk_score,
                        "risk_level": a.risk_level,
                        "ml_score": a.ml_score,
                        "ml_fraude_detectada": bool(a.ml_fraude_detectada),
                        "ml_motivos": a.ml_motivos,
                        "genai_parecer": a.genai_parecer,
                        "dados_conferem": bool(a.dados_conferem),
                        "created_at": a.created_at.isoformat() if a.created_at else None,
                    }
                    for a in analises
                ],
                "eventos_fluxo": eventos,
            }
        )

    return {
        "resumo": {
            "total_registros": len(itens),
            "fraudes_ml": fraudes,
            "eventos_por_perfil": por_perfil_evento,
        },
        "itens": itens,
    }


def _triggered_label(triggered: str) -> str:
    return {
        "envio_gerente": "Envio da remessa ao gerente (Analista)",
        "reanalise_gerente": "Reanálise solicitada pelo Gerente",
        "catalogo_mba": "Catálogo de demonstração MBA",
    }.get(triggered, triggered.replace("_", " ").title())
