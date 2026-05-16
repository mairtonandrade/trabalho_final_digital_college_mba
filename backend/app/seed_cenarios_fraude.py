"""
Catálogo de demonstração: todos os tipos de detecção do motor ML + heurísticas + GenAI.
Uma remessa dedicada com pagamentos rotulados, justificados e visíveis no Gerente/Diretoria.
"""

import json
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import (
    AuditLog,
    Colaborador,
    ContaBancaria,
    Fornecedor,
    Pagamento,
    PagamentoAnaliseIA,
    Remessa,
)

TITULO_CATALOGO = "Catálogo MBA — Todos os tipos de detecção IA"
TITULO_CATALOGO_LIBERADO = "Catálogo MBA — Casos resolvidos (histórico)"


def _motivos_json(items: list[str]) -> str:
    return json.dumps(items, ensure_ascii=False)


def _parecer(codigo: str, nome: str, valor: float, nivel: str) -> str:
    return (
        f"[Parecer IA — {codigo} | Risco {nivel}]\n"
        f"Beneficiário: {nome}. Valor: R$ {valor:,.2f}.\n"
        f"Cenário de demonstração do catálogo anti-fraude MBA. "
        f"Revisão gerencial obrigatória antes da liberação."
    )


def _pagamento_catalogo(
    db,
    remessa_id: int,
    *,
    codigo: str,
    nome: str,
    documento: str,
    valor: float,
    tipo_ben: str,
    fornecedor_id: int | None,
    colaborador_id: int | None,
    tipo_despesa: str,
    flags: list[str],
    ml_score: float,
    ml_fraude: int,
    ml_motivos: list[str],
    risk_score: float,
    risk_level: str,
    genai: str,
    dados_conferem: int,
    fornecedor_nao_cad: int = 0,
    pf_nao_cad: int = 0,
    documento_nome: str = "NF-catalogo-ok.pdf",
    dt: datetime,
) -> Pagamento:
    pag = Pagamento(
        remessa_id=remessa_id,
        tipo_beneficiario=tipo_ben,
        fornecedor_id=fornecedor_id,
        colaborador_id=colaborador_id,
        beneficiario_nome=nome,
        beneficiario_documento=documento,
        tipo_despesa=tipo_despesa,
        valor=valor,
        documento_nome=documento_nome,
        fornecedor_nao_cadastrado=fornecedor_nao_cad,
        pf_nao_cadastrado=pf_nao_cad,
        risk_score=risk_score,
        risk_level=risk_level,
        heuristic_flags=json.dumps(flags, ensure_ascii=False),
        ml_score=ml_score,
        ml_fraude_detectada=ml_fraude,
        ml_motivos=_motivos_json(ml_motivos),
        genai_parecer=genai,
        dados_conferem=dados_conferem,
        ia_analisado=1,
        revisado_gerente=0,
        revisado_documentos=0,
        revisado_valores=0,
        ponto_atencao_diretoria=1,
        created_at=dt,
    )
    db.add(pag)
    db.flush()
    db.add(
        PagamentoAnaliseIA(
            pagamento_id=pag.id,
            versao=1,
            triggered_by="catalogo_mba",
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
    )
    db.add(
        AuditLog(
            entity_type="pagamento",
            entity_id=pag.id,
            action="catalogo_fraude_registrado",
            user_role="sistema",
            details=json.dumps(
                {"codigo_cenario": codigo, "ml_fraude": ml_fraude, "motivos": ml_motivos},
                ensure_ascii=False,
            ),
            created_at=dt,
        )
    )
    return pag


def _montar_cenarios(db) -> list[dict]:
    ativos = db.query(Fornecedor).filter(Fornecedor.status == "ativo").all()
    pendentes = db.query(Fornecedor).filter(Fornecedor.status == "pendente").all()
    cols = db.query(Colaborador).filter(Colaborador.status == "ativo").all()
    conta = db.query(ContaBancaria).filter(ContaBancaria.ativa == 1).first()
    saldo = conta.saldo if conta else 500_000.0

    f_ativo = ativos[0] if ativos else None
    f_pendente = pendentes[0] if pendentes else None
    f_velocity = ativos[1] if len(ativos) > 1 else f_ativo
    col = cols[0] if cols else None

    if not f_ativo:
        return []

    base = datetime.utcnow() - timedelta(days=2)
    cenarios = []

    def add(**kwargs):
        cenarios.append(kwargs)

    # 1 — XGBoost / ML fraude
    add(
        codigo="ML_XGBOOST_FRAUDE",
        nome=f_ativo.razao_social,
        documento=f_ativo.cnpj,
        valor=287_500.0,
        tipo_ben="pj",
        fornecedor_id=f_ativo.id,
        colaborador_id=None,
        tipo_despesa="fornecedor",
        flags=["ALERTA: Score ML acima do limiar operacional (55%)"],
        ml_score=0.82,
        ml_fraude=1,
        ml_motivos=[
            "Modelo XGBoost classificou FRAUDE (probabilidade 82%).",
            "Score ML 82% ≥ limiar 55% → suspeita de fraude.",
            "Valor elevado: R$ 287.500,00 acima do padrão operacional.",
        ],
        risk_score=0.88,
        risk_level="alto",
        dados_conferem=1,
        documento_nome="NF-287500-ok.pdf",
    )

    # 2 — Valor elevado (>150k regra ML)
    add(
        codigo="ML_VALOR_ELEVADO",
        nome=ativos[2].razao_social if len(ativos) > 2 else f_ativo.razao_social,
        documento=ativos[2].cnpj if len(ativos) > 2 else f_ativo.cnpj,
        valor=168_000.0,
        tipo_ben="pj",
        fornecedor_id=ativos[2].id if len(ativos) > 2 else f_ativo.id,
        colaborador_id=None,
        tipo_despesa="fornecedor",
        flags=["Valor acima do padrão histórico da operação"],
        ml_score=0.61,
        ml_fraude=1,
        ml_motivos=[
            "Valor elevado: R$ 168.000,00 acima do padrão operacional.",
            "Score ML 61% ≥ limiar 55% → suspeita de fraude.",
        ],
        risk_score=0.72,
        risk_level="alto",
        dados_conferem=1,
    )

    # 3 — Heurística limite R$ 200.000
    add(
        codigo="HEU_VALOR_LIMITE_200K",
        nome=ativos[3].razao_social if len(ativos) > 3 else f_ativo.razao_social,
        documento=ativos[3].cnpj if len(ativos) > 3 else f_ativo.cnpj,
        valor=215_000.0,
        tipo_ben="pj",
        fornecedor_id=ativos[3].id if len(ativos) > 3 else f_ativo.id,
        colaborador_id=None,
        tipo_despesa="fornecedor",
        flags=["Valor acima do limite operacional padrão (R$ 200.000)"],
        ml_score=0.58,
        ml_fraude=1,
        ml_motivos=[
            "Regra heurística: Valor acima do limite operacional padrão (R$ 200.000).",
            "Score ML 58% ≥ limiar 55% → suspeita de fraude.",
        ],
        risk_score=0.75,
        risk_level="alto",
        dados_conferem=1,
    )

    # 4 — Liquidez / % do saldo da conta
    pct = 0.48
    valor_liq = round(saldo * pct, 2)
    add(
        codigo="ML_RISCO_LIQUIDEZ_SALDO",
        nome=f_ativo.razao_social,
        documento=f_ativo.cnpj,
        valor=valor_liq,
        tipo_ben="pj",
        fornecedor_id=f_ativo.id,
        colaborador_id=None,
        tipo_despesa="fornecedor",
        flags=[f"Pagamento consome {pct:.0%} do saldo da conta — risco de liquidez"],
        ml_score=0.57,
        ml_fraude=1,
        ml_motivos=[
            f"Pagamento consome {pct:.0%} do saldo da conta — risco de liquidez.",
            "Score ML 57% ≥ limiar 55% → suspeita de fraude.",
        ],
        risk_score=0.68,
        risk_level="alto",
        dados_conferem=1,
    )

    # 5 — Benford / valor atípico
    add(
        codigo="HEU_BENFORD_ATIPICO",
        nome=ativos[4].razao_social if len(ativos) > 4 else f_ativo.razao_social,
        documento=ativos[4].cnpj if len(ativos) > 4 else f_ativo.cnpj,
        valor=12_345.67,
        tipo_ben="pj",
        fornecedor_id=ativos[4].id if len(ativos) > 4 else f_ativo.id,
        colaborador_id=None,
        tipo_despesa="fornecedor",
        flags=["Valor com padrão atípico (Benford/heurística)"],
        ml_score=0.42,
        ml_fraude=0,
        ml_motivos=[
            "Regra heurística: Valor com padrão atípico (Benford/heurística).",
        ],
        risk_score=0.48,
        risk_level="medio",
        dados_conferem=1,
    )

    # 6 — Fornecedor não cadastrado (whitelist)
    if f_pendente:
        add(
            codigo="REGRA_FORNECEDOR_NAO_CAD",
            nome=f_pendente.razao_social,
            documento=f_pendente.cnpj,
            valor=8_500.0,
            tipo_ben="pj",
            fornecedor_id=f_pendente.id,
            colaborador_id=None,
            tipo_despesa="fornecedor",
            flags=["ALERTA: Fornecedor PJ NÃO CADASTRADO na whitelist."],
            ml_score=0.52,
            ml_fraude=0,
            ml_motivos=[
                "Beneficiário PJ fora da whitelist de fornecedores.",
                "Regra heurística: ALERTA: Fornecedor PJ NÃO CADASTRADO na whitelist.",
            ],
            risk_score=0.62,
            risk_level="medio",
            dados_conferem=1,
            fornecedor_nao_cad=1,
        )

    # 7 — PF não cadastrado
    add(
        codigo="REGRA_PF_NAO_CAD",
        nome="Prestador Autônomo Externo",
        documento="999.888.777-66",
        valor=7_200.0,
        tipo_ben="pf",
        fornecedor_id=f_ativo.id,
        colaborador_id=None,
        tipo_despesa="outros",
        flags=["ALERTA: PF com CPF NÃO CADASTRADO como colaborador."],
        ml_score=0.48,
        ml_fraude=0,
        ml_motivos=[
            "CPF não cadastrado como colaborador no RH.",
            "Regra heurística: ALERTA: PF com CPF NÃO CADASTRADO como colaborador.",
        ],
        risk_score=0.58,
        risk_level="medio",
        dados_conferem=1,
        pf_nao_cad=1,
    )

    # 8 — Salário atípico
    if col:
        add(
            codigo="ML_SALARIO_ATIPICO",
            nome=col.nome_completo,
            documento=col.cpf,
            valor=62_000.0,
            tipo_ben="pf",
            fornecedor_id=f_ativo.id,
            colaborador_id=col.id,
            tipo_despesa="salario",
            flags=["Despesa de SALÁRIO — competência 04/2026"],
            ml_score=0.56,
            ml_fraude=1,
            ml_motivos=[
                "Salário com valor atípico para validação de competência.",
                "Score ML 56% ≥ limiar 55% → suspeita de fraude.",
            ],
            risk_score=0.55,
            risk_level="medio",
            dados_conferem=1,
            documento_nome="holerite-042026.pdf",
        )

    # 9 — Documento não confere (OCR simulado)
    add(
        codigo="GENAI_DOCUMENTO_DIVERGENTE",
        nome=f_ativo.razao_social,
        documento=f_ativo.cnpj,
        valor=34_000.0,
        tipo_ben="pj",
        fornecedor_id=f_ativo.id,
        colaborador_id=None,
        tipo_despesa="fornecedor",
        flags=["Cruzamento documental: anexo NÃO CONFEREM com cadastro"],
        ml_score=0.38,
        ml_fraude=0,
        ml_motivos=[
            "Dados do documento não conferem com o cadastro (simulação OCR).",
            "Arquivo contém indicador 'fake' — possível fraude documental.",
        ],
        risk_score=0.52,
        risk_level="medio",
        dados_conferem=0,
        documento_nome="nf-fake-documento.pdf",
    )

    # 10 — Razão social incompleta
    add(
        codigo="HEU_RAZAO_SOCIAL_INCOMPLETA",
        nome="ABC",
        documento="11.111.111/0001-11",
        valor=15_000.0,
        tipo_ben="pj",
        fornecedor_id=f_ativo.id,
        colaborador_id=None,
        tipo_despesa="fornecedor",
        flags=["Razão social incompleta"],
        ml_score=0.35,
        ml_fraude=0,
        ml_motivos=["Regra heurística: Razão social incompleta."],
        risk_score=0.42,
        risk_level="medio",
        dados_conferem=1,
        fornecedor_nao_cad=1,
    )

    # 11–12 — Velocity (2 pagamentos prévios + 3º no catálogo)
    if f_velocity:
        for i, v in enumerate([38_000.0, 42_000.0], start=1):
            add(
                codigo=f"HEU_VELOCITY_PRE_{i}",
                nome=f_velocity.razao_social,
                documento=f_velocity.cnpj,
                valor=v,
                tipo_ben="pj",
                fornecedor_id=f_velocity.id,
                colaborador_id=None,
                tipo_despesa="fornecedor",
                flags=[f"Velocity: {i}º pagamento ao mesmo fornecedor no dia (pré-catálogo)"],
                ml_score=0.28 + i * 0.05,
                ml_fraude=0,
                ml_motivos=[f"Velocity rule: pagamento {i} de 3 no mesmo dia."],
                risk_score=0.35 + i * 0.08,
                risk_level="medio",
                dados_conferem=1,
            )
        add(
            codigo="HEU_VELOCITY_3O_PAGAMENTO",
            nome=f_velocity.razao_social,
            documento=f_velocity.cnpj,
            valor=41_500.0,
            tipo_ben="pj",
            fornecedor_id=f_velocity.id,
            colaborador_id=None,
            tipo_despesa="fornecedor",
            flags=[
                "Velocity: 3º pagamento ao mesmo fornecedor hoje",
                "Possível fracionamento para burlar alçada (>100k fracionado)",
            ],
            ml_score=0.59,
            ml_fraude=1,
            ml_motivos=[
                "Velocity rule: múltiplos pagamentos ao mesmo beneficiário no dia.",
                "Regra heurística: Possível fracionamento para burlar alçada (>100k fracionado).",
                "Score ML 59% ≥ limiar 55% → suspeita de fraude.",
            ],
            risk_score=0.71,
            risk_level="alto",
            dados_conferem=1,
        )

    # 13–14 — Fracionamento explícito (2 parcelas)
    f_frac = ativos[5] if len(ativos) > 5 else f_ativo
    for i, v in enumerate([47_800.0, 48_200.0], start=1):
        add(
            codigo=f"HEU_FRACIONAMENTO_{i}",
            nome=f_frac.razao_social,
            documento=f_frac.cnpj,
            valor=v,
            tipo_ben="pj",
            fornecedor_id=f_frac.id,
            colaborador_id=None,
            tipo_despesa="fornecedor",
            flags=[
                f"Parcela {i}/2 — Possível fracionamento para burlar alçada (>100k fracionado)"
            ],
            ml_score=0.54 if i == 2 else 0.46,
            ml_fraude=1 if i == 2 else 0,
            ml_motivos=[
                "Regra heurística: Possível fracionamento para burlar alçada (>100k fracionado).",
                *(["Score ML 54% ≥ limiar 55% → suspeita de fraude."] if i == 2 else []),
            ],
            risk_score=0.58 if i == 2 else 0.5,
            risk_level="medio" if i == 1 else "alto",
            dados_conferem=1,
        )

    # 15 — Horário de risco (simulado no parecer)
    add(
        codigo="ML_HORARIO_RISCO",
        nome=ativos[6].razao_social if len(ativos) > 6 else f_ativo.razao_social,
        documento=ativos[6].cnpj if len(ativos) > 6 else f_ativo.cnpj,
        valor=92_000.0,
        tipo_ben="pj",
        fornecedor_id=ativos[6].id if len(ativos) > 6 else f_ativo.id,
        colaborador_id=None,
        tipo_despesa="fornecedor",
        flags=["Pagamento registrado em janela de horário de risco (22h–06h)"],
        ml_score=0.44,
        ml_fraude=0,
        ml_motivos=[
            "Feature hour_risk elevada — operação fora do horário comercial.",
        ],
        risk_score=0.46,
        risk_level="medio",
        dados_conferem=1,
        documento_nome="NF-madrugada-ok.pdf",
    )

    for i, c in enumerate(cenarios):
        c["dt"] = base + timedelta(minutes=10 * (i + 1))

    return cenarios


def _criar_remessa_catalogo(db, titulo: str, status: str, cenarios: list[dict], dt_base: datetime):
    existente = db.query(Remessa).filter(Remessa.titulo == titulo).first()
    if existente:
        return existente

    conta = db.query(ContaBancaria).filter(ContaBancaria.ativa == 1).first()
    rem = Remessa(
        titulo=titulo,
        conta_bancaria_id=conta.id if conta else None,
        status=status,
        created_by="analista",
        analise_ia_concluida=1,
        created_at=dt_base,
        updated_at=dt_base,
    )
    db.add(rem)
    db.flush()

    pagamentos = []
    for c in cenarios:
        nivel = "ALTO" if c["risk_level"] == "alto" else "MÉDIO"
        genai = _parecer(c["codigo"], c["nome"], c["valor"], nivel)
        pag = _pagamento_catalogo(
            db,
            rem.id,
            codigo=c["codigo"],
            nome=c["nome"],
            documento=c["documento"],
            valor=c["valor"],
            tipo_ben=c["tipo_ben"],
            fornecedor_id=c["fornecedor_id"],
            colaborador_id=c.get("colaborador_id"),
            tipo_despesa=c["tipo_despesa"],
            flags=c["flags"],
            ml_score=c["ml_score"],
            ml_fraude=c["ml_fraude"],
            ml_motivos=c["ml_motivos"],
            risk_score=c["risk_score"],
            risk_level=c["risk_level"],
            genai=genai,
            dados_conferem=c["dados_conferem"],
            fornecedor_nao_cad=c.get("fornecedor_nao_cad", 0),
            pf_nao_cad=c.get("pf_nao_cad", 0),
            documento_nome=c.get("documento_nome", "NF-catalogo-ok.pdf"),
            dt=c["dt"],
        )
        pagamentos.append(pag)

    rem.valor_total = sum(p.valor for p in pagamentos)
    rem.risk_score_max = max(p.risk_score for p in pagamentos) if pagamentos else 0
    rem.risk_level = "alto" if rem.risk_score_max >= 0.7 else "medio"
    if status == "liberada_banco":
        rem.gerente_justificativa = (
            "Catálogo MBA: casos revisados e liberados com documentação complementar."
        )
        rem.email_auditoria = f"Catálogo liberado — {len(pagamentos)} cenários auditados."

    db.add(
        AuditLog(
            entity_type="remessa",
            entity_id=rem.id,
            action="catalogo_fraude_criado",
            user_role="sistema",
            details=json.dumps(
                {
                    "titulo": titulo,
                    "cenarios": len(pagamentos),
                    "codigos": [c["codigo"] for c in cenarios],
                },
                ensure_ascii=False,
            ),
            created_at=dt_base,
        )
    )
    return rem


def seed_catalogo_fraude(force: bool = False) -> dict:
    """
    Garante remessa(s) catálogo com todos os tipos de detecção.
    Retorna estatísticas.
    """
    db = SessionLocal()
    try:
        if force:
            for titulo in (TITULO_CATALOGO, TITULO_CATALOGO_LIBERADO):
                rem = db.query(Remessa).filter(Remessa.titulo == titulo).first()
                if rem:
                    db.query(PagamentoAnaliseIA).filter(
                        PagamentoAnaliseIA.pagamento_id.in_(
                            db.query(Pagamento.id).filter(Pagamento.remessa_id == rem.id)
                        )
                    ).delete(synchronize_session=False)
                    db.query(Pagamento).filter(Pagamento.remessa_id == rem.id).delete()
                    db.query(AuditLog).filter(
                        AuditLog.entity_type == "remessa", AuditLog.entity_id == rem.id
                    ).delete()
                    db.delete(rem)
            db.commit()

        cenarios = _montar_cenarios(db)
        if not cenarios:
            return {"ok": False, "motivo": "cadastros insuficientes"}

        dt = datetime.utcnow() - timedelta(days=1)
        rem_pend = _criar_remessa_catalogo(
            db, TITULO_CATALOGO, "aguardando_gerente", cenarios, dt
        )

        # Subconjunto “resolvido” para diretoria (primeiros 5 cenários únicos)
        vistos = set()
        subset = []
        for c in cenarios:
            if c["codigo"] not in vistos:
                subset.append(c)
                vistos.add(c["codigo"])
            if len(subset) >= 6:
                break
        _criar_remessa_catalogo(
            db,
            TITULO_CATALOGO_LIBERADO,
            "liberada_banco",
            subset,
            dt - timedelta(days=30),
        )

        db.commit()
        n_fraude = sum(1 for c in cenarios if c.get("ml_fraude"))
        return {
            "ok": True,
            "remessa_catalogo_id": rem_pend.id,
            "total_cenarios": len(cenarios),
            "cenarios_ml_fraude": n_fraude,
            "titulo": TITULO_CATALOGO,
        }
    finally:
        db.close()
