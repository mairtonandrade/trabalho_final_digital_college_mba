from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    LIMITE_FORNECEDOR_NAO_CADASTRADO,
    LIMITE_PF_NAO_CADASTRADO,
    Colaborador,
    ContaBancaria,
    Fornecedor,
    Pagamento,
    Remessa,
)
from app.schemas import RemessaCreate, RemessaDecisao, RemessaDevolucao, RemessaOut, RemessaSubmit
from app.services.documentos import (
    LABELS,
    TIPO_CONTRATO,
    TIPO_HOLERITE,
    TIPO_NF_AVULSA,
    TIPO_NF_PADRAO,
    TIPO_RPA,
    listar_anexos_pagamento,
    salvar_anexo,
    validar_anexos_completos,
)
from app.services.cadastro_historico import STATUS_ELEGIVEL_PAGAMENTO, alertas_historico_para_ia
from app.services.ia_analise import analisar_remessa_completa
from app.services.pagamento_out import build_pagamento_out
from app.services.audit_service import gerar_email_auditoria, registrar
from app.services.conta_service import debitar_remessa, verificar_saldo_remessa
from app.services.utils import formatar_cpf, validar_competencia, validar_cpf

router = APIRouter(prefix="/remessas", tags=["remessas"])
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _remessa_completa(
    db: Session, remessa: Remessa, incluir_historico: bool = False
) -> RemessaOut:
    incluir_ia = bool(remessa.analise_ia_concluida) and remessa.status in (
        "aguardando_gerente",
        "liberada_banco",
        "rejeitada",
    )
    pagamentos = db.query(Pagamento).filter(Pagamento.remessa_id == remessa.id).all()
    conta = None
    saldo_disp = None
    if remessa.conta_bancaria_id:
        conta = (
            db.query(ContaBancaria)
            .filter(ContaBancaria.id == remessa.conta_bancaria_id)
            .first()
        )
        if conta:
            saldo_disp = conta.saldo
    total = sum(p.valor for p in pagamentos)
    return RemessaOut(
        id=remessa.id,
        titulo=remessa.titulo,
        conta_bancaria_id=remessa.conta_bancaria_id,
        conta_nome=conta.nome if conta else None,
        status=remessa.status,
        valor_total=total or remessa.valor_total or 0,
        risk_score_max=remessa.risk_score_max,
        risk_level=remessa.risk_level,
        gerente_justificativa=remessa.gerente_justificativa,
        email_auditoria=remessa.email_auditoria,
        motivo_devolucao=remessa.motivo_devolucao,
        analise_ia_concluida=remessa.analise_ia_concluida or 0,
        created_by=remessa.created_by,
        created_at=remessa.created_at,
        pagamentos=[
            build_pagamento_out(db, p, incluir_ia=incluir_ia, incluir_historico=incluir_historico)
            for p in pagamentos
        ],
        saldo_conta_disponivel=saldo_disp,
    )


@router.get("", response_model=list[RemessaOut])
def listar(
    status: str | None = None,
    historico_ia: bool = False,
    db: Session = Depends(get_db),
):
    q = db.query(Remessa)
    if status:
        q = q.filter(Remessa.status == status)
    remessas = q.order_by(Remessa.created_at.desc()).all()
    return [_remessa_completa(db, r, incluir_historico=historico_ia) for r in remessas]


