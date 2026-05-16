"""Histórico de cadastros com alertas para IA e auditoria."""

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditLog

STATUS_ATIVO = ("ativo", "aprovado")
STATUS_ELEGIVEL_PAGAMENTO = STATUS_ATIVO


def analisar_alertas_cadastro(
    action: str,
    dados: dict | None,
    historico_prev: list[AuditLog] | None = None,
) -> list[str]:
    alertas: list[str] = []
    if not dados:
        return alertas

    if action in ("solicitacao_edicao", "solicitacao_exclusao", "edicao_direta", "exclusao_solicitada"):
        alertas.append("ALERTA: Alteração cadastral — revisar histórico antes de pagamentos.")

    if dados.get("banco") or dados.get("agencia") or dados.get("conta"):
        if action in ("edicao_direta", "solicitacao_edicao", "colaborador_aprovado", "fornecedor_aprovado"):
            alertas.append("ALERTA: Dados bancários alterados — risco de desvio de pagamento.")

    if historico_prev:
        acoes_sensiveis = sum(
            1
            for h in historico_prev[:20]
            if h.action
            in (
                "solicitacao_edicao",
                "edicao_direta",
                "inativado",
                "solicitacao_exclusao",
                "colaborador_rejeitado",
                "fornecedor_rejeitado",
            )
        )
        if acoes_sensiveis >= 2:
            alertas.append(
                "SUSPEITA IA: Múltiplas alterações recentes no cadastro — possível fraude ou inconsistência."
            )

    if dados.get("cpf") or dados.get("cnpj"):
        alertas.append("Conferir documento (CPF/CNPJ) com base oficial.")

    if action == "inativado":
        alertas.append("Cadastro inativado — não deve aparecer em novos pagamentos.")

    if action == "reativado":
        alertas.append("Cadastro reativado — validar motivo e última alteração bancária.")

    return alertas


def registrar_cadastro(
    db: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    user_role: str,
    dados: dict | None = None,
    ip_address: str = "127.0.0.1",
) -> AuditLog:
    historico_prev = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(AuditLog.created_at.desc())
        .limit(30)
        .all()
    )
    alertas = analisar_alertas_cadastro(action, dados, historico_prev)
    payload: dict[str, Any] = dict(dados or {})
    if alertas:
        payload["alertas_ia"] = alertas
        payload["suspeita_fraude"] = any("SUSPEITA" in a or "ALERTA" in a for a in alertas)

    from app.services.audit_service import registrar

    return registrar(db, entity_type, entity_id, action, user_role, payload, ip_address)


def obter_historico_cadastro(db: Session, entity_type: str, entity_id: int) -> list[dict]:
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
        .order_by(AuditLog.created_at.desc())
        .limit(50)
        .all()
    )
    out = []
    for log in logs:
        alertas: list[str] = []
        detalhe_raw = log.details
        if detalhe_raw:
            try:
                parsed = json.loads(detalhe_raw)
                if isinstance(parsed, dict):
                    alertas = parsed.get("alertas_ia", [])
                    detalhe_raw = json.dumps(
                        {k: v for k, v in parsed.items() if k != "alertas_ia"},
                        ensure_ascii=False,
                    )
            except json.JSONDecodeError:
                pass
        out.append(
            {
                "id": log.id,
                "action": log.action,
                "user_role": log.user_role,
                "details": detalhe_raw,
                "alertas_ia": alertas,
                "suspeita": bool(alertas),
                "created_at": log.created_at,
            }
        )
    return out


def alertas_historico_para_ia(db: Session, entity_type: str, entity_id: int) -> list[str]:
    hist = obter_historico_cadastro(db, entity_type, entity_id)
    flags: list[str] = []
    for h in hist[:10]:
        for a in h.get("alertas_ia", []):
            if a not in flags:
                flags.append(a)
    return flags
