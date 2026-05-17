"""Auditoria e histórico de cadastros — 6 meses para Diretoria e relatórios."""

import json
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import AuditLog, Colaborador, Fornecedor, Pagamento

ACOES_REMESSA = [
    ("remessa_criada", "analista"),
    ("remessa_enviada_ia", "analista"),
    ("ia_analise_concluida", "sistema"),
    ("aguardando_aprovacao_gerente", "gerente"),
    ("remessa_liberada", "gerente"),
    ("visao_diretoria", "diretoria"),
    ("remessa_devolvida", "gerente"),
    ("remessa_rejeitada", "gerente"),
]

ACOES_CADASTRO = [
    ("fornecedor_cadastrado", "analista", "fornecedor"),
    ("fornecedor_aprovado", "gerente", "fornecedor"),
    ("fornecedor_pendente", "analista", "fornecedor"),
    ("colaborador_cadastrado", "analista", "colaborador"),
    ("colaborador_aprovado", "gerente", "colaborador"),
    ("solicitacao_edicao", "analista", "fornecedor"),
    ("edicao_direta", "gerente", "fornecedor"),
    ("inativado", "gerente", "colaborador"),
    ("reativado", "gerente", "colaborador"),
    ("alerta_ia_cadastro", "sistema", "fornecedor"),
]


def _log(
    db: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    role: str,
    details: dict | None,
    dt: datetime,
):
    db.add(
        AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_role=role,
            details=json.dumps(details, ensure_ascii=False) if details else None,
            created_at=dt,
        )
    )


def seed_auditoria_completa(db: Session) -> int:
    """Gera histórico de cadastros (6 meses) e complementa trilha WORM."""
    if db.query(AuditLog).filter(AuditLog.action == "fornecedor_aprovado").count() > 8:
        return 0

    rng = random.Random(99)
    base = datetime.utcnow()
    inseridos = 0

    for mes in range(6, 0, -1):
        dt_mes = base - timedelta(days=30 * mes)
        for action, role, etype in rng.sample(ACOES_CADASTRO, k=min(4, len(ACOES_CADASTRO))):
            if etype == "fornecedor":
                ent = rng.choice(db.query(Fornecedor).limit(8).all() or [None])
            else:
                ent = rng.choice(db.query(Colaborador).limit(8).all() or [None])
            if not ent:
                continue
            _log(
                db,
                etype,
                ent.id,
                action,
                role,
                {
                    "mes": mes,
                    "nome": getattr(ent, "razao_social", None) or getattr(ent, "nome_completo", ""),
                    "alertas_ia": ["Conferir dados bancários"] if "edicao" in action else [],
                },
                dt_mes + timedelta(days=rng.randint(1, 20)),
            )
            inseridos += 1

    db.commit()
    return inseridos


def ajustar_saldos_contas(db: Session) -> None:
    """Garante saldos operacionais realistas após débitos do seed."""
    from app.models import ContaBancaria

    alvos = {
        1: 1_180_000.0,
        2: 355_000.0,
        3: 590_000.0,
    }
    for conta in db.query(ContaBancaria).filter(ContaBancaria.ativa == 1).all():
        if conta.id in alvos:
            conta.saldo = alvos[conta.id]
        elif conta.saldo < 50_000:
            conta.saldo = 420_000.0
    db.commit()


def enriquecer_pagamentos_diretoria(db: Session) -> int:
    """Marca revisões, pontos de atenção e casos não cadastrados para painéis."""
    rng = random.Random(77)
    pags = db.query(Pagamento).all()
    n = 0
    fornecedores_pend = (
        db.query(Fornecedor).filter(Fornecedor.status == "pendente").all()
    )
    for i, pag in enumerate(pags):
        if pag.ia_analisado and rng.random() < 0.35:
            pag.revisado_gerente = 1
            pag.revisado_documentos = 1
            pag.revisado_valores = 1
            pag.revisado_observacao = "Conferido pelo gerente — documentação e valores OK."
            pag.ponto_atencao_diretoria = 1
            n += 1
        if pag.ml_fraude_detectada or (pag.risk_score or 0) >= 0.65:
            pag.ponto_atencao_diretoria = 1
            n += 1
        if fornecedores_pend and i % 17 == 0:
            f = fornecedores_pend[0]
            pag.fornecedor_id = f.id
            pag.fornecedor_nao_cadastrado = 1
            pag.beneficiario_nome = f.razao_social
            pag.beneficiario_documento = f.cnpj
            pag.risk_score = max(pag.risk_score or 0, 0.55)
            pag.risk_level = "medio"
            n += 1
        if i % 23 == 0:
            pag.tipo_beneficiario = "pf"
            pag.pf_nao_cadastrado = 1
            pag.beneficiario_nome = "Prestador Externo Demo"
            pag.beneficiario_documento = "999.888.777-66"
            pag.risk_score = max(pag.risk_score or 0, 0.52)
            n += 1
    db.commit()
    return n
