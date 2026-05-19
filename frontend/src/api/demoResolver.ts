import type { InternalAxiosRequestConfig } from 'axios'
import type { Colaborador, ColaboradorDetalhe, Fornecedor, FornecedorDetalhe } from './client'
import {
  DEMO_SNAPSHOT,
  findPagamentoDemo,
  historicoControleDemo,
  remessasDemo,
} from './demoSnapshotData'

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
  {
    id: 2,
    cpf: '529.982.247-25',
    nome_completo: 'Carlos Eduardo Lima',
    cargo: 'Gerente de Projetos',
    banco: '001',
    agencia: '2002',
    conta: '20002-2',
    status: 'ativo',
  },
]

function dt(daysAgo: number): string {
  const d = new Date()
  d.setDate(d.getDate() - daysAgo)
  return d.toISOString()
}

function historicoCadastro(nome: string): ColaboradorDetalhe['historico'] {
  return [
    { id: 1, action: 'colaborador_cadastrado', user_role: 'analista', created_at: dt(120), details: `Cadastro ${nome}` },
    { id: 2, action: 'colaborador_aprovado', user_role: 'gerente', created_at: dt(115), alertas_ia: ['Conferir CPF'] },
    { id: 3, action: 'edicao_direta', user_role: 'gerente', created_at: dt(45), alertas_ia: ['ALERTA: Dados bancários alterados'] },
  ]
}

export function resolveDemoResponse(config: InternalAxiosRequestConfig): unknown {
  const url = (config.url || '').split('?')[0]
  const params = config.params || {}
  const status = params.status as string | undefined

  if (url.includes('/health')) return { status: 'ok', modo: 'demonstracao' }
  if (url.endsWith('/contas') && !url.includes('/movimentos')) return DEMO_SNAPSHOT.contas
  if (url.includes('/movimentos')) return DEMO_SNAPSHOT.movimentos
  if (url.includes('/fornecedores/ativos')) return FORN.filter((f) => f.status === 'ativo')
  if (url.match(/\/fornecedores\/\d+$/)) {
    const f = FORN.find((x) => url.includes(String(x.id))) || FORN[0]
    return {
      ...f,
      historico: [
        { id: 1, action: 'fornecedor_cadastrado', user_role: 'analista', created_at: dt(100) },
        { id: 2, action: 'fornecedor_aprovado', user_role: 'gerente', created_at: dt(95), alertas_ia: ['Conferir CNPJ'] },
      ],
    } satisfies FornecedorDetalhe
  }
  if (url.includes('/fornecedores'))
    return status ? FORN.filter((f) => f.status === status) : FORN
  if (url.includes('/colaboradores/ativos')) return COLS.filter((c) => c.status === 'ativo')
  if (url.match(/\/colaboradores\/\d+$/)) {
    const c = COLS[0]
    return { ...c, historico: historicoCadastro(c.nome_completo) } satisfies ColaboradorDetalhe
  }
  if (url.includes('/colaboradores')) return COLS
  if (url.includes('/cadastros/solicitacoes'))
    return [
      {
        id: 1,
        entity_type: 'fornecedor',
        entity_id: 7,
        operacao: 'editar',
        status: 'pendente',
        entidade_nome: 'Fornecedor Novo Ltda',
        alertas_ia: '["ALERTA: Alteração cadastral"]',
        created_at: dt(5),
      },
    ]
  if (url.includes('/remessas')) {
    return remessasDemo(status)
  }
  if (url.includes('/pagamentos/')) {
    const id = parseInt(url.split('/').pop() || '0', 10)
    return findPagamentoDemo(id) || findPagamentoDemo(91)
  }
  if (url.includes('/dashboard/kpis')) return DEMO_SNAPSHOT.kpis
  if (url.includes('/dashboard/auditoria')) return DEMO_SNAPSHOT.auditoria
  if (url.includes('/metricas-ia')) return DEMO_SNAPSHOT.metricasIA
  if (url.includes('/historico-controle-ia')) {
    const limit = Math.min(Number(params.limit) || 150, 300)
    return historicoControleDemo(limit)
  }
  if (url.includes('/deteccoes-ia')) return DEMO_SNAPSHOT.deteccoesIA
  if (url.includes('/pontos-atencao')) return DEMO_SNAPSHOT.pontosAtencao
  if (url.includes('/pagamentos-nao-cadastrados')) return DEMO_SNAPSHOT.pagamentosNaoCadastrados
  if (url.includes('/pagamentos-pf-nao-cadastrados')) return DEMO_SNAPSHOT.pagamentosPFNaoCadastrados
  if (url.includes('/ml/status')) return { modelo_disponivel: true, modo: 'demonstracao' }
  if (url.includes('/alertas')) return DEMO_SNAPSHOT.alertas

  if (config.method === 'post' || config.method === 'patch' || config.method === 'put') {
    if (url.includes('/remessas')) {
      const ag = remessasDemo('aguardando_gerente')[0]
      return ag || { ok: true, demo: true }
    }
    return { ok: true, demo: true }
  }

  return []
}