@router.post("", response_model=RemessaOut)
def criar(payload: RemessaCreate, db: Session = Depends(get_db)):
    conta = (
        db.query(ContaBancaria)
        .filter(ContaBancaria.id == payload.conta_bancaria_id, ContaBancaria.ativa == 1)
        .first()
    )
    if not conta:
        raise HTTPException(400, "Conta bancária inválida ou inativa")
    r = Remessa(
        titulo=payload.titulo,
        status="rascunho",
        conta_bancaria_id=payload.conta_bancaria_id,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    registrar(
        db,
        "remessa",
        r.id,
        "remessa_criada",
        "analista",
        {"titulo": r.titulo, "conta_id": conta.id},
    )
    return _remessa_completa(db, r)


@router.get("/{remessa_id}", response_model=RemessaOut)
def obter_remessa(remessa_id: int, db: Session = Depends(get_db)):
    remessa = db.query(Remessa).filter(Remessa.id == remessa_id).first()
    if not remessa:
        raise HTTPException(404, "Remessa não encontrada")
    return _remessa_completa(db, remessa)


@router.post("/{remessa_id}/pagamentos")
async def adicionar_pagamento(
    remessa_id: int,
    tipo_beneficiario: str = Form("pj"),
    tipo_despesa: str = Form("fornecedor"),
    valor: float = Form(...),
    arquivo: UploadFile | None = File(None),
    arquivo_nf_padrao: UploadFile | None = File(None),
    arquivo_contrato: UploadFile | None = File(None),
    arquivo_nf_avulsa: UploadFile | None = File(None),
    arquivo_rpa: UploadFile | None = File(None),
    arquivo_holerite: UploadFile | None = File(None),
    fornecedor_id: int | None = Form(None),
    colaborador_id: int | None = Form(None),
    cpf_beneficiario: str | None = Form(None),
    nome_beneficiario: str | None = Form(None),
    competencia: str | None = Form(None),
    db: Session = Depends(get_db),
):
    remessa = db.query(Remessa).filter(Remessa.id == remessa_id).first()
    if not remessa:
        raise HTTPException(404, "Remessa não encontrada")
    if remessa.status not in ("rascunho", "devolvida_analista"):
        raise HTTPException(400, "Remessa não permite novos pagamentos neste status")

    tipo_beneficiario = tipo_beneficiario.lower().strip()
    tipo_despesa = tipo_despesa.lower().strip()

    if tipo_despesa == "salario":
        if not competencia or not validar_competencia(competencia):
            raise HTTPException(400, "Despesa de salário exige competência no formato MM/AAAA (ex: 03/2026).")
        if tipo_beneficiario != "pf":
            raise HTTPException(400, "Pagamento de salário deve ser para Pessoa Física (colaborador).")

    nome = ""
    documento = ""
    fornecedor_nao_cad = 0
    pf_nao_cad = 0
    fid = None
    cid = None
    fornecedor_id_heur = 0

    if tipo_beneficiario == "pj":
        if not fornecedor_id:
            raise HTTPException(400, "Selecione o fornecedor (PJ).")
        fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
        if not fornecedor:
            raise HTTPException(404, "Fornecedor não encontrado")
        fid = fornecedor.id
        fornecedor_id_heur = fornecedor.id
        nome = fornecedor.razao_social
        documento = fornecedor.cnpj
        if fornecedor.status not in STATUS_ELEGIVEL_PAGAMENTO:
            fornecedor_nao_cad = 1
            if valor > LIMITE_FORNECEDOR_NAO_CADASTRADO:
                raise HTTPException(
                    400,
                    f"Fornecedor não cadastrado: limite R$ {LIMITE_FORNECEDOR_NAO_CADASTRADO:,.2f}.",
                )
    else:
        if colaborador_id:
            col = db.query(Colaborador).filter(Colaborador.id == colaborador_id).first()
            if not col:
                raise HTTPException(404, "Colaborador não encontrado")
            cid = col.id
            nome = col.nome_completo
            documento = col.cpf
            if col.status not in STATUS_ELEGIVEL_PAGAMENTO:
                pf_nao_cad = 1
                if valor > LIMITE_PF_NAO_CADASTRADO:
                    raise HTTPException(
                        400,
                        f"Colaborador não aprovado: limite R$ {LIMITE_PF_NAO_CADASTRADO:,.2f}.",
                    )
        elif cpf_beneficiario and nome_beneficiario:
            if not validar_cpf(cpf_beneficiario):
                raise HTTPException(400, "CPF inválido")
            cpf_fmt = formatar_cpf(cpf_beneficiario)
            col = db.query(Colaborador).filter(Colaborador.cpf == cpf_fmt).first()
            nome = nome_beneficiario.strip()
            documento = cpf_fmt
            if col and col.status in STATUS_ELEGIVEL_PAGAMENTO:
                cid = col.id
                nome = col.nome_completo
            else:
                pf_nao_cad = 1
                if valor > LIMITE_PF_NAO_CADASTRADO:
                    raise HTTPException(
                        400,
                        f"CPF não cadastrado como colaborador: limite R$ {LIMITE_PF_NAO_CADASTRADO:,.2f}.",
                    )
        else:
            raise HTTPException(
                400,
                "Informe colaborador cadastrado ou CPF + nome do beneficiário (PF).",
            )

    uploads_map: dict[str, UploadFile] = {}
    if tipo_beneficiario == "pj":
        nf = arquivo_nf_padrao or arquivo
        if not nf:
            raise HTTPException(400, "Anexe a nota fiscal padrão (PJ).")
        uploads_map[TIPO_NF_PADRAO] = nf
    elif tipo_despesa == "salario":
        hol = arquivo_holerite or arquivo
        if not hol:
            raise HTTPException(400, "Anexe o holerite/comprovante de salário (PF).")
        uploads_map[TIPO_HOLERITE] = hol
    else:
        if not arquivo_contrato or not arquivo_nf_avulsa or not arquivo_rpa:
            raise HTTPException(
                400,
                "Transferência para PF exige três anexos: Contrato do serviço, "
                "Nota fiscal avulsa e RPA.",
            )
        uploads_map = {
            TIPO_CONTRATO: arquivo_contrato,
            TIPO_NF_AVULSA: arquivo_nf_avulsa,
            TIPO_RPA: arquivo_rpa,
        }

    nomes_arquivos = ", ".join(u.filename or "arquivo" for u in uploads_map.values())
    arquivo_ref = next(iter(uploads_map.values()))
    flags_docs = [
        f"✓ {LABELS[t]}" for t in uploads_map
    ]

    pag = Pagamento(
        remessa_id=remessa_id,
        tipo_beneficiario=tipo_beneficiario,
        fornecedor_id=fid,
        colaborador_id=cid,
        beneficiario_nome=nome,
        beneficiario_documento=documento,
        tipo_despesa=tipo_despesa,
        competencia=competencia if tipo_despesa == "salario" else None,
        valor=valor,
        documento_nome=nomes_arquivos,
        documento_path=None,
        fornecedor_nao_cadastrado=fornecedor_nao_cad,
        pf_nao_cadastrado=pf_nao_cad,
        ia_analisado=0,
        ponto_atencao_diretoria=0,
        risk_score=0.0,
        risk_level="pendente_ia",
        heuristic_flags="; ".join(flags_docs) if flags_docs else None,
    )
    db.add(pag)
    db.flush()

    primeiro_caminho = None
    for tipo_anexo, up in uploads_map.items():
        anexo = await salvar_anexo(UPLOAD_DIR, remessa_id, pag.id, tipo_anexo, up, db)
        if primeiro_caminho is None:
            primeiro_caminho = anexo.caminho
    if primeiro_caminho:
        pag.documento_path = primeiro_caminho
    db.commit()
    db.refresh(pag)

    pagamentos = db.query(Pagamento).filter(Pagamento.remessa_id == remessa_id).all()
    remessa.valor_total = sum(p.valor for p in pagamentos)
    if remessa.status == "devolvida_analista":
        remessa.motivo_devolucao = None
    db.commit()

    registrar(
        db,
        "pagamento",
        pag.id,
        "pagamento_incluido_remessa",
        "analista",
        {"valor": valor, "codigo": f"PAY-{pag.id:06d}"},
    )
    return build_pagamento_out(db, pag, incluir_ia=False)


@router.post("/{remessa_id}/enviar", response_model=RemessaOut)
async def enviar_gerente(
    remessa_id: int,
    payload: RemessaSubmit,
    db: Session = Depends(get_db),
):
    remessa = db.query(Remessa).filter(Remessa.id == remessa_id).first()
    if not remessa:
        raise HTTPException(404, "Remessa não encontrada")
    if remessa.status not in ("rascunho", "devolvida_analista"):
        raise HTTPException(400, "Remessa não pode ser enviada neste status")

    pagamentos = db.query(Pagamento).filter(Pagamento.remessa_id == remessa_id).all()
    if not pagamentos:
        raise HTTPException(400, "Adicione ao menos um pagamento à remessa")

    ok, msg, total = verificar_saldo_remessa(db, remessa, pagamentos)
    if not ok:
        raise HTTPException(400, msg)

    for p in pagamentos:
        anexos = listar_anexos_pagamento(db, p.id)
        tipos = {a.tipo for a in anexos}
        if not anexos and p.documento_path:
            continue
        ok_doc, msg_doc = validar_anexos_completos(
            p.tipo_beneficiario or "pj", p.tipo_despesa or "fornecedor", tipos
        )
        if not ok_doc:
            raise HTTPException(400, f"PAY-{p.id:06d}: {msg_doc}")

    triggered = "reenvio_gerente" if remessa.status == "devolvida_analista" else "envio_gerente"
    remessa.status = "analisando_ia"
    remessa.analise_ia_concluida = 0
    remessa.motivo_devolucao = None
    db.commit()

    await analisar_remessa_completa(db, remessa, triggered)

    remessa.valor_total = total
    remessa.status = "aguardando_gerente"
    db.commit()
    registrar(
        db,
        "remessa",
        remessa.id,
        "enviada_gerente",
        payload.user_role,
        {"valor_total": total, "pagamentos": len(pagamentos), "ia": True},
    )
    return _remessa_completa(db, remessa, incluir_historico=False)


@router.post("/{remessa_id}/devolver", response_model=RemessaOut)
def devolver_analista(
    remessa_id: int,
    payload: RemessaDevolucao,
    db: Session = Depends(get_db),
):
    remessa = db.query(Remessa).filter(Remessa.id == remessa_id).first()
    if not remessa:
        raise HTTPException(404, "Remessa não encontrada")
    if remessa.status != "aguardando_gerente":
        raise HTTPException(400, "Só é possível devolver remessas aguardando gerente")
    if not payload.motivo.strip():
        raise HTTPException(400, "Informe o motivo da devolução ao analista")

    pagamentos = db.query(Pagamento).filter(Pagamento.remessa_id == remessa_id).all()
    remessa.status = "devolvida_analista"
    remessa.motivo_devolucao = payload.motivo.strip()
    remessa.analise_ia_concluida = 0
    for p in pagamentos:
        p.revisado_gerente = 0
        p.revisado_documentos = 0
        p.revisado_valores = 0
        p.ia_analisado = 0
    db.commit()
    registrar(
        db,
        "remessa",
        remessa.id,
        "devolvida_analista",
        payload.user_role,
        {"motivo": payload.motivo},
    )
    return _remessa_completa(db, remessa)


@router.post("/{remessa_id}/reanalisar-ia", response_model=RemessaOut)
async def reanalisar_ia(
    remessa_id: int,
    db: Session = Depends(get_db),
):
    remessa = db.query(Remessa).filter(Remessa.id == remessa_id).first()
    if not remessa:
        raise HTTPException(404, "Remessa não encontrada")
    if remessa.status != "aguardando_gerente":
        raise HTTPException(400, "Reanálise disponível apenas com remessa aguardando gerente")

    await analisar_remessa_completa(db, remessa, "reanalise_gerente")
    db.commit()
    registrar(db, "remessa", remessa.id, "reanalise_ia", "gerente", {})
    return _remessa_completa(db, remessa, incluir_historico=True)


@router.post("/{remessa_id}/decisao", response_model=RemessaOut)
def decisao_gerente(
    remessa_id: int,
    payload: RemessaDecisao,
    db: Session = Depends(get_db),
):
    remessa = db.query(Remessa).filter(Remessa.id == remessa_id).first()
    if not remessa:
        raise HTTPException(404, "Remessa não encontrada")
    if remessa.status != "aguardando_gerente":
        raise HTTPException(400, "Remessa não está aguardando gerente")

    if payload.aprovado and not remessa.analise_ia_concluida:
        raise HTTPException(
            400,
            "A remessa só pode ser liberada após a conclusão da análise IA. "
            "Aguarde o processamento ou solicite reanálise.",
        )

    pagamentos = db.query(Pagamento).filter(Pagamento.remessa_id == remessa_id).all()

    if payload.aprovado:
        sem_ia = [p for p in pagamentos if not p.ia_analisado]
        if sem_ia:
            ids = ", ".join(f"PAY-{p.id:06d}" for p in sem_ia)
            raise HTTPException(
                400,
                f"Todos os pagamentos devem passar pela revisão da IA antes da liberação. "
                f"Pendente(s): {ids}.",
            )
    tem_nao_cadastrado = any(p.fornecedor_nao_cadastrado for p in pagamentos)
    tem_pf_nao_cad = any(p.pf_nao_cadastrado for p in pagamentos)

    if remessa.risk_level == "alto" and payload.aprovado and not payload.justificativa:
        raise HTTPException(
            400,
            "Justificativa obrigatória para liberar pagamento de ALTO RISCO (Zero-Trust).",
        )
    tem_ml_fraude = any(p.ml_fraude_detectada for p in pagamentos)

    if (tem_nao_cadastrado or tem_pf_nao_cad or tem_ml_fraude) and payload.aprovado and not payload.justificativa:
        raise HTTPException(
            400,
            "Justificativa obrigatória: remessa com alerta (não cadastrado, PF ou fraude detectada pelo ML).",
        )

    if payload.aprovado:
        nao_revisados = [p for p in pagamentos if not p.revisado_gerente]
        if nao_revisados:
            ids = ", ".join(f"#{p.id}" for p in nao_revisados)
            raise HTTPException(
                400,
                f"Revise valores e documentos de todos os pagamentos antes de liberar. "
                f"Pendente(s): {ids}.",
            )

    fids = [p.fornecedor_id for p in pagamentos if p.fornecedor_id]
    fornecedores_map = {
        f.id: f for f in db.query(Fornecedor).filter(Fornecedor.id.in_(fids)).all()
    } if fids else {}

    if payload.aprovado:
        ok, msg, _ = verificar_saldo_remessa(db, remessa, pagamentos)
        if not ok:
            raise HTTPException(400, msg)
        try:
            debitar_remessa(db, remessa.conta_bancaria_id, remessa, pagamentos)
        except ValueError as e:
            raise HTTPException(400, str(e))

        remessa.status = "liberada_banco"
        remessa.gerente_justificativa = payload.justificativa
        remessa.email_auditoria = gerar_email_auditoria(
            remessa, pagamentos, fornecedores_map
        )
        revisados = [p for p in pagamentos if p.revisado_gerente]
        if revisados:
            remessa.email_auditoria += (
                "\n\n*** PONTOS DE ATENÇÃO DIRETORIA: Pagamento(s) revisados pelo gerente "
                "(valores e documentos conferidos) — acompanhar na trilha executiva. ***"
            )
        if tem_nao_cadastrado or tem_pf_nao_cad:
            remessa.email_auditoria += (
                "\n\n*** ALERTA DIRETORIA: Pagamento(s) a beneficiário não cadastrado (PJ/PF). "
                f"Justificativa gerente: {payload.justificativa} ***"
            )
        action = "remessa_liberada_banco"
    else:
        remessa.status = "rejeitada"
        remessa.gerente_justificativa = payload.justificativa or "Rejeitada pelo gerente"
        action = "remessa_rejeitada"

    db.commit()
    registrar(
        db,
        "remessa",
        remessa.id,
        action,
        payload.user_role,
        {
            "justificativa": payload.justificativa,
            "nao_cadastrado": tem_nao_cadastrado,
            "pf_nao_cadastrado": tem_pf_nao_cad,
        },
        payload.ip_address,
    )
    return _remessa_completa(db, remessa)
