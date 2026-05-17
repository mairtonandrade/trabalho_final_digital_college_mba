import type { HistoricoControleIAItem, MetricasIAResponse } from '../api/client'

export interface PeriodoFiltro {
  de: string
  ate: string
}

export const PERIODO_TODOS: PeriodoFiltro = { de: '', ate: '' }

const MESES_PT = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

export function periodoAtivo(periodo: PeriodoFiltro): boolean {
  return Boolean(periodo.de || periodo.ate)
}

export function chaveMes(iso: string | null | undefined): string | null {
  if (!iso) return null
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return null
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

export function rotuloMes(chave: string): string {
  const [ano, mes] = chave.split('-')
  return `${MESES_PT[parseInt(mes, 10) - 1]}/${ano.slice(2)}`
}

export function toDateInput(d: Date): string {
  return d.toISOString().slice(0, 10)
}

export function boundsDoMes(chave: string): PeriodoFiltro {
  const [ano, mes] = chave.split('-').map(Number)
  const de = new Date(ano, mes - 1, 1)
  const ate = new Date(ano, mes, 0)
  return { de: toDateInput(de), ate: toDateInput(ate) }
}

export function presetUltimosDias(dias: number): PeriodoFiltro {
  const ate = new Date()
  const de = new Date()
  de.setDate(de.getDate() - dias)
  return { de: toDateInput(de), ate: toDateInput(ate) }
}

export function buildMesesOpcoes(
  datas: (string | null | undefined)[],
  max = 12
): { value: string; label: string }[] {
  const set = new Set<string>()
  for (const d of datas) {
    const k = chaveMes(d)
    if (k) set.add(k)
  }
  return Array.from(set)
    .sort()
    .reverse()
    .slice(0, max)
    .map((value) => ({ value, label: rotuloMes(value) }))
}

export function limitesPeriodo(datas: (string | null | undefined)[]): PeriodoFiltro {
  const validas = datas
    .map((d) => (d ? new Date(d).getTime() : NaN))
    .filter((t) => !Number.isNaN(t))
  if (!validas.length) return PERIODO_TODOS
  const min = new Date(Math.min(...validas))
  const max = new Date(Math.max(...validas))
  return { de: toDateInput(min), ate: toDateInput(max) }
}

export function noPeriodo(iso: string | null | undefined, periodo: PeriodoFiltro): boolean {
  if (!periodoAtivo(periodo)) return true
  if (!iso) return false
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return false
  const t = d.getTime()
  if (periodo.de) {
    const ini = new Date(periodo.de)
    ini.setHours(0, 0, 0, 0)
    if (t < ini.getTime()) return false
  }
  if (periodo.ate) {
    const fim = new Date(periodo.ate)
    fim.setHours(23, 59, 59, 999)
    if (t > fim.getTime()) return false
  }
  return true
}

/** @deprecated use noPeriodo */
export function noMes(iso: string | null | undefined, mes: string): boolean {
  if (!mes || mes === 'todos') return true
  return chaveMes(iso) === mes
}

export const MES_TODOS = 'todos'

export function isFraudeMl(item: { ml_fraude_detectada?: boolean | number | null }): boolean {
  return Boolean(item.ml_fraude_detectada)
}

export function historicoNoPeriodo(item: HistoricoControleIAItem, periodo: PeriodoFiltro): boolean {
  if (!periodoAtivo(periodo)) return true
  if (noPeriodo(item.created_at, periodo)) return true
  if (item.eventos_fluxo?.some((e) => noPeriodo(e.data, periodo))) return true
  if (item.analises_ia?.some((a) => noPeriodo(a.created_at, periodo))) return true
  return false
}

/** @deprecated use historicoNoPeriodo */
export function historicoNoMes(item: HistoricoControleIAItem, mes: string): boolean {
  if (!mes || mes === MES_TODOS) return true
  return historicoNoPeriodo(item, boundsDoMes(mes))
}

export function dataPagamentoOuRemessa(
  pagamento: { created_at?: string; historico_analises?: { created_at?: string }[] },
  remessa?: { created_at?: string }
): string | undefined {
  if (pagamento.created_at) return pagamento.created_at
  const h = pagamento.historico_analises?.[0]?.created_at
  if (h) return h
  return remessa?.created_at
}

export function remessaNoPeriodo(
  remessa: {
    created_at?: string
    pagamentos: { created_at?: string; historico_analises?: { created_at?: string }[] }[]
  },
  periodo: PeriodoFiltro
): boolean {
  if (!periodoAtivo(periodo)) return true
  if (noPeriodo(remessa.created_at, periodo)) return true
  return remessa.pagamentos.some((p) => noPeriodo(dataPagamentoOuRemessa(p, remessa), periodo))
}

/** @deprecated use remessaNoPeriodo */
export function remessaNoMes(
  remessa: {
    created_at?: string
    pagamentos: { created_at?: string; historico_analises?: { created_at?: string }[] }[]
  },
  mes: string
): boolean {
  if (!mes || mes === MES_TODOS) return true
  return remessaNoPeriodo(remessa, boundsDoMes(mes))
}

/** Filtra análises IA pelo período quando ativo (alinhado aos badges e gráficos). */
function analisesNoPeriodo(
  item: HistoricoControleIAItem,
  periodo: PeriodoFiltro
): HistoricoControleIAItem['analises_ia'] {
  const lista = item.analises_ia || []
  if (!periodoAtivo(periodo)) return lista
  return lista.filter((a) => noPeriodo(a.created_at, periodo))
}

export function metricasDeHistorico(
  itens: HistoricoControleIAItem[],
  periodo: PeriodoFiltro = PERIODO_TODOS
): MetricasIAResponse {
  const porPerfil: Record<string, number> = {}
  const porMes: Record<string, number> = {}
  const porTipo: Record<string, number> = {}

  const tipoDe = (p: HistoricoControleIAItem) => {
    if (p.ml_fraude_detectada) return 'fraude_ml'
    if (p.fornecedor_nao_cadastrado) return 'pj_nao_cadastrado'
    if (p.pf_nao_cadastrado) return 'pf_nao_cadastrado'
    if (p.risk_level === 'alto' || (p.risk_score ?? 0) >= 0.7) return 'risco_alto'
    if (p.risk_level === 'medio' || (p.risk_score ?? 0) >= 0.4) return 'risco_medio'
    return 'conformidade'
  }

  const labelsTipo: Record<string, string> = {
    fraude_ml: 'Fraude ML',
    pj_nao_cadastrado: 'PJ não cadastrado',
    pf_nao_cadastrado: 'PF não cadastrado',
    risco_alto: 'Risco alto',
    risco_medio: 'Risco médio',
    conformidade: 'Conformidade',
  }

  const labelsPerfil: Record<string, string> = {
    analista: 'Analista',
    gerente: 'Gerente',
    sistema: 'Sistema / IA',
    diretoria: 'Diretoria',
  }

  /** Mesmo mapeamento do backend (dashboard_ia_metrics.TRIGGER_PERFIL). */
  const triggerParaPerfil: Record<string, string> = {
    envio_gerente: 'analista',
    reenvio_gerente: 'analista',
    reanalise_gerente: 'gerente',
    catalogo_mba: 'sistema',
  }

  for (const item of itens) {
    const tipo = tipoDe(item)
    porTipo[tipo] = (porTipo[tipo] || 0) + 1

    for (const a of analisesNoPeriodo(item, periodo)) {
      const perfil = triggerParaPerfil[a.triggered_by] || 'sistema'
      porPerfil[perfil] = (porPerfil[perfil] || 0) + 1
      const mes = chaveMes(a.created_at)
      if (mes) porMes[mes] = (porMes[mes] || 0) + 1
    }
  }

  const totalAnalises = Object.values(porPerfil).reduce((s, n) => s + n, 0)
  const fraudesMl = itens.filter((i) => i.ml_fraude_detectada).length

  return {
    resumo: {
      total_analises: totalAnalises,
      total_pagamentos_ia: itens.length,
      fraudes_ml: fraudesMl,
    },
    por_perfil: Object.entries(porPerfil)
      .map(([perfil, quantidade]) => ({
      perfil,
      label:
        labelsPerfil[perfil] ||
        perfil.charAt(0).toUpperCase() + perfil.slice(1).replace(/_/g, ' '),
      quantidade,
    }))
      .sort((a, b) => b.quantidade - a.quantidade),
    por_mes: Object.entries(porMes)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([mes, quantidade]) => ({ mes, label: rotuloMes(mes), quantidade })),
    por_tipo_deteccao: Object.entries(porTipo).map(([tipo, quantidade]) => ({
      tipo,
      label: labelsTipo[tipo] || tipo,
      quantidade,
    })),
  }
}

