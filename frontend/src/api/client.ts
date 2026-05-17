import axios, { type InternalAxiosRequestConfig } from 'axios'
import { isDemoMode } from './apiConfig'
import { resolveDemoResponse } from './demoResolver'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 120000,
})

function isHtmlPayload(data: unknown): boolean {
  if (typeof data !== 'string') return false
  const s = data.trim().toLowerCase()
  return s.startsWith('<!doctype') || s.startsWith('<html')
}

api.interceptors.response.use(
  (response) => {
    const ct = String(response.headers['content-type'] || '')
    if (ct.includes('text/html') || isHtmlPayload(response.data)) {
      return Promise.reject(
        new Error('API indisponível — configure VITE_API_URL no Netlify ou use modo demo.')
      )
    }
    return response
  },
  (error) => Promise.reject(error)
)

if (isDemoMode()) {
  api.defaults.adapter = (config: InternalAxiosRequestConfig) =>
    Promise.resolve({
      data: resolveDemoResponse(config),
      status: 200,
      statusText: 'OK',
      headers: { 'content-type': 'application/json' },
      config,
    })
}

export interface ContaBancaria {
  id: number
  nome: string
  banco: string
  agencia: string
  conta: string
  saldo: number
  ativa: number
}

export interface MovimentoConta {
  id: number
  conta_id: number
  tipo: string
  valor: number
  saldo_apos: number
  descricao?: string
  remessa_id?: number
  created_at: string
}

export interface Fornecedor {
  id: number
  cnpj: string
  razao_social: string
  banco: string
  agencia: string
  conta: string
  status: string
  motivo_rejeicao?: string
  created_at?: string
}

export interface FornecedorHistoricoItem {
  id: number
  action: string
  user_role: string
  details?: string
  created_at: string
}

export interface FornecedorDetalhe extends Fornecedor {
  historico: HistoricoCadastroItem[]
}

export interface Colaborador {
  id: number
  cpf: string
  nome_completo: string
  cargo?: string
  banco: string
  agencia: string
  conta: string
  status: string
}

export interface HistoricoCadastroItem {
  id: number
  action: string
  user_role: string
  details?: string
  alertas_ia?: string[]
  suspeita?: boolean
  created_at: string
}

export interface ColaboradorDetalhe extends Colaborador {
  historico: HistoricoCadastroItem[]
}

export interface CadastroSolicitacao {
  id: number
  entity_type: string
  entity_id: number
  operacao: string
  motivo?: string
  status: string
  alertas_ia?: string
  entidade_nome?: string
  created_at: string
}

export interface PagamentoAnexo {
  id: number
  pagamento_id: number
  tipo: string
  tipo_label: string
  nome_arquivo: string
  mime_type?: string
  created_at: string
}

export interface PagamentoAnaliseIA {
  id: number
  pagamento_id: number
  versao: number
  triggered_by: string
  risk_score: number
  risk_level: string
  ml_fraude_detectada: number
  ml_motivos?: string
  genai_parecer?: string
  created_at: string
}

export interface Pagamento {
  id: number
  remessa_id: number
  tipo_beneficiario?: string
  fornecedor_id?: number
  colaborador_id?: number
  beneficiario_nome?: string
  beneficiario_documento?: string
  tipo_despesa?: string
  competencia?: string
  valor: number
  documento_nome?: string
  fornecedor_nao_cadastrado?: number
  pf_nao_cadastrado?: number
  risk_score: number
  risk_level: string
  heuristic_flags?: string
  ml_score: number
  ml_fraude_detectada?: number
  ml_motivos?: string
  genai_parecer?: string
  dados_conferem: number
  revisado_gerente?: number
  revisado_documentos?: number
  revisado_valores?: number
  revisado_observacao?: string
  ponto_atencao_diretoria?: number
  anexos?: PagamentoAnexo[]
  documentos_completos?: boolean
  ia_analisado?: number
  codigo_pagamento?: string
  historico_analises?: PagamentoAnaliseIA[]
  fornecedor_razao_social?: string
  fornecedor_cnpj?: string
}

export interface PontoAtencao {
  pagamento_id: number
  remessa_id: number
  remessa_status?: string
  remessa_titulo?: string
  tipo_beneficiario: string
  tipo_despesa: string
  beneficiario_nome?: string
  beneficiario_documento?: string
  valor: number
  revisado_gerente: boolean
  revisado_observacao?: string
  gerente_justificativa?: string
  risk_score: number
  risk_level: string
  ml_fraude_detectada: boolean
  pf_nao_cadastrado: boolean
  fornecedor_nao_cadastrado: boolean
}

export interface Remessa {
  id: number
  titulo: string
  conta_bancaria_id?: number
  conta_nome?: string
  status: string
  valor_total: number
  risk_score_max: number
  risk_level: string
  gerente_justificativa?: string
  email_auditoria?: string
  motivo_devolucao?: string
  analise_ia_concluida?: number
  created_by: string
  created_at: string
  pagamentos: Pagamento[]
  saldo_conta_disponivel?: number
}

