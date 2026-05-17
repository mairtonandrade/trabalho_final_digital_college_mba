import type { InternalAxiosRequestConfig } from 'axios'
import type {
  AuditLog,
  Colaborador,
  ColaboradorDetalhe,
  DeteccaoIA,
  Fornecedor,
  FornecedorDetalhe,
  HistoricoControleIAResponse,
  KPIs,
  MetricasIAResponse,
  MovimentoConta,
  Pagamento,
  PagamentoNaoCadastrado,
  PagamentoPFNaoCadastrado,
  PontoAtencao,
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

const CONTAS = [
  { id: 1, nome: 'Conta Operacional Principal', banco: '341', agencia: '1001', conta: '50001-0', saldo: 1_180_000, ativa: 1 },
  { id: 2, nome: 'Conta Folha de Pagamento', banco: '001', agencia: '2002', conta: '30002-1', saldo: 355_000, ativa: 1 },
  { id: 3, nome: 'Conta Fornecedores', banco: '237', agencia: '3300', conta: '88001-5', saldo: 590_000, ativa: 1 },
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

const PAG_FRAUDE: Pagamento = {
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
  ml_motivos: '["Modelo XGBoost classificou FRAUDE (82%).","Valor elevado acima do padrão."]',
  genai_parecer: 'ALERTA IA: revisão documental reforçada antes da liberação.',
  dados_conferem: 1,
  ia_analisado: 1,
  ponto_atencao_diretoria: 1,
  revisado_gerente: 1,
  revisado_documentos: 1,
  revisado_valores: 1,
  revisado_observacao: 'Conferido — exceção aprovada com documentação complementar.',
  codigo_pagamento: 'PAY-000101',
  historico_analises: [
    { id: 1, pagamento_id: 101, versao: 1, triggered_by: 'envio_gerente', risk_score: 0.88, risk_level: 'alto', ml_fraude_detectada: 1, created_at: dt(2) },
    { id: 2, pagamento_id: 101, versao: 2, triggered_by: 'reanalise_gerente', risk_score: 0.72, risk_level: 'alto', ml_fraude_detectada: 1, created_at: dt(1) },
  ],
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
  created_at: dt(1),
  pagamentos: [PAG_FRAUDE],
  saldo_conta_disponivel: 1_180_000,
}

const REM_LIBERADA: Remessa = {
  id: 8,
  titulo: 'Fornecedores estratégicos — ciclo 03/2026',
  conta_bancaria_id: 1,
  conta_nome: 'Conta Operacional Principal',
  status: 'liberada_banco',
  valor_total: 245_000,
  risk_score_max: 0.42,
  risk_level: 'medio',
  analise_ia_concluida: 1,
  created_by: 'analista',
  created_at: dt(45),
  gerente_justificativa: 'Liberação após revisão documental.',
  pagamentos: [],
  saldo_conta_disponivel: 1_180_000,
}

const REM_DEVOLVIDA: Remessa = {
  id: 12,
  titulo: 'Remessa devolvida — correção documental',
  conta_bancaria_id: 1,
  conta_nome: 'Conta Operacional Principal',
  status: 'devolvida_analista',
  motivo_devolucao: 'Ajustar NF do pagamento com maior score ML.',
  valor_total: 128_000,
  risk_score_max: 0.71,
  risk_level: 'alto',
  analise_ia_concluida: 1,
  created_by: 'analista',
  created_at: dt(20),
  pagamentos: [],
  saldo_conta_disponivel: 1_180_000,
}

const DETECCOES: DeteccaoIA[] = [
  {
    pagamento_id: 101,
    codigo_pagamento: 'PAY-000101',
    remessa_id: 26,
    remessa_status: 'aguardando_gerente',
    created_at: dt(2),
    valor: 287_500,
    beneficiario_nome: 'Tech Solutions Ltda',
    risk_score: 0.88,
    risk_level: 'alto',
    ml_fraude_detectada: true,
    ml_motivos: 'Modelo XGBoost — fraude 82%',
    genai_parecer: 'Bloquear até revisão gerencial.',
    historico_analises: [
      { versao: 1, triggered_by: 'envio_gerente', ml_fraude_detectada: true, risk_level: 'alto', created_at: dt(2) },
      { versao: 2, triggered_by: 'reanalise_gerente', ml_fraude_detectada: true, risk_level: 'alto', created_at: dt(1) },
    ],
  },
  {
    pagamento_id: 42,
    codigo_pagamento: 'PAY-000042',
    remessa_id: 8,
    remessa_status: 'liberada_banco',
    created_at: dt(45),
    valor: 215_000,
    beneficiario_nome: 'Logística Brasil S.A.',
    risk_score: 0.76,
    risk_level: 'alto',
    ml_fraude_detectada: true,
    ml_motivos: 'Valor acima do limite operacional',
    genai_parecer: 'Liberado com justificativa do gerente.',
    gerente_justificativa: 'Documentação validada com área solicitante.',
    historico_analises: [{ versao: 1, triggered_by: 'envio_gerente', ml_fraude_detectada: true, risk_level: 'alto', created_at: dt(45) }],
  },
  {
    pagamento_id: 55,
    codigo_pagamento: 'PAY-000055',
    remessa_id: 12,
    remessa_status: 'devolvida_analista',
    valor: 98_000,
    beneficiario_nome: 'Energia Verde Comercial',
    risk_score: 0.58,
    risk_level: 'medio',
    ml_fraude_detectada: false,
    motivo_devolucao: 'Ajustar documentação do pagamento com maior score ML.',
    historico_analises: [{ versao: 1, triggered_by: 'envio_gerente', ml_fraude_detectada: false, risk_level: 'medio', created_at: dt(20) }],
  },
]

function mesLabel(monthsAgo: number): { mes: string; label: string } {
  const d = new Date()
  d.setMonth(d.getMonth() - monthsAgo)
  const mes = d.toISOString().slice(0, 7)
  const labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
  return { mes, label: `${labels[d.getMonth()]}/${String(d.getFullYear()).slice(2)}` }
}

const METRICAS_IA: MetricasIAResponse = {
  resumo: { total_analises: 94, total_pagamentos_ia: 78, fraudes_ml: 12 },
  por_perfil: [
    { perfil: 'analista', label: 'Analista', quantidade: 62 },
    { perfil: 'gerente', label: 'Gerente', quantidade: 24 },
    { perfil: 'sistema', label: 'Sistema / IA', quantidade: 8 },
  ],
  por_mes: [5, 4, 3, 2, 1, 0].map((ago, i) => ({
    ...mesLabel(ago),
    quantidade: [8, 14, 18, 22, 20, 12][i],
  })),
  por_tipo_deteccao: [
    { tipo: 'fraude_ml', label: 'Fraude ML', quantidade: 12 },
    { tipo: 'pj_nao_cadastrado', label: 'PJ não cadastrado', quantidade: 5 },
    { tipo: 'pf_nao_cadastrado', label: 'PF não cadastrado', quantidade: 3 },
    { tipo: 'risco_alto', label: 'Risco alto', quantidade: 18 },
    { tipo: 'risco_medio', label: 'Risco médio', quantidade: 24 },
    { tipo: 'conformidade', label: 'Conformidade', quantidade: 16 },
  ],
}

const HISTORICO_CONTROLE_IA: HistoricoControleIAResponse = {
  resumo: {
    total_registros: 4,
    fraudes_ml: 2,
    eventos_por_perfil: { analista: 8, sistema: 4, gerente: 5, diretoria: 1 },
  },
  itens: [
    {
      pagamento_id: 101,
      codigo_pagamento: 'PAY-000101',
      remessa_id: 26,
      remessa_titulo: 'Catálogo MBA — Cenários de fraude',
      remessa_status: 'aguardando_gerente',
      valor: 287_500,
      beneficiario_nome: 'Tech Solutions Ltda',
      beneficiario_documento: '12.345.678/0001-90',
      tipo_beneficiario: 'pj',
      tipo_despesa: 'fornecedor',
      risk_score: 0.88,
      risk_level: 'alto',
      ml_fraude_detectada: true,
      ml_motivos: 'Modelo XGBoost — fraude 82%; valor acima do padrão',
      genai_parecer: 'Bloquear até revisão gerencial com documentação complementar.',
      gerente_justificativa: null,
      motivo_devolucao: null,
      eventos_fluxo: [
        { data: dt(5), perfil: 'analista', acao: 'remessa_criada', acao_label: 'Remessa criada (Analista)' },
        { data: dt(3), perfil: 'analista', acao: 'remessa_enviada_ia', acao_label: 'Envio para análise IA em lote (Analista)' },
        { data: dt(2), perfil: 'sistema', acao: 'ia_analise_concluida', acao_label: 'Análise IA concluída — ML + GenAI (Sistema)' },
        { data: dt(2), perfil: 'sistema', acao: 'aguardando_aprovacao_gerente', acao_label: 'Aguardando revisão do Gerente' },
      ],
      analises_ia: [
        {
          id: 1,
          versao: 1,
          triggered_by: 'envio_gerente',
          triggered_label: 'Envio da remessa ao gerente (Analista)',
          risk_score: 0.88,
          risk_level: 'alto',
          ml_fraude_detectada: true,
          ml_motivos: 'Fraude ML 82%',
          genai_parecer: 'Revisão documental reforçada.',
          created_at: dt(2),
        },
        {
          id: 2,
          versao: 2,
          triggered_by: 'reanalise_gerente',
          triggered_label: 'Reanálise solicitada pelo Gerente',
          risk_score: 0.72,
          risk_level: 'alto',
          ml_fraude_detectada: true,
          created_at: dt(1),
        },
      ],
    },
    {
      pagamento_id: 42,
      codigo_pagamento: 'PAY-000042',
      remessa_id: 8,
      remessa_titulo: 'Fornecedores Q4 — liberada',
      remessa_status: 'liberada_banco',
      valor: 215_000,
      beneficiario_nome: 'Logística Brasil S.A.',
      beneficiario_documento: '98.765.432/0001-10',
      tipo_beneficiario: 'pj',
      tipo_despesa: 'fornecedor',
      risk_score: 0.76,
      risk_level: 'alto',
      ml_fraude_detectada: true,
      ml_motivos: 'Valor acima do limite operacional',
      genai_parecer: 'Liberado com justificativa do gerente.',
      gerente_justificativa: 'Documentação validada com área solicitante.',
      motivo_devolucao: null,
      eventos_fluxo: [
        { data: dt(50), perfil: 'analista', acao: 'remessa_criada', acao_label: 'Remessa criada (Analista)' },
        { data: dt(48), perfil: 'analista', acao: 'remessa_enviada_ia', acao_label: 'Envio para análise IA em lote (Analista)' },
        { data: dt(47), perfil: 'sistema', acao: 'ia_analise_concluida', acao_label: 'Análise IA concluída — ML + GenAI (Sistema)' },
        { data: dt(46), perfil: 'gerente', acao: 'remessa_liberada', acao_label: 'Remessa liberada para banco (Gerente)' },
        { data: dt(44), perfil: 'diretoria', acao: 'visao_diretoria', acao_label: 'Registro de acompanhamento (Diretoria)' },
      ],
      analises_ia: [
        {
          id: 3,
          versao: 1,
          triggered_by: 'envio_gerente',
          triggered_label: 'Envio da remessa ao gerente (Analista)',
          risk_score: 0.76,
          risk_level: 'alto',
          ml_fraude_detectada: true,
          created_at: dt(47),
        },
      ],
    },
    {
      pagamento_id: 55,
      codigo_pagamento: 'PAY-000055',
      remessa_id: 12,
      remessa_titulo: 'Utilidades — devolvida',
      remessa_status: 'devolvida_analista',
      valor: 98_000,
      beneficiario_nome: 'Energia Verde Comercial',
      tipo_beneficiario: 'pj',
      tipo_despesa: 'fornecedor',
      risk_score: 0.58,
      risk_level: 'medio',
      ml_fraude_detectada: false,
      genai_parecer: 'Score moderado — conferir nota fiscal.',
      gerente_justificativa: null,
      motivo_devolucao: 'Ajustar documentação do pagamento com maior score ML.',
      eventos_fluxo: [
        { data: dt(25), perfil: 'analista', acao: 'remessa_criada', acao_label: 'Remessa criada (Analista)' },
        { data: dt(22), perfil: 'analista', acao: 'remessa_enviada_ia', acao_label: 'Envio para análise IA em lote (Analista)' },
        { data: dt(21), perfil: 'sistema', acao: 'ia_analise_concluida', acao_label: 'Análise IA concluída — ML + GenAI (Sistema)' },
        { data: dt(20), perfil: 'gerente', acao: 'remessa_devolvida', acao_label: 'Devolvida ao Analista para correção (Gerente)' },
      ],
      analises_ia: [
        {
          id: 4,
          versao: 1,
          triggered_by: 'envio_gerente',
          triggered_label: 'Envio da remessa ao gerente (Analista)',
          risk_score: 0.58,
          risk_level: 'medio',
          ml_fraude_detectada: false,
          created_at: dt(21),
        },
      ],
    },
    {
      pagamento_id: 88,
      codigo_pagamento: 'PAY-000088',
      remessa_id: 15,
      remessa_titulo: 'Exceção PJ não cadastrado',
      remessa_status: 'liberada_banco',
      valor: 8_500,
      beneficiario_nome: 'Fornecedor Novo Ltda',
      tipo_beneficiario: 'pj',
      tipo_despesa: 'fornecedor',
      risk_score: 0.62,
      risk_level: 'medio',
      ml_fraude_detectada: false,
      genai_parecer: 'Fornecedor fora da whitelist — exceção documentada.',
      gerente_justificativa: 'Exceção documentada — contrato emergencial.',
      eventos_fluxo: [
        { data: dt(30), perfil: 'analista', acao: 'remessa_criada', acao_label: 'Remessa criada (Analista)' },
        { data: dt(28), perfil: 'analista', acao: 'remessa_enviada_ia', acao_label: 'Envio para análise IA em lote (Analista)' },
        { data: dt(27), perfil: 'sistema', acao: 'ia_analise_concluida', acao_label: 'Análise IA concluída — ML + GenAI (Sistema)' },
        { data: dt(26), perfil: 'gerente', acao: 'remessa_liberada', acao_label: 'Remessa liberada para banco (Gerente)' },
      ],
      analises_ia: [
        {
          id: 5,
          versao: 1,
          triggered_by: 'envio_gerente',
          triggered_label: 'Envio da remessa ao gerente (Analista)',
          risk_score: 0.62,
          risk_level: 'medio',
          ml_fraude_detectada: false,
          genai_parecer: 'PJ não cadastrado — limite R$ 10.000 respeitado.',
          created_at: dt(27),
        },
      ],
    },
  ],
}

const AUDITORIA: AuditLog[] = [
  { id: 1, entity_type: 'remessa', entity_id: 26, action: 'remessa_enviada_ia', user_role: 'analista', ip_address: '127.0.0.1', created_at: dt(1) },
  { id: 2, entity_type: 'pagamento', entity_id: 101, action: 'ia_analise_concluida', user_role: 'sistema', ip_address: '127.0.0.1', details: '{"ml_fraude":true}', created_at: dt(1) },
  { id: 3, entity_type: 'remessa', entity_id: 8, action: 'remessa_liberada', user_role: 'gerente', ip_address: '127.0.0.1', created_at: dt(44) },
  { id: 4, entity_type: 'remessa', entity_id: 8, action: 'visao_diretoria', user_role: 'diretoria', ip_address: '127.0.0.1', created_at: dt(44) },
  { id: 5, entity_type: 'fornecedor', entity_id: 7, action: 'fornecedor_pendente', user_role: 'analista', ip_address: '127.0.0.1', created_at: dt(60) },
  { id: 6, entity_type: 'fornecedor', entity_id: 1, action: 'fornecedor_aprovado', user_role: 'gerente', ip_address: '127.0.0.1', created_at: dt(90) },
  { id: 7, entity_type: 'colaborador', entity_id: 1, action: 'colaborador_aprovado', user_role: 'gerente', ip_address: '127.0.0.1', created_at: dt(100) },
  { id: 8, entity_type: 'fornecedor', entity_id: 2, action: 'solicitacao_edicao', user_role: 'analista', ip_address: '127.0.0.1', created_at: dt(30) },
  { id: 9, entity_type: 'remessa', entity_id: 12, action: 'remessa_devolvida', user_role: 'gerente', ip_address: '127.0.0.1', created_at: dt(19) },
  { id: 10, entity_type: 'pagamento', entity_id: 42, action: 'ia_analise_concluida', user_role: 'sistema', ip_address: '127.0.0.1', created_at: dt(45) },
]

const PONTOS: PontoAtencao[] = [
  {
    pagamento_id: 101,
    remessa_id: 26,
    remessa_status: 'aguardando_gerente',
    remessa_titulo: REM_CATALOGO.titulo,
    tipo_beneficiario: 'pj',
    tipo_despesa: 'fornecedor',
    beneficiario_nome: 'Tech Solutions Ltda',
    beneficiario_documento: '12.345.678/0001-90',
    valor: 287_500,
    revisado_gerente: true,
    revisado_observacao: 'Conferido pelo gerente.',
    risk_score: 0.88,
    risk_level: 'alto',
    ml_fraude_detectada: true,
    pf_nao_cadastrado: false,
    fornecedor_nao_cadastrado: false,
  },
]

const MOVIMENTOS: MovimentoConta[] = [
  { id: 1, conta_id: 1, tipo: 'receita', valor: 1_250_000, saldo_apos: 1_250_000, descricao: 'Saldo inicial', created_at: dt(180) },
  { id: 2, conta_id: 1, tipo: 'debito', valor: 70_000, saldo_apos: 1_180_000, descricao: 'Remessa #8 liberada', remessa_id: 8, created_at: dt(44) },
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
  saldo_total_contas: 2_125_000,
}

const NAO_CAD: PagamentoNaoCadastrado[] = [
  {
    pagamento_id: 88,
    remessa_id: 15,
    remessa_status: 'liberada_banco',
    valor: 8_500,
    fornecedor: 'Fornecedor Novo Ltda',
    cnpj: '11.222.333/0001-44',
    status_fornecedor: 'pendente',
    risk_score: 0.62,
    gerente_justificativa: 'Exceção documentada — contrato emergencial.',
  },
]

const PF_NAO_CAD: PagamentoPFNaoCadastrado[] = [
  {
    pagamento_id: 91,
    remessa_id: 18,
    remessa_status: 'aguardando_gerente',
    nome: 'Prestador Autônomo Externo',
    cpf: '999.888.777-66',
    valor: 7_200,
    tipo_despesa: 'outros',
    risk_score: 0.58,
    gerente_justificativa: 'Pendente validação RH.',
  },
]

export function resolveDemoResponse(config: InternalAxiosRequestConfig): unknown {
  const url = (config.url || '').split('?')[0]
  const params = config.params || {}
  const status = params.status as string | undefined

  if (url.includes('/health')) return { status: 'ok', modo: 'demonstracao' }
  if (url.endsWith('/contas') && !url.includes('/movimentos')) return CONTAS
  if (url.includes('/movimentos')) return MOVIMENTOS
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
    if (status === 'aguardando_gerente') return [REM_CATALOGO]
    if (status === 'devolvida_analista') return [REM_DEVOLVIDA]
    if (status === 'liberada_banco') return [REM_LIBERADA]
    if (params.historico_ia) {
      const pagLiberada: Pagamento = {
        ...PAG_FRAUDE,
        id: 42,
        remessa_id: 8,
        ml_fraude_detectada: 1,
        created_at: dt(45),
      }
      const pagDevolvido: Pagamento = {
        ...PAG_FRAUDE,
        id: 55,
        remessa_id: 12,
        valor: 98_000,
        ml_fraude_detectada: 0,
        risk_level: 'medio',
        risk_score: 0.58,
        created_at: dt(20),
      }
      return [
        REM_CATALOGO,
        { ...REM_LIBERADA, pagamentos: [pagLiberada] },
        { ...REM_DEVOLVIDA, pagamentos: [pagDevolvido] },
      ]
    }
    return [REM_CATALOGO, REM_DEVOLVIDA, REM_LIBERADA]
  }
  if (url.includes('/pagamentos/')) return PAG_FRAUDE
  if (url.includes('/dashboard/kpis')) return KPIS
  if (url.includes('/dashboard/auditoria')) return AUDITORIA
  if (url.includes('/metricas-ia')) return METRICAS_IA
  if (url.includes('/historico-controle-ia')) return HISTORICO_CONTROLE_IA
  if (url.includes('/deteccoes-ia')) return DETECCOES
  if (url.includes('/pontos-atencao')) return PONTOS
  if (url.includes('/pagamentos-nao-cadastrados')) return NAO_CAD
  if (url.includes('/pagamentos-pf-nao-cadastrados')) return PF_NAO_CAD
  if (url.includes('/ml/status')) return { modelo_disponivel: true, modo: 'demonstracao' }
  if (url.includes('/alertas'))
    return [
      {
        id: 101,
        remessa_id: 26,
        valor: 287_500,
        risk_score: 0.88,
        risk_level: 'alto',
        genai_parecer: PAG_FRAUDE.genai_parecer,
        fornecedor_nao_cadastrado: false,
        fornecedor_razao_social: 'Tech Solutions Ltda',
        fornecedor_status: 'ativo',
      },
    ]

  if (config.method === 'post' || config.method === 'patch' || config.method === 'put') {
    if (url.includes('/remessas')) return { ...REM_CATALOGO, status: 'aguardando_gerente' }
    return { ok: true, demo: true }
  }

  return []
}
