"""Seed de histórico (~6 meses) para demonstração nos 3 perfis, com foco em IA."""

import json
import random
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import (
    AuditLog,
    ContaBancaria,
    Fornecedor,
    MovimentoConta,
    Pagamento,
    PagamentoAnaliseIA,
    Remessa,
)

MESES_HISTORICO = 6
REM_ESSAS_POR_MES = 4
PARECER_TEMPLATE = (
    "Parecer automático (demo): beneficiário {nome}, valor R$ {valor:,.2f}. "
    "Score heurístico integrado ao XGBoost. Documentação coerente com cadastro."
)
GENAI_FRAUDE = (
    "ALERTA IA: padrão atípico de valor e beneficiário. Recomenda-se revisão documental "
    "reforçada e confirmação com área solicitante antes da liberação."
)


def _dt_mes(mes_offset: int, dia: int = 15) -> datetime:
    base = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    alvo = base - timedelta(days=30 * mes_offset + random.randint(0, 12))
    return alvo.replace(day=min(dia, 28))


def _pick_beneficiario(db, rng: random.Random):
    """PJ com fornecedor cadastrado (compatível com schema SQLite legado)."""
    f = rng.choice(db.query(Fornecedor).filter(Fornecedor.status == "ativo").all())
    despesa = "salario" if rng.random() < 0.15 else "fornecedor"
    return "pj", None, f, f.razao_social, f.cnpj, despesa


def _criar_pagamento(
    db,
    remessa_id: int,
    rng: random.Random,
    forcar_fraude: bool = False,
    created_at: datetime | None = None,
) -> Pagamento:
    tipo_ben, col, forn, nome, doc, despesa = _pick_beneficiario(db, rng)
    valor = round(rng.uniform(2_500, 85_000), 2)
    if forcar_fraude:
        valor = round(rng.uniform(180_000, 320_000), 2)

    risk = rng.uniform(0.08, 0.35)
    ml_score = rng.uniform(0.05, 0.4)
    ml_fraude = 0
    ml_motivos = None
    flags = []
    if forcar_fraude or rng.random() < 0.12:
        risk = rng.uniform(0.72, 0.95)
        ml_score = rng.uniform(0.58, 0.92)
        ml_fraude = 1
        ml_motivos = json.dumps(
            ["Valor acima do padrão histórico", "Beneficiário com alerta heurístico"],
            ensure_ascii=False,
        )
        flags = ["ALERTA: Valor fora do padrão", "Score ML elevado"]

    level = "baixo"
    if risk >= 0.7:
        level = "alto"
    elif risk >= 0.4:
        level = "medio"

    pag = Pagamento(
        remessa_id=remessa_id,
        tipo_beneficiario=tipo_ben,
        colaborador_id=col.id if col else None,
        fornecedor_id=forn.id if forn else None,
        beneficiario_nome=nome,
        beneficiario_documento=doc,
        tipo_despesa=despesa,
        competencia=None,
        valor=valor,
        documento_nome=f"NF-{rng.randint(1000,9999)}.pdf",
        risk_score=risk,
        risk_level=level,
        heuristic_flags=json.dumps(flags, ensure_ascii=False) if flags else None,
        ml_score=ml_score,
        ml_fraude_detectada=ml_fraude,
        ml_motivos=ml_motivos,
        genai_parecer=GENAI_FRAUDE if ml_fraude else PARECER_TEMPLATE.format(nome=nome, valor=valor),
        dados_conferem=0 if ml_fraude else 1,
        ia_analisado=1,
        revisado_gerente=1 if rng.random() > 0.3 else 0,
        revisado_documentos=1 if rng.random() > 0.25 else 0,
        revisado_valores=1,
        ponto_atencao_diretoria=1 if ml_fraude or risk >= 0.65 else 0,
    )
    if created_at:
        pag.created_at = created_at
    db.add(pag)
    db.flush()
    return pag


def _registrar_analise_ia(db, pag: Pagamento, versao: int, triggered: str, dt: datetime):
    rec = PagamentoAnaliseIA(
        pagamento_id=pag.id,
        versao=versao,
        triggered_by=triggered,
        risk_score=pag.risk_score,
        risk_level=pag.risk_level,
        heuristic_flags=pag.heuristic_flags,
        ml_score=pag.ml_score,
        ml_fraude_detectada=pag.ml_fraude_detectada,
        ml_motivos=pag.ml_motivos,
        genai_parecer=pag.genai_parecer,
        dados_conferem=pag.dados_conferem,
        created_at=dt,
    )
    db.add(rec)


def _audit(db, entity_type, entity_id, action, role, details, dt):
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


