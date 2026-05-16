from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pagamento, PagamentoAnexo, PagamentoAnaliseIA, Remessa
from app.schemas import PagamentoAnaliseIAOut
from app.schemas import PagamentoOut, PagamentoRevisao
from app.services.audit_service import registrar
from app.services.documentos import LABELS, listar_anexos_pagamento
from app.services.pagamento_out import build_pagamento_out

router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"


@router.get("/{pagamento_id}", response_model=PagamentoOut)
def obter_pagamento(pagamento_id: int, db: Session = Depends(get_db)):
    p = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not p:
        raise HTTPException(404, "Pagamento não encontrado")
    return build_pagamento_out(db, p, incluir_ia=bool(p.ia_analisado), incluir_historico=True)


@router.get("/{pagamento_id}/analises", response_model=list[PagamentoAnaliseIAOut])
def historico_analises(pagamento_id: int, db: Session = Depends(get_db)):
    p = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not p:
        raise HTTPException(404, "Pagamento não encontrado")
    rows = (
        db.query(PagamentoAnaliseIA)
        .filter(PagamentoAnaliseIA.pagamento_id == pagamento_id)
        .order_by(PagamentoAnaliseIA.versao.desc())
        .all()
    )
    return rows


@router.get("/{pagamento_id}/anexos/{anexo_id}/download")
def download_anexo(pagamento_id: int, anexo_id: int, db: Session = Depends(get_db)):
    p = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not p:
        raise HTTPException(404, "Pagamento não encontrado")

    if anexo_id == 0 and p.documento_path:
        path = Path(p.documento_path)
        if not path.exists():
            raise HTTPException(404, "Arquivo não encontrado")
        return FileResponse(path, filename=p.documento_nome or path.name)

    anexo = (
        db.query(PagamentoAnexo)
        .filter(PagamentoAnexo.id == anexo_id, PagamentoAnexo.pagamento_id == pagamento_id)
        .first()
    )
    if not anexo:
        raise HTTPException(404, "Anexo não encontrado")
    path = Path(anexo.caminho)
    if not path.exists():
        raise HTTPException(404, "Arquivo não encontrado no servidor")
    return FileResponse(path, filename=anexo.nome_arquivo, media_type=anexo.mime_type)


@router.post("/{pagamento_id}/revisar", response_model=PagamentoOut)
def revisar_pagamento(
    pagamento_id: int,
    payload: PagamentoRevisao,
    db: Session = Depends(get_db),
):
    p = db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()
    if not p:
        raise HTTPException(404, "Pagamento não encontrado")
    rem = db.query(Remessa).filter(Remessa.id == p.remessa_id).first()
    if not rem or rem.status != "aguardando_gerente":
        raise HTTPException(400, "Pagamento só pode ser revisado com remessa aguardando gerente.")

    if not p.ia_analisado:
        raise HTTPException(400, "Aguarde a análise da IA antes de revisar este pagamento.")

    if not payload.valores_ok or not payload.documentos_ok:
        raise HTTPException(
            400,
            "Marque valores e documentos em conformidade para registrar a revisão.",
        )

    anexos = listar_anexos_pagamento(db, p.id)
    if not anexos and not p.documento_path:
        raise HTTPException(400, "Pagamento sem anexos para revisar.")

    p.revisado_gerente = 1
    p.revisado_valores = 1 if payload.valores_ok else 0
    p.revisado_documentos = 1 if payload.documentos_ok else 0
    p.revisado_em = datetime.utcnow()
    p.revisado_observacao = payload.observacao
    p.ponto_atencao_diretoria = 1
    db.commit()
    db.refresh(p)

    registrar(
        db,
        "pagamento",
        p.id,
        "pagamento_revisado_gerente",
        payload.user_role,
        {
            "valores_ok": payload.valores_ok,
            "documentos_ok": payload.documentos_ok,
            "observacao": payload.observacao,
            "ponto_atencao_diretoria": True,
        },
    )
    return build_pagamento_out(db, p, incluir_ia=True, incluir_historico=True)