export interface DeteccaoIA {
  pagamento_id: number
  codigo_pagamento: string
  remessa_id: number
  remessa_status?: string
  valor: number
  beneficiario_nome?: string
  risk_score: number
  risk_level: string
  ml_fraude_detectada: boolean
  ml_motivos?: string
  genai_parecer?: string
  gerente_justificativa?: string
  motivo_devolucao?: string
  revisado_observacao?: string
  historico_analises: { versao: number; triggered_by: string; ml_fraude_detectada: boolean; risk_level: string; created_at: string }[]
}

export interface EventoFluxoIA {
  data: string | null
  perfil: string
  acao: string
  acao_label: string
  entity_type?: string
  entity_id?: number
  detalhes?: Record<string, unknown>
}

export interface AnaliseIAVersao {
  id: number
  versao: number
  triggered_by: string
  triggered_label?: string
  risk_score: number
  risk_level: string
  ml_score?: number
  ml_fraude_detectada: boolean
  ml_motivos?: string
  genai_parecer?: string
  dados_conferem?: boolean
  created_at: string | null
}

export interface HistoricoControleIAItem {
  pagamento_id: number
  codigo_pagamento: string
  remessa_id: number
  remessa_titulo?: string | null
  remessa_status?: string | null
  valor: number
  beneficiario_nome?: string
  beneficiario_documento?: string
  tipo_beneficiario?: string
  tipo_despesa?: string
  risk_score: number
  risk_level: string
  ml_score?: number
  ml_fraude_detectada: boolean
  ml_motivos?: string
  genai_parecer?: string
  gerente_justificativa?: string | null
  motivo_devolucao?: string | null
  revisado_observacao?: string
  eventos_fluxo: EventoFluxoIA[]
  analises_ia: AnaliseIAVersao[]
}

export interface HistoricoControleIAResponse {
  resumo: {
    total_registros: number
    fraudes_ml: number
    eventos_por_perfil?: Record<string, number>
  }
  itens: HistoricoControleIAItem[]
}

export interface MetricasIAResponse {
  resumo: {
    total_analises: number
    total_pagamentos_ia: number
    fraudes_ml: number
    atualizado_em?: string
  }
  por_perfil: { perfil: string; label: string; quantidade: number }[]
  por_mes: { mes: string; label: string; quantidade: number }[]
  por_tipo_deteccao: { tipo: string; label: string; quantidade: number }[]
}

export interface KPIs {
  total_remessas: number
  total_pagamentos: number
  valor_total_aprovado: number
  valor_bloqueado_ia: number
  fraudes_detectadas: number
  tempo_medio_aprovacao_horas: number
  pagamentos_nao_cadastrados: number
  pagamentos_pf_nao_cadastrados: number
  saldo_total_contas: number
}

export interface PagamentoPFNaoCadastrado {
  pagamento_id: number
  remessa_id: number
  remessa_status?: string
  nome?: string
  cpf?: string
  valor: number
  tipo_despesa?: string
  competencia?: string
  risk_score: number
  gerente_justificativa?: string
  genai_parecer?: string
}

export interface AuditLog {
  id: number
  entity_type: string
  entity_id: number
  action: string
  user_role: string
  ip_address: string
  details?: string
  created_at: string
}

export interface PagamentoNaoCadastrado {
  pagamento_id: number
  remessa_id: number
  remessa_status?: string
  valor: number
  fornecedor?: string
  cnpj?: string
  status_fornecedor?: string
  risk_score: number
  gerente_justificativa?: string
  genai_parecer?: string
}

