import json
from sqlalchemy.orm import Session

from app.models import AuditLog


def registrar(
    db: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    user_role: str,
    details: dict | None = None,
    ip_address: str = "127.0.0.1",
):
    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_role=user_role,
        ip_address=ip_address,
        details=json.dumps(details, ensure_ascii=False) if details else None,
    )
    db.add(log)
    db.commit()
    return log


def gerar_email_auditoria(remessa, pagamentos, fornecedores_map) -> str:
    linhas = [
        "=== E-MAIL DE AUDITORIA - LIBERAÇÃO BANCÁRIA ===",
        f"Remessa #{remessa.id}: {remessa.titulo}",
        f"Status: {remessa.status}",
        f"Risco máximo: {remessa.risk_score_max:.0%} ({remessa.risk_level})",
        "",
        "RESUMO DOS PAGAMENTOS:",
    ]
    for p in pagamentos:
        f = fornecedores_map.get(p.fornecedor_id) if p.fornecedor_id else None
        nome = p.beneficiario_nome or (f.razao_social if f else "N/A")
        doc = p.beneficiario_documento or (f.cnpj if f else "")
        extra = ""
        if getattr(p, "tipo_despesa", None) == "salario" and getattr(p, "competencia", None):
            extra = f" | Salário competência {p.competencia}"
        if getattr(p, "pf_nao_cadastrado", 0):
            extra += " | ALERTA PF NÃO CADASTRADO"
        linhas.append(
            f"  - {nome} ({doc}): R$ {p.valor:,.2f} | Risco {p.risk_score:.0%}{extra}"
        )
        if p.genai_parecer:
            linhas.append(f"    Parecer IA: {p.genai_parecer[:200]}...")
    linhas.extend(
        [
            "",
            "Trilha imutável registrada no sistema (WORM).",
            "Destinatários: auditoria@empresa.com; diretoria@empresa.com",
        ]
    )
    return "\n".join(linhas)
