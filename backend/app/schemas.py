from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ContaBancariaOut(BaseModel):
    id: int
    nome: str
    banco: str
    agencia: str
    conta: str
    saldo: float
    ativa: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReceitaCreate(BaseModel):
    valor: float = Field(gt=0)
    descricao: str = "Receita operacional"


class MovimentoContaOut(BaseModel):
    id: int
    conta_id: int
    tipo: str
    valor: float
    saldo_apos: float
    descricao: Optional[str]
    remessa_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class FornecedorCreate(BaseModel):
    cnpj: str
    razao_social: str
    banco: str
    agencia: str
    conta: str


class FornecedorOut(BaseModel):
    id: int
    cnpj: str
    razao_social: str
    banco: str
    agencia: str
    conta: str
    status: str
    motivo_rejeicao: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HistoricoCadastroItem(BaseModel):
    id: int
    action: str
    user_role: str
    details: Optional[str] = None
    alertas_ia: List[str] = []
    suspeita: bool = False
    created_at: datetime


class FornecedorHistoricoItem(HistoricoCadastroItem):
    pass


class FornecedorDetalhe(FornecedorOut):
    historico: List[HistoricoCadastroItem] = []


class FornecedorUpdate(BaseModel):
    razao_social: Optional[str] = None
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None


class StatusCadastroUpdate(BaseModel):
    ativo: bool
    motivo: Optional[str] = None
    user_role: str = "gerente"


class FornecedorAprovacao(BaseModel):
    aprovado: bool
    motivo_rejeicao: Optional[str] = None


class ColaboradorCreate(BaseModel):
    cpf: str
    nome_completo: str
    cargo: Optional[str] = None
    banco: str
    agencia: str
    conta: str


class ColaboradorOut(BaseModel):
    id: int
    cpf: str
    nome_completo: str
    cargo: Optional[str]
    banco: str
    agencia: str
    conta: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ColaboradorAprovacao(BaseModel):
    aprovado: bool


class ColaboradorUpdate(BaseModel):
    nome_completo: Optional[str] = None
    cargo: Optional[str] = None
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None


class ColaboradorDetalhe(ColaboradorOut):
    historico: List[HistoricoCadastroItem] = []


class CadastroSolicitacaoCreate(BaseModel):
    operacao: str  # editar | excluir
    motivo: Optional[str] = None
    dados: Optional[dict] = None
    user_role: str = "analista"


class CadastroSolicitacaoOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    operacao: str
    dados_json: Optional[str]
    motivo: Optional[str]
    status: str
    alertas_ia: Optional[str]
    solicitado_por: str
    created_at: datetime
    entidade_nome: Optional[str] = None

    class Config:
        from_attributes = True


class CadastroSolicitacaoDecisao(BaseModel):
    aprovada: bool
    motivo_rejeicao: Optional[str] = None
    user_role: str = "gerente"


class PagamentoAnexoOut(BaseModel):
    id: int
    pagamento_id: int
    tipo: str
    tipo_label: str
    nome_arquivo: str
    mime_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PagamentoAnaliseIAOut(BaseModel):
    id: int
    pagamento_id: int
    versao: int
    triggered_by: str
    risk_score: float
    risk_level: str
    heuristic_flags: Optional[str]
    ml_score: float
    ml_fraude_detectada: int
    ml_motivos: Optional[str]
    genai_parecer: Optional[str]
    dados_conferem: int
    created_at: datetime

    class Config:
        from_attributes = True


class PagamentoOut(BaseModel):
    id: int
    remessa_id: int
    tipo_beneficiario: str = "pj"
    fornecedor_id: Optional[int] = None
    colaborador_id: Optional[int] = None
    beneficiario_nome: Optional[str] = None
    beneficiario_documento: Optional[str] = None
    tipo_despesa: str = "fornecedor"
    competencia: Optional[str] = None
    valor: float
    documento_nome: Optional[str]
    fornecedor_nao_cadastrado: int = 0
    pf_nao_cadastrado: int = 0
    risk_score: float
    risk_level: str
    heuristic_flags: Optional[str]
    ml_score: float
    ml_fraude_detectada: int = 0
    ml_motivos: Optional[str] = None
    genai_parecer: Optional[str]
    dados_conferem: int
    revisado_gerente: int = 0
    revisado_documentos: int = 0
    revisado_valores: int = 0
    revisado_em: Optional[datetime] = None
    revisado_observacao: Optional[str] = None
    ponto_atencao_diretoria: int = 0
    anexos: List["PagamentoAnexoOut"] = []
    documentos_completos: bool = True
    ia_analisado: int = 0
    codigo_pagamento: Optional[str] = None
    historico_analises: List[PagamentoAnaliseIAOut] = []
    fornecedor_razao_social: Optional[str] = None
    fornecedor_cnpj: Optional[str] = None

    class Config:
        from_attributes = True


class PagamentoRevisao(BaseModel):
    valores_ok: bool
    documentos_ok: bool
    observacao: Optional[str] = None
    user_role: str = "gerente"


class PontoAtencaoOut(BaseModel):
    created_at: str | None = None
    pagamento_id: int
    remessa_id: int
    remessa_status: Optional[str]
    remessa_titulo: Optional[str]
    tipo_beneficiario: str
    tipo_despesa: str
    beneficiario_nome: Optional[str]
    beneficiario_documento: Optional[str]
    valor: float
    revisado_gerente: bool
    revisado_observacao: Optional[str]
    gerente_justificativa: Optional[str]
    risk_score: float
    risk_level: str
    ml_fraude_detectada: bool
    pf_nao_cadastrado: bool
    fornecedor_nao_cadastrado: bool


class RemessaCreate(BaseModel):
    titulo: str
    conta_bancaria_id: int


class RemessaOut(BaseModel):
    id: int
    titulo: str
    conta_bancaria_id: Optional[int]
    conta_nome: Optional[str] = None
    status: str
    valor_total: float
    risk_score_max: float
    risk_level: str
    gerente_justificativa: Optional[str]
    email_auditoria: Optional[str]
    motivo_devolucao: Optional[str] = None
    analise_ia_concluida: int = 0
    created_by: str
    created_at: datetime
    pagamentos: List[PagamentoOut] = []
    saldo_conta_disponivel: Optional[float] = None

    class Config:
        from_attributes = True


class RemessaSubmit(BaseModel):
    user_role: str = "analista"


class RemessaDecisao(BaseModel):
    aprovado: bool
    justificativa: Optional[str] = None
    user_role: str = "gerente"
    ip_address: str = "127.0.0.1"


class RemessaDevolucao(BaseModel):
    motivo: str
    user_role: str = "gerente"


class DashboardKPIs(BaseModel):
    total_remessas: int
    total_pagamentos: int
    valor_total_aprovado: float
    valor_bloqueado_ia: float
    fraudes_detectadas: int
    tempo_medio_aprovacao_horas: float
    pagamentos_nao_cadastrados: int
    pagamentos_pf_nao_cadastrados: int
    saldo_total_contas: float


class AuditLogOut(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    user_role: str
    ip_address: str
    details: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