export const apiClient = {
  health: () => api.get('/health'),
  contas: () => api.get<ContaBancaria[]>('/contas'),
  movimentosConta: (id: number) => api.get<MovimentoConta[]>(`/contas/${id}/movimentos`),
  registrarReceita: (id: number, valor: number, descricao: string) =>
    api.post<ContaBancaria>(`/contas/${id}/receita`, { valor, descricao }),
  fornecedores: (status?: string) =>
    api.get<Fornecedor[]>('/fornecedores', { params: { status } }),
  fornecedorDetalhe: (id: number) => api.get<FornecedorDetalhe>(`/fornecedores/${id}`),
  fornecedoresAtivos: () => api.get<Fornecedor[]>('/fornecedores/ativos'),
  fornecedoresAprovados: () => api.get<Fornecedor[]>('/fornecedores/ativos'),
  editarFornecedor: (id: number, data: Partial<Fornecedor>) =>
    api.put<Fornecedor>(`/fornecedores/${id}?user_role=gerente`, data),
  fornecedorStatus: (id: number, ativo: boolean, motivo?: string) =>
    api.patch<Fornecedor>(`/fornecedores/${id}/status`, { ativo, motivo, user_role: 'gerente' }),
  solicitarFornecedor: (id: number, operacao: 'editar' | 'excluir', dados?: Record<string, string>) =>
    api.post<{ id: number; alertas_ia?: string[] }>(`/fornecedores/${id}/solicitar`, {
      operacao,
      dados,
      user_role: 'analista',
    }),
  solicitacoesCadastro: () => api.get<CadastroSolicitacao[]>('/cadastros/solicitacoes'),
  decidirSolicitacao: (id: number, aprovada: boolean) =>
    api.patch(`/cadastros/solicitacoes/${id}`, { aprovada, user_role: 'gerente' }),
  colaboradores: (status?: string) =>
    api.get<Colaborador[]>('/colaboradores', { params: { status } }),
  colaboradoresAtivos: () => api.get<Colaborador[]>('/colaboradores/ativos'),
  colaboradoresAprovados: () => api.get<Colaborador[]>('/colaboradores/ativos'),
  colaboradorDetalhe: (id: number) => api.get<ColaboradorDetalhe>(`/colaboradores/${id}`),
  criarColaborador: (data: Omit<Colaborador, 'id' | 'status'>) =>
    api.post<Colaborador>('/colaboradores', data),
  aprovarColaborador: (id: number, aprovado: boolean) =>
    api.patch<Colaborador>(`/colaboradores/${id}/decisao`, { aprovado }),
  colaboradorStatus: (id: number, ativo: boolean, motivo?: string) =>
    api.patch<Colaborador>(`/colaboradores/${id}/status`, { ativo, motivo, user_role: 'gerente' }),
  editarColaborador: (id: number, data: Partial<Colaborador>) =>
    api.put<Colaborador>(`/colaboradores/${id}?user_role=gerente`, data),
  solicitarColaborador: (id: number, operacao: 'editar' | 'excluir', dados?: Record<string, string>) =>
    api.post<{ id: number; alertas_ia?: string[] }>(`/colaboradores/${id}/solicitar`, {
      operacao,
      dados,
      user_role: 'analista',
    }),
  criarFornecedor: (data: Omit<Fornecedor, 'id' | 'status'>) =>
    api.post<Fornecedor>('/fornecedores', data),
  aprovarFornecedor: (id: number, aprovado: boolean, motivo?: string) =>
    api.patch(`/fornecedores/${id}/decisao`, { aprovado, motivo_rejeicao: motivo }),
  remessas: (status?: string, historicoIa = false) =>
    api.get<Remessa[]>('/remessas', { params: { status, historico_ia: historicoIa } }),
  remessa: (id: number) => api.get<Remessa>(`/remessas/${id}`),
  pagamento: (id: number) => api.get<Pagamento>(`/pagamentos/${id}`),
  revisarPagamento: (
    id: number,
    body: { valores_ok: boolean; documentos_ok: boolean; observacao?: string }
  ) => api.post<Pagamento>(`/pagamentos/${id}/revisar`, { ...body, user_role: 'gerente' }),
  pagamentoDetalheExecutivo: (id: number) =>
    api.get<{ pagamento: Pagamento; remessa: Record<string, unknown> }>(
      `/dashboard/pagamentos/${id}/detalhe`
    ),
  pontosAtencao: () => api.get<PontoAtencao[]>('/dashboard/pontos-atencao'),
  criarRemessa: (titulo: string, conta_bancaria_id: number) =>
    api.post<Remessa>('/remessas', { titulo, conta_bancaria_id }),
  adicionarPagamento: (remessaId: number, form: FormData) =>
    api.post<Pagamento>(`/remessas/${remessaId}/pagamentos`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  enviarRemessa: (id: number) =>
    api.post<Remessa>(`/remessas/${id}/enviar`, { user_role: 'analista' }, { timeout: 300000 }),
  devolverRemessa: (id: number, motivo: string) =>
    api.post<Remessa>(`/remessas/${id}/devolver`, { motivo, user_role: 'gerente' }),
  reanalisarRemessa: (id: number) =>
    api.post<Remessa>(`/remessas/${id}/reanalisar-ia`, {}, { timeout: 300000 }),
  limparLancamentos: () => api.post('/admin/limpar-lancamentos'),
  deteccoesIA: () => api.get<DeteccaoIA[]>('/dashboard/deteccoes-ia'),
  historicoControleIA: (limit = 150) =>
    api.get<HistoricoControleIAResponse>('/dashboard/historico-controle-ia', { params: { limit } }),
  metricasIA: (meses = 6) =>
    api.get<MetricasIAResponse>('/dashboard/metricas-ia', { params: { meses } }),
  decisaoRemessa: (id: number, aprovado: boolean, justificativa?: string) =>
    api.post<Remessa>(`/remessas/${id}/decisao`, {
      aprovado,
      justificativa,
      user_role: 'gerente',
    }),
  mlStatus: () => api.get('/ml/status'),
  kpis: () => api.get<KPIs>('/dashboard/kpis'),
  auditoria: () => api.get<AuditLog[]>('/dashboard/auditoria'),
  alertas: () => api.get('/dashboard/alertas'),
  pagamentosNaoCadastrados: () =>
    api.get<PagamentoNaoCadastrado[]>('/dashboard/pagamentos-nao-cadastrados'),
  pagamentosPFNaoCadastrados: () =>
    api.get<PagamentoPFNaoCadastrado[]>('/dashboard/pagamentos-pf-nao-cadastrados'),
}

export default api
