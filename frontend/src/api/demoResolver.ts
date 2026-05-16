import type { InternalAxiosRequestConfig } from 'axios'
import type {
  Colaborador,
  ContaBancaria,
  DeteccaoIA,
  Fornecedor,
  KPIs,
  Pagamento,
  Remessa,
} from './client'

const FORN: Fornecedor[] = [
  {
    id: 1,
    cnpj: '12.345.678/0001-90',
    razao_social: 'Tech Solutions Ltda',
    banco: '341',
    agencia: '1234',
    conta: '56789-0',
    status: 'ativo',
  },
  {
    id: 2,
    cnpj: '98.765.432/0001-10',
    razao_social: 'Logística Brasil S.A.',
    banco: '001',
    agencia: '4321',
    conta: '98765-4',
    status: 'ativo',
  },
  {
    id: 7,
    cnpj: '11.222.333/0001-44',
    razao_social: 'Fornecedor Novo Ltda',
    banco: '237',
    agencia: '0001',
    conta: '12345-6',
    status: 'pendente',
  },
]

const COLS: Colaborador[] = [
  {
    id: 1,
    cpf: '390.533.447-05',
    nome_completo: 'Ana Paula Ferreira',
    cargo: 'Analista Financeiro',
    banco: '341',
    agencia: '1001',
    conta: '10001-1',
    status: 'ativo',
  },
]

const CONTAS: ContaBancaria[] = [
  {
    id: 1,
    nome: 'Conta Operacional Principal',
    banco: '341',
    agencia: '1001',
    conta: '50001-0',
    saldo: 1_250_000,
    ativa: 1,
  },
]

const PAG_CATALOGO: Pagamento = {
  id: 101,
  remessa_id: 26,
  tipo_beneficiario: 'pj',
  fornecedor_id: 1,
  beneficiario_nome: 'Tech Solutions Ltda',
  beneficiario_documento: '12.345.678/0001-90',
  fornecedor_razao_social: 'Tech Solutions Ltda',
  tipo_despesa: 'fornecedor',
  valor: 287_500,
  risk_score: 0.88,
  risk_level: 'alto',
  ml_score: 0.82,
  ml_fraude_detectada: 1,
  ml_motivos: JSON.stringify(['Modelo XGBoost classificou FRAUDE (82%).']),
  genai_parecer: 'ALERTA IA: revisão documental reforçada.',
  dados_conferem: 1,
  ia_analisado: 1,
  ponto_atencao_diretoria: 1,
  codigo_pagamento: 'PAY-000101',
  historico_analises: [],
}

const REM_CATALOGO: Remessa = {
  id: 26,
  titulo: 'Catálogo MBA — Todos os tipos de detecção IA',
  conta_bancaria_id: 1,
  conta_nome: 'Conta Operacional Principal',
  status: 'aguardando_gerente',
  valor_total: 892_000,
  risk_score_max: 0.88,
  risk_level: 'alto',
  analise_ia_concluida: 1,
  created_by: 'analista',
  created_at: new Date().toISOString(),
  pagamentos: [PAG_CATALOGO],
  saldo_conta_disponivel: 1_250_000,
}

const REM_DEVOLVIDA: Remessa = {
  ...REM_CATALOGO,
  id: 12,
  titulo: 'Remessa devolvida — correção documental',
  status: 'devolvida_analista',
  motivo_devolucao: 'Ajustar NF do pagamento com maior score ML.',
  pagamentos: [],
}

const DETECCOES: DeteccaoIA[] = [
  {
    pagamento_id: 101,
    codigo_pagamento: 'PAY-000101',
    remessa_id: 26,
    remessa_status: 'aguardando_gerente',
    valor: 287_500,
    beneficiario_nome: 'Tech Solutions Ltda',
    risk_score: 0.88,
    risk_level: 'alto',
    ml_fraude_detectada: true,
    ml_motivos: 'Modelo XGBoost — fraude',
    genai_parecer: 'Bloquear até revisão gerencial.',
    historico_analises: [],
  },
]

const KPIS: KPIs = {
  total_remessas: 27,
  total_pagamentos: 107,
  valor_total_aprovado: 4_250_000,
  valor_bloqueado_ia: 320_000,
  fraudes_detectadas: 12,
  tempo_medio_aprovacao_horas: 4.5,
  pagamentos_nao_cadastrados: 2,
  pagamentos_pf_nao_cadastrados: 1,
  saldo_total_contas: 2_250_000,
}

export function resolveDemoResponse(config: InternalAxiosRequestConfig): unknown {
  const url = (config.url || '').split('?')[0]
  const params = config.params || {}
  const status = params.status as string | undefined

  if (url.includes('/health')) return { status: 'ok', modo: 'demonstracao' }
  if (url.endsWith('/contas') && !url.includes('/movimentos')) return CONTAS
  if (url.includes('/movimentos')) return []
  if (url.includes('/fornecedores/ativos'))
    return FORN.filter((f) => f.status === 'ativo')
  if (url.match(/\/fornecedores\/\d+$/))
    return { ...(FORN.find((f) => url.includes(String(f.id))) || FORN[0]), historico: [] }
  if (url.includes('/fornecedores'))
    return status ? FORN.filter((f) => f.status === status) : FORN
  if (url.includes('/colaboradores/ativos'))
    return COLS.filter((c) => c.status === 'ativo')
  if (url.match(/\/colaboradores\/\d+$/))
    return { ...(COLS[0]), historico: [] }
  if (url.includes('/colaboradores')) return COLS
  if (url.includes('/cadastros/solicitacoes')) return []
  if (url.includes('/remessas')) {
    if (status === 'aguardando_gerente') return [REM_CATALOGO]
    if (status === 'devolvida_analista') return [REM_DEVOLVIDA]
    return [REM_CATALOGO, REM_DEVOLVIDA]
  }
  if (url.includes('/pagamentos/')) return PAG_CATALOGO
  if (url.includes('/dashboard/kpis')) return KPIS
  if (url.includes('/dashboard/auditoria'))
    return [
      {
        id: 1,
        entity_type: 'remessa',
        entity_id: 26,
        action: 'catalogo_fraude_criado',
        user_role: 'sistema',
        ip_address: '127.0.0.1',
        details: '{"cenarios":16}',
        created_at: new Date().toISOString(),
      },
    ]
  if (url.includes('/deteccoes-ia')) return DETECCOES
  if (url.includes('/pontos-atencao')) return []
  if (url.includes('/pagamentos-nao-cadastrados')) return []
  if (url.includes('/pagamentos-pf-nao-cadastrados')) return []
  if (url.includes('/ml/status'))
    return { modelo_disponivel: true, modo: 'demonstracao' }
  if (url.includes('/alertas')) return []

  if (config.method === 'post' || config.method === 'patch' || config.method === 'put') {
    if (url.includes('/remessas')) return { ...REM_CATALOGO, status: 'aguardando_gerente' }
    return { ok: true, demo: true }
  }

  return []
}
