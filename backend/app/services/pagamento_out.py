from sqlalchemy.orm import Session

from app.models import Fornecedor, Pagamento, PagamentoAnaliseIA
from app.schemas import PagamentoAnaliseIAOut, PagamentoAnexoOut, PagamentoOut
from app.services.documentos import LABELS, conferir_documentos_pagamento, listar_anexos_pagamento


def _historico_out(db: Session, pagamento_id: int) -> list[PagamentoAnaliseIAOut]:
    rows = (
        db.query(PagamentoAnaliseIA)
        .filter(PagamentoAnaliseIA.pagamento_id == pagamento_id)
        .order_by(PagamentoAnaliseIA.versao.desc())
        .all()
    )
    return [PagamentoAnaliseIAOut.model_validate(r) for r in rows]


def build_pagamento_out(
    db: Session, p: Pagamento, incluir_ia: bool = True, incluir_historico: bool = False
) -> PagamentoOut:
    f = (
        db.query(Fornecedor).filter(Fornecedor.id == p.fornecedor_id).first()
        if p.fornecedor_id
        else None
    )
    nome = p.beneficiario_nome or (f.razao_social if f else None)
    doc = p.beneficiario_documento or (f.cnpj if f else None)
    anexos_db = listar_anexos_pagamento(db, p.id)
    anexos_out = [
        PagamentoAnexoOut(
            id=a.id,
            pagamento_id=a.pagamento_id,
            tipo=a.tipo,
            tipo_label=LABELS.get(a.tipo, a.tipo),
            nome_arquivo=a.nome_arquivo,
            mime_type=a.mime_type,
            created_at=a.created_at,
        )
        for a in anexos_db
    ]
    if not anexos_out and p.documento_nome and p.documento_path:
        tipo_legacy = "nf_padrao" if (p.tipo_beneficiario or "pj") == "pj" else (
            "holerite" if p.tipo_despesa == "salario" else "contrato"
        )
        anexos_out = [
            PagamentoAnexoOut(
                id=0,
                pagamento_id=p.id,
                tipo=tipo_legacy,
                tipo_label=LABELS.get(tipo_legacy, "Documento"),
                nome_arquivo=p.documento_nome,
                mime_type=None,
                created_at=p.created_at,
            )
        ]

    mostrar_ia = incluir_ia and (p.ia_analisado or 0)
    historico = _historico_out(db, p.id) if incluir_historico else []

    return PagamentoOut(
        id=p.id,
        remessa_id=p.remessa_id,
        tipo_beneficiario=p.tipo_beneficiario or "pj",
        fornecedor_id=p.fornecedor_id,
        colaborador_id=p.colaborador_id,
        beneficiario_nome=nome,
        beneficiario_documento=doc,
        tipo_despesa=p.tipo_despesa or "fornecedor",
        competencia=p.competencia,
        valor=p.valor,
        documento_nome=p.documento_nome,
        fornecedor_nao_cadastrado=p.fornecedor_nao_cadastrado or 0,
        pf_nao_cadastrado=p.pf_nao_cadastrado or 0,
        risk_score=p.risk_score if mostrar_ia else 0.0,
        risk_level=p.risk_level if mostrar_ia else "pendente_ia",
        heuristic_flags=p.heuristic_flags if mostrar_ia else None,
        ml_score=p.ml_score if mostrar_ia else 0.0,
        ml_fraude_detectada=p.ml_fraude_detectada if mostrar_ia else 0,
        ml_motivos=p.ml_motivos if mostrar_ia else None,
        genai_parecer=p.genai_parecer if mostrar_ia else None,
        dados_conferem=p.dados_conferem,
        revisado_gerente=p.revisado_gerente or 0,
        revisado_documentos=p.revisado_documentos or 0,
        revisado_valores=p.revisado_valores or 0,
        revisado_em=p.revisado_em,
        revisado_observacao=p.revisado_observacao,
        ponto_atencao_diretoria=p.ponto_atencao_diretoria or 0,
        anexos=anexos_out,
        documentos_completos=conferir_documentos_pagamento(p, anexos_db),
        ia_analisado=p.ia_analisado or 0,
        codigo_pagamento=f"PAY-{p.id:06d}",
        historico_analises=historico,
        fornecedor_razao_social=f.razao_social if f else nome,
        fornecedor_cnpj=f.cnpj if f else doc,
    )
