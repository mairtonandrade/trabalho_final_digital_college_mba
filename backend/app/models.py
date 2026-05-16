from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database import Base

LIMITE_FORNECEDOR_NAO_CADASTRADO = 10_000.0
LIMITE_PF_NAO_CADASTRADO = 10_000.0


class ContaBancaria(Base):
    __tablename__ = "contas_bancarias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    banco = Column(String(100), nullable=False)
    agencia = Column(String(20), nullable=False)
    conta = Column(String(30), nullable=False)
    saldo = Column(Float, default=0.0)
    ativa = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class MovimentoConta(Base):
    __tablename__ = "movimentos_conta"

    id = Column(Integer, primary_key=True, index=True)
    conta_id = Column(Integer, nullable=False, index=True)
    tipo = Column(String(20), nullable=False)
    valor = Column(Float, nullable=False)
    saldo_apos = Column(Float, nullable=False)
    descricao = Column(String(500), nullable=True)
    remessa_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Colaborador(Base):
    __tablename__ = "colaboradores"

    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String(14), unique=True, nullable=False)
    nome_completo = Column(String(255), nullable=False)
    cargo = Column(String(120), nullable=True)
    banco = Column(String(100), nullable=False)
    agencia = Column(String(20), nullable=False)
    conta = Column(String(30), nullable=False)
    status = Column(String(20), default="pendente")  # pendente | ativo | inativo | rejeitado
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(18), unique=True, nullable=False)
    razao_social = Column(String(255), nullable=False)
    banco = Column(String(100), nullable=False)
    agencia = Column(String(20), nullable=False)
    conta = Column(String(30), nullable=False)
    status = Column(String(20), default="pendente")  # pendente | ativo | inativo | rejeitado
    motivo_rejeicao = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CadastroSolicitacao(Base):
    __tablename__ = "cadastro_solicitacoes"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(20), nullable=False)  # fornecedor | colaborador
    entity_id = Column(Integer, nullable=False)
    operacao = Column(String(20), nullable=False)  # editar | excluir
    dados_json = Column(Text, nullable=True)
    motivo = Column(Text, nullable=True)
    status = Column(String(20), default="pendente")  # pendente | aprovada | rejeitada
    alertas_ia = Column(Text, nullable=True)
    solicitado_por = Column(String(50), default="analista")
    created_at = Column(DateTime, default=datetime.utcnow)


class Remessa(Base):
    __tablename__ = "remessas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    conta_bancaria_id = Column(Integer, nullable=True, index=True)
    status = Column(String(30), default="rascunho")
    valor_total = Column(Float, default=0.0)
    risk_score_max = Column(Float, default=0.0)
    risk_level = Column(String(20), default="baixo")
    gerente_justificativa = Column(Text, nullable=True)
    email_auditoria = Column(Text, nullable=True)
    motivo_devolucao = Column(Text, nullable=True)
    analise_ia_concluida = Column(Integer, default=0)
    created_by = Column(String(50), default="analista")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    remessa_id = Column(Integer, nullable=False, index=True)
    tipo_beneficiario = Column(String(5), default="pj")  # pj | pf
    fornecedor_id = Column(Integer, nullable=True)
    colaborador_id = Column(Integer, nullable=True)
    beneficiario_nome = Column(String(255), nullable=True)
    beneficiario_documento = Column(String(18), nullable=True)
    tipo_despesa = Column(String(30), default="fornecedor")  # fornecedor | salario | outros
    competencia = Column(String(7), nullable=True)  # MM/AAAA
    valor = Column(Float, nullable=False)
    documento_nome = Column(String(255), nullable=True)
    documento_path = Column(String(500), nullable=True)
    fornecedor_nao_cadastrado = Column(Integer, default=0)
    pf_nao_cadastrado = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="baixo")
    heuristic_flags = Column(Text, nullable=True)
    ml_score = Column(Float, default=0.0)
    ml_fraude_detectada = Column(Integer, default=0)
    ml_motivos = Column(Text, nullable=True)
    genai_parecer = Column(Text, nullable=True)
    dados_conferem = Column(Integer, default=1)
    revisado_gerente = Column(Integer, default=0)
    revisado_documentos = Column(Integer, default=0)
    revisado_valores = Column(Integer, default=0)
    revisado_em = Column(DateTime, nullable=True)
    revisado_observacao = Column(Text, nullable=True)
    ponto_atencao_diretoria = Column(Integer, default=0)
    ia_analisado = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class PagamentoAnaliseIA(Base):
    __tablename__ = "pagamento_analises_ia"

    id = Column(Integer, primary_key=True, index=True)
    pagamento_id = Column(Integer, nullable=False, index=True)
    versao = Column(Integer, nullable=False, default=1)
    triggered_by = Column(String(50), default="envio_gerente")
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="baixo")
    heuristic_flags = Column(Text, nullable=True)
    ml_score = Column(Float, default=0.0)
    ml_fraude_detectada = Column(Integer, default=0)
    ml_motivos = Column(Text, nullable=True)
    genai_parecer = Column(Text, nullable=True)
    dados_conferem = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)


class PagamentoAnexo(Base):
    __tablename__ = "pagamento_anexos"

    id = Column(Integer, primary_key=True, index=True)
    pagamento_id = Column(Integer, nullable=False, index=True)
    tipo = Column(String(30), nullable=False)
    nome_arquivo = Column(String(255), nullable=False)
    caminho = Column(String(500), nullable=False)
    mime_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(100), nullable=False)
    user_role = Column(String(50), nullable=False)
    ip_address = Column(String(50), default="127.0.0.1")
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
