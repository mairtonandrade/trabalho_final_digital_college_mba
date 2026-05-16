"""Tipos de anexo e regras documentais por beneficiário/despesa."""

from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models import Pagamento, PagamentoAnexo
from app.services.utils import validar_mime_arquivo

TIPO_CONTRATO = "contrato"
TIPO_NF_AVULSA = "nf_avulsa"
TIPO_RPA = "rpa"
TIPO_NF_PADRAO = "nf_padrao"
TIPO_HOLERITE = "holerite"

LABELS = {
    TIPO_CONTRATO: "Contrato do serviço prestado",
    TIPO_NF_AVULSA: "Nota fiscal avulsa",
    TIPO_RPA: "RPA (Recibo de Pagamento Autônomo)",
    TIPO_NF_PADRAO: "Nota fiscal padrão",
    TIPO_HOLERITE: "Holerite / comprovante de salário",
}


def tipos_obrigatorios(tipo_beneficiario: str, tipo_despesa: str) -> list[str]:
    if tipo_beneficiario == "pj":
        return [TIPO_NF_PADRAO]
    if tipo_despesa == "salario":
        return [TIPO_HOLERITE]
    return [TIPO_CONTRATO, TIPO_NF_AVULSA, TIPO_RPA]


def validar_anexos_completos(
    tipo_beneficiario: str, tipo_despesa: str, tipos_presentes: set[str]
) -> tuple[bool, str]:
    obrig = set(tipos_obrigatorios(tipo_beneficiario, tipo_despesa))
    faltando = obrig - tipos_presentes
    if faltando:
        nomes = ", ".join(LABELS.get(t, t) for t in sorted(faltando))
        return False, f"Documentos obrigatórios em falta: {nomes}."
    return True, ""


async def salvar_anexo(
    upload_dir: Path,
    remessa_id: int,
    pagamento_id: int,
    tipo: str,
    arquivo: UploadFile,
    db: Session,
) -> PagamentoAnexo:
    if not arquivo.filename:
        raise HTTPException(400, f"Arquivo inválido para {LABELS.get(tipo, tipo)}.")
    dest = upload_dir / f"rem_{remessa_id}_pag_{pagamento_id}_{tipo}_{arquivo.filename}"
    with dest.open("wb") as f:
        content = await arquivo.read()
        f.write(content)
    ok_mime, mime = validar_mime_arquivo(dest)
    if not ok_mime:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            400,
            f"{LABELS.get(tipo, tipo)}: tipo não permitido. Use PDF, PNG ou JPG.",
        )
    anexo = PagamentoAnexo(
        pagamento_id=pagamento_id,
        tipo=tipo,
        nome_arquivo=arquivo.filename,
        caminho=str(dest),
        mime_type=mime,
    )
    db.add(anexo)
    return anexo


def listar_anexos_pagamento(db: Session, pagamento_id: int) -> list[PagamentoAnexo]:
    return (
        db.query(PagamentoAnexo)
        .filter(PagamentoAnexo.pagamento_id == pagamento_id)
        .order_by(PagamentoAnexo.id)
        .all()
    )


def conferir_documentos_pagamento(p: Pagamento, anexos: list[PagamentoAnexo]) -> bool:
    tipos = {a.tipo for a in anexos}
    if p.documento_path and not anexos:
        if p.tipo_beneficiario == "pj":
            tipos.add(TIPO_NF_PADRAO)
        elif p.tipo_despesa == "salario":
            tipos.add(TIPO_HOLERITE)
        else:
            tipos.update({TIPO_CONTRATO, TIPO_NF_AVULSA, TIPO_RPA})
    ok, _ = validar_anexos_completos(
        p.tipo_beneficiario or "pj", p.tipo_despesa or "fornecedor", tipos
    )
    return ok
