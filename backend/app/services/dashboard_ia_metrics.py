"""Métricas agregadas de detecção IA para gráficos executivos (Diretoria)."""

from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Pagamento, PagamentoAnaliseIA

TRIGGER_PERFIL = {
    "envio_gerente": "analista",
    "reenvio_gerente": "analista",
    "reanalise_gerente": "gerente",
    "catalogo_mba": "sistema",
}

PERFIL_LABEL = {
    "analista": "Analista",
    "gerente": "Gerente",
    "sistema": "Sistema / IA",
    "diretoria": "Diretoria",
}

MESES_PT = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]


def _tipo_deteccao(p: Pagamento) -> str:
    if p.ml_fraude_detectada:
        return "fraude_ml"
    if p.fornecedor_nao_cadastrado:
        return "pj_nao_cadastrado"
    if p.pf_nao_cadastrado:
        return "pf_nao_cadastrado"
    if (p.risk_level or "").lower() == "alto" or (p.risk_score or 0) >= 0.7:
        return "risco_alto"
    if (p.risk_level or "").lower() == "medio" or (p.risk_score or 0) >= 0.4:
        return "risco_medio"
    return "conformidade"


TIPO_LABEL = {
    "fraude_ml": "Fraude ML",
    "pj_nao_cadastrado": "PJ não cadastrado",
    "pf_nao_cadastrado": "PF não cadastrado",
    "risco_alto": "Risco alto",
    "risco_medio": "Risco médio",
    "conformidade": "Conformidade",
}


def metricas_ia_diretoria(db: Session, meses: int = 6) -> dict:
    pagamentos_ia = db.query(Pagamento).filter(Pagamento.ia_analisado == 1).all()
    analises = db.query(PagamentoAnaliseIA).order_by(PagamentoAnaliseIA.created_at.asc()).all()

    por_perfil: dict[str, int] = defaultdict(int)
    for a in analises:
        perfil = TRIGGER_PERFIL.get(a.triggered_by or "", "sistema")
        por_perfil[perfil] += 1

    por_perfil_out = [
        {
            "perfil": k,
            "label": PERFIL_LABEL.get(k, k.title()),
            "quantidade": v,
        }
        for k, v in sorted(por_perfil.items(), key=lambda x: -x[1])
    ]

    por_mes: dict[str, int] = defaultdict(int)
    for a in analises:
        if not a.created_at:
            continue
        chave = a.created_at.strftime("%Y-%m")
        por_mes[chave] += 1
    for p in pagamentos_ia:
        if not p.created_at:
            continue
        chave = p.created_at.strftime("%Y-%m")
        if chave not in por_mes:
            por_mes[chave] = por_mes.get(chave, 0)

    chaves_ordenadas = sorted(por_mes.keys())[-meses:]
    por_mes_out = []
    for chave in chaves_ordenadas:
        ano, mes = chave.split("-")
        por_mes_out.append(
            {
                "mes": chave,
                "label": f"{MESES_PT[int(mes) - 1]}/{ano[2:]}",
                "quantidade": por_mes[chave],
            }
        )

    por_tipo: dict[str, int] = defaultdict(int)
    for p in pagamentos_ia:
        tipo = _tipo_deteccao(p)
        por_tipo[tipo] += 1

    ordem_tipos = [
        "fraude_ml",
        "pj_nao_cadastrado",
        "pf_nao_cadastrado",
        "risco_alto",
        "risco_medio",
        "conformidade",
    ]
    por_tipo_out = [
        {
            "tipo": t,
            "label": TIPO_LABEL[t],
            "quantidade": por_tipo.get(t, 0),
        }
        for t in ordem_tipos
        if por_tipo.get(t, 0) > 0
    ]

    return {
        "resumo": {
            "total_analises": len(analises),
            "total_pagamentos_ia": len(pagamentos_ia),
            "fraudes_ml": sum(1 for p in pagamentos_ia if p.ml_fraude_detectada),
            "atualizado_em": datetime.utcnow().isoformat(),
        },
        "por_perfil": por_perfil_out,
        "por_mes": por_mes_out,
        "por_tipo_deteccao": por_tipo_out,
    }