export interface KPIsPainel {
  pagamentosAnalisados: number
  execucoesIA: number
  fraudesMl: number
  pjNaoCadastrados: number
  pfNaoCadastrados: number
  valorAnalisado: number
  saldoContas: number | null
  remessasNoPeriodo?: number
}

export function kpisCoerentesComGraficos(
  itens: HistoricoControleIAItem[],
  metricas: MetricasIAResponse | null,
  options?: { saldoContas?: number | null; remessasNoPeriodo?: number }
): KPIsPainel {
  const fraudesMl = metricas?.resumo.fraudes_ml ?? itens.filter((i) => i.ml_fraude_detectada).length
  return {
    pagamentosAnalisados: itens.length,
    execucoesIA: metricas?.resumo.total_analises ?? 0,
    fraudesMl,
    pjNaoCadastrados: itens.filter((i) => i.fornecedor_nao_cadastrado).length,
    pfNaoCadastrados: itens.filter((i) => i.pf_nao_cadastrado).length,
    valorAnalisado: itens.reduce((s, i) => s + (i.valor || 0), 0),
    saldoContas: options?.saldoContas ?? null,
    remessasNoPeriodo: options?.remessasNoPeriodo,
  }
}

/** Uma única fonte para Diretoria: KPIs + gráficos + resumo do histórico. */
export function painelDiretoriaConsolidado(
  itens: HistoricoControleIAItem[],
  periodo: PeriodoFiltro,
  saldoContas: number | null
) {
  const metricas = metricasDeHistorico(itens, periodo)
  const kpis = kpisCoerentesComGraficos(itens, metricas, { saldoContas })
  const remessasIds = new Set(itens.map((i) => i.remessa_id))
  return {
    metricas,
    kpis,
    historicoResumo: {
      total_registros: itens.length,
      fraudes_ml: kpis.fraudesMl,
      execucoes_ia: kpis.execucoesIA,
      remessas_distintas: remessasIds.size,
    },
  }
}
