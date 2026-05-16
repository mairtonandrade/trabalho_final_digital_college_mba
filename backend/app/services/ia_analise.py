"""Análise IA (ML + GenAI) executada no envio ao gerente ou na reanálise."""

from sqlalchemy.orm import Session

from app.models import ContaBancaria, Pagamento, PagamentoAnaliseIA, Remessa
from app.services import genai_audit
from app.services.fraud_engine import analisar_fraude
from app.services.fraud_detector import score_final
from app.services.heuristics import regras_heuristicas
from app.services.cadastro_historico import alertas_historico_para_ia
from app.services.utils import nivel_risco


async def executar_analise_ia_pagamento(
    db: Session,
    pag: Pagamento,
    remessa: Remessa,
    triggered_by: str = "envio_gerente",
) -> PagamentoAnaliseIA:
    nome = pag.beneficiario_nome or ""
    documento = pag.beneficiario_documento or ""
    fornecedor_id_heur = pag.fornecedor_id or 0

    dados_conferem = 1
    if pag.documento_nome:
        dados_conferem = int(
            genai_audit.conferir_dados_documento(
                nome, documento, pag.valor, pag.documento_nome
            )
        )

    h_score, flags = regras_heuristicas(
        db, fornecedor_id_heur, pag.valor, nome, documento
    )
    if pag.fornecedor_nao_cadastrado:
        flags.append("ALERTA: Fornecedor PJ NÃO CADASTRADO na whitelist.")
        h_score = min(h_score + 0.35, 0.85)
    if pag.pf_nao_cadastrado:
        flags.append("ALERTA: PF com CPF NÃO CADASTRADO como colaborador.")
        h_score = min(h_score + 0.4, 0.9)
    if pag.tipo_despesa == "salario" and pag.competencia:
        flags.append(f"Despesa de SALÁRIO — competência {pag.competencia}")

    if pag.colaborador_id:
        flags.extend(alertas_historico_para_ia(db, "colaborador", pag.colaborador_id))
    if pag.fornecedor_id:
        flags.extend(alertas_historico_para_ia(db, "fornecedor", pag.fornecedor_id))

    saldo_conta = None
    if remessa.conta_bancaria_id:
        conta = (
            db.query(ContaBancaria)
            .filter(ContaBancaria.id == remessa.conta_bancaria_id)
            .first()
        )
        saldo_conta = conta.saldo if conta else None

    analise_ml = analisar_fraude(
        db,
        valor=pag.valor,
        saldo_conta=saldo_conta,
        heuristic_score=h_score,
        flags_heuristicas=flags,
        fornecedor_nao_cad=bool(pag.fornecedor_nao_cadastrado),
        pf_nao_cad=bool(pag.pf_nao_cadastrado),
        fornecedor_id=fornecedor_id_heur or None,
        tipo_despesa=pag.tipo_despesa or "fornecedor",
    )
    ml_score = analise_ml.ml_score
    risk = score_final(h_score, ml_score, bool(dados_conferem))
    if analise_ml.ml_fraude_detectada:
        risk = min(risk + 0.1, 1.0)
    if pag.fornecedor_nao_cadastrado or pag.pf_nao_cadastrado:
        risk = min(risk + 0.15, 1.0)
    level = nivel_risco(risk)

    parecer = await genai_audit.gerar_parecer_auditoria(
        nome,
        documento,
        pag.valor,
        risk,
        flags,
        bool(dados_conferem),
        pag.documento_nome or "",
    )
    if pag.pf_nao_cadastrado:
        parecer = "[PF NÃO CADASTRADA — justificativa gerencial obrigatória se liberar.]\n" + parecer
    if pag.tipo_despesa == "salario":
        parecer = f"[SALÁRIO — Competência {pag.competencia}]\n" + parecer
    if analise_ml.ml_fraude_detectada:
        parecer = (
            f"[⚠ MODELO ML — FRAUDE DETECTADA ({ml_score:.0%})]\n"
            + "\n".join(f"• {m}" for m in analise_ml.ml_motivos[:5])
            + "\n\n"
            + parecer
        )

    versao = (
        db.query(PagamentoAnaliseIA)
        .filter(PagamentoAnaliseIA.pagamento_id == pag.id)
        .count()
        + 1
    )

    registro = PagamentoAnaliseIA(
        pagamento_id=pag.id,
        versao=versao,
        triggered_by=triggered_by,
        risk_score=risk,
        risk_level=level,
        heuristic_flags="; ".join(flags) if flags else None,
        ml_score=ml_score,
        ml_fraude_detectada=1 if analise_ml.ml_fraude_detectada else 0,
        ml_motivos="; ".join(analise_ml.ml_motivos) if analise_ml.ml_motivos else None,
        genai_parecer=parecer,
        dados_conferem=dados_conferem,
    )
    db.add(registro)

    pag.risk_score = risk
    pag.risk_level = level
    pag.heuristic_flags = registro.heuristic_flags
    pag.ml_score = ml_score
    pag.ml_fraude_detectada = registro.ml_fraude_detectada
    pag.ml_motivos = registro.ml_motivos
    pag.genai_parecer = parecer
    pag.dados_conferem = dados_conferem
    pag.ia_analisado = 1
    pag.ponto_atencao_diretoria = 1 if (analise_ml.ml_fraude_detectada or risk >= 0.4) else pag.ponto_atencao_diretoria

    return registro


async def analisar_remessa_completa(
    db: Session, remessa: Remessa, triggered_by: str = "envio_gerente"
) -> int:
    pagamentos = db.query(Pagamento).filter(Pagamento.remessa_id == remessa.id).all()
    for p in pagamentos:
        p.revisado_gerente = 0
        p.revisado_documentos = 0
        p.revisado_valores = 0
        p.revisado_em = None
        p.revisado_observacao = None
        await executar_analise_ia_pagamento(db, p, remessa, triggered_by)

    if pagamentos:
        remessa.risk_score_max = max(p.risk_score for p in pagamentos)
        remessa.risk_level = nivel_risco(remessa.risk_score_max)
        remessa.valor_total = sum(p.valor for p in pagamentos)
    remessa.analise_ia_concluida = 1
    return len(pagamentos)