def _debitar_conta(db, conta: ContaBancaria, valor: float, remessa_id: int, desc: str, dt: datetime):
    """Debita até 12% do saldo por remessa — saldos finais ajustados no pós-seed."""
    debito = min(valor, conta.saldo * 0.12)
    conta.saldo = max(conta.saldo * 0.35, conta.saldo - debito)
    db.add(
        MovimentoConta(
            conta_id=conta.id,
            tipo="debito",
            valor=round(debito, 2),
            saldo_apos=conta.saldo,
            descricao=desc,
            remessa_id=remessa_id,
            created_at=dt,
        )
    )


def seed_historico_demo(force: bool = False) -> bool:
    """Popula ~6 meses de remessas. Retorna True se inseriu dados."""
    db = SessionLocal()
    rng = random.Random(42)
    try:
        if db.query(Remessa).count() > 0 and not force:
            return False

        if force:
            from app.services.limpar_dados import limpar_lancamentos

            limpar_lancamentos(db)

        contas = db.query(ContaBancaria).filter(ContaBancaria.ativa == 1).all()
        if not contas:
            return False

        titulos_base = [
            "Folha complementar",
            "Fornecedores estratégicos",
            "Serviços recorrentes",
            "Projeto expansão",
            "Manutenção predial",
            "TI e licenças",
        ]
        statuses_pool = [
            ("liberada_banco", 0.55),
            ("aguardando_gerente", 0.15),
            ("devolvida_analista", 0.1),
            ("rejeitada", 0.05),
            ("rascunho", 0.15),
        ]

        def pick_status():
            r = rng.random()
            acc = 0.0
            for st, p in statuses_pool:
                acc += p
                if r <= acc:
                    return st
            return "liberada_banco"

        remessa_idx = 0
        for mes in range(MESES_HISTORICO, 0, -1):
            for _ in range(REM_ESSAS_POR_MES):
                remessa_idx += 1
                dt_rem = _dt_mes(mes, rng.randint(5, 25))
                conta = rng.choice(contas)
                status = pick_status()
                n_pag = rng.randint(2, 6)
                forcar_fraude_rem = mes <= 2 and rng.random() < 0.25

                rem = Remessa(
                    titulo=f"{rng.choice(titulos_base)} — ciclo {mes:02d}/{dt_rem.year}",
                    conta_bancaria_id=conta.id,
                    status=status,
                    created_by="analista",
                    analise_ia_concluida=0 if status == "rascunho" else 1,
                    created_at=dt_rem,
                    updated_at=dt_rem + timedelta(hours=rng.randint(2, 48)),
                )
                db.add(rem)
                db.flush()

                _audit(
                    db,
                    "remessa",
                    rem.id,
                    "remessa_criada",
                    "analista",
                    {"titulo": rem.titulo, "pagamentos_previstos": n_pag},
                    dt_rem,
                )

                pagamentos = []
                valor_total = 0.0
                risk_max = 0.0
                for i in range(n_pag):
                    dt_pag = dt_rem + timedelta(minutes=15 * (i + 1))
                    pag = _criar_pagamento(
                        db,
                        rem.id,
                        rng,
                        forcar_fraude=forcar_fraude_rem and i == 0,
                        created_at=dt_pag,
                    )
                    pagamentos.append(pag)
                    valor_total += pag.valor
                    risk_max = max(risk_max, pag.risk_score)
                    if status != "rascunho":
                        _registrar_analise_ia(db, pag, 1, "envio_gerente", dt_pag + timedelta(minutes=5))
                        _audit(
                            db,
                            "pagamento",
                            pag.id,
                            "ia_analise_concluida",
                            "sistema",
                            {
                                "ml_score": pag.ml_score,
                                "ml_fraude": pag.ml_fraude_detectada,
                                "risk_level": pag.risk_level,
                            },
                            dt_pag + timedelta(minutes=5),
                        )

                rem.valor_total = valor_total
                rem.risk_score_max = risk_max
                rem.risk_level = (
                    "alto" if risk_max >= 0.7 else ("medio" if risk_max >= 0.4 else "baixo")
                )

                if status == "rascunho":
                    rem.analise_ia_concluida = 0
                    for p in pagamentos:
                        p.ia_analisado = 0
                        p.ml_score = 0
                        p.risk_score = 0
                        p.risk_level = "baixo"
                    continue

                dt_envio = dt_rem + timedelta(hours=1)
                rem.status = "aguardando_gerente"
                rem.analise_ia_concluida = 1
                _audit(
                    db,
                    "remessa",
                    rem.id,
                    "remessa_enviada_ia",
                    "analista",
                    {"valor_total": valor_total, "risk_max": risk_max},
                    dt_envio,
                )

                if status == "devolvida_analista":
                    rem.status = status
                    rem.motivo_devolucao = (
                        "Ajustar documentação do pagamento com maior score ML e reenviar."
                    )
                    _audit(
                        db,
                        "remessa",
                        rem.id,
                        "remessa_devolvida",
                        "gerente",
                        {"motivo": rem.motivo_devolucao},
                        dt_envio + timedelta(hours=4),
                    )
                    for idx, p0 in enumerate(pagamentos):
                        p0.valor = round(p0.valor * (0.88 if idx == 0 else 0.95), 2)
                        if idx == 0:
                            p0.ml_fraude_detectada = 0
                            p0.ml_score = 0.22
                            p0.risk_score = 0.28
                            p0.risk_level = "baixo"
                        _registrar_analise_ia(
                            db,
                            p0,
                            2,
                            "reanalise_gerente",
                            dt_envio + timedelta(hours=12 + idx * 3),
                        )
                    continue

                if status == "rejeitada":
                    rem.status = status
                    rem.gerente_justificativa = "Risco inaceitável após parecer IA."
                    _audit(
                        db,
                        "remessa",
                        rem.id,
                        "remessa_rejeitada",
                        "gerente",
                        {"justificativa": rem.gerente_justificativa},
                        dt_envio + timedelta(hours=6),
                    )
                    continue

                if status == "aguardando_gerente":
                    rem.status = status
                    _audit(
                        db,
                        "remessa",
                        rem.id,
                        "aguardando_aprovacao_gerente",
                        "gerente",
                        {"pendente": True},
                        dt_envio + timedelta(hours=2),
                    )
                    continue

                # liberada_banco
                dt_lib = dt_envio + timedelta(hours=rng.randint(8, 36))
                for p in pagamentos:
                    if (p.risk_score or 0) >= 0.45 or p.ml_fraude_detectada:
                        if rng.random() < 0.35:
                            _registrar_analise_ia(
                                db,
                                p,
                                2,
                                "reanalise_gerente",
                                dt_lib - timedelta(hours=rng.randint(2, 8)),
                            )
                rem.status = "liberada_banco"
                rem.email_auditoria = (
                    f"Auditoria remessa #{rem.id} — {len(pagamentos)} pagamentos, "
                    f"total R$ {valor_total:,.2f}"
                )
                if risk_max >= 0.7 or any(p.ml_fraude_detectada for p in pagamentos):
                    rem.gerente_justificativa = (
                        "Liberação autorizada após revisão documental e confirmação de área."
                    )
                _audit(
                    db,
                    "remessa",
                    rem.id,
                    "remessa_liberada",
                    "gerente",
                    {"valor_total": valor_total},
                    dt_lib,
                )
                _audit(
                    db,
                    "remessa",
                    rem.id,
                    "visao_diretoria",
                    "diretoria",
                    {"kpi_mes": mes, "risk_max": risk_max},
                    dt_lib + timedelta(hours=1),
                )
                _debitar_conta(
                    db,
                    conta,
                    valor_total,
                    rem.id,
                    f"Remessa #{rem.id} liberada",
                    dt_lib,
                )
                rem.updated_at = dt_lib

        # Remessa atual em análise (para gerente)
        conta_op = contas[0]
        rem_atual = Remessa(
            titulo="Remessa demonstração — aguardando gerente",
            conta_bancaria_id=conta_op.id,
            status="aguardando_gerente",
            valor_total=0,
            risk_score_max=0.55,
            risk_level="medio",
            analise_ia_concluida=1,
            created_by="analista",
            created_at=datetime.utcnow() - timedelta(days=1),
        )
        db.add(rem_atual)
        db.flush()
        total = 0.0
        for i in range(3):
            pag = _criar_pagamento(db, rem_atual.id, rng, forcar_fraude=(i == 2))
            total += pag.valor
            _registrar_analise_ia(
                db, pag, 1, "envio_gerente", datetime.utcnow() - timedelta(hours=12)
            )
        rem_atual.valor_total = total
        rem_atual.risk_score_max = max(p.risk_score for p in db.query(Pagamento).filter_by(remessa_id=rem_atual.id))

        from app.seed_auditoria import (
            ajustar_saldos_contas,
            enriquecer_pagamentos_diretoria,
            enriquecer_reanalises_gerente,
            seed_auditoria_completa,
        )

        enriquecer_pagamentos_diretoria(db)
        enriquecer_reanalises_gerente(db)
        seed_auditoria_completa(db)
        ajustar_saldos_contas(db)

        db.commit()
        return True
    finally:
        db.close()
