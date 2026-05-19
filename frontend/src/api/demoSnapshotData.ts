/**
 * Snapshot exportado do seed do backend (scripts/export_demo_snapshot.py).
 * Garante paridade local (API) x Netlify (modo demo).
 */
import type {
  AuditLog,
  DeteccaoIA,
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
import raw from './demoSnapshot.json'

export interface DemoSnapshot {
  meta: {
    gerado_em: string
    seed: string
    kpis_diretoria_esperados: {
      pagamentos_analisados: number
      execucoes_ia: number
      fraudes_ml: number
    }
  }
  historicoControleIA: HistoricoControleIAResponse
  metricasIA: MetricasIAResponse
  kpis: KPIs
  auditoria: AuditLog[]
  deteccoesIA: DeteccaoIA[]
  alertas: unknown[]
  pagamentosNaoCadastrados: PagamentoNaoCadastrado[]
  pagamentosPFNaoCadastrados: PagamentoPFNaoCadastrado[]
  pontosAtencao: PontoAtencao[]
  remessas: Remessa[]
  contas: { id: number; nome: string; banco: string; agencia: string; conta: string; saldo: number; ativa: number }[]
  movimentos: MovimentoConta[]
}

export const DEMO_SNAPSHOT = raw as unknown as DemoSnapshot

export function findPagamentoDemo(id: number): Pagamento | undefined {
  for (const r of DEMO_SNAPSHOT.remessas) {
    const p = r.pagamentos.find((x) => x.id === id)
    if (p) return p
  }
  return undefined
}

export function remessasDemo(status?: string): Remessa[] {
  if (status) return DEMO_SNAPSHOT.remessas.filter((r) => r.status === status)
  return DEMO_SNAPSHOT.remessas
}

export function historicoControleDemo(limit = 150): HistoricoControleIAResponse {
  const base = DEMO_SNAPSHOT.historicoControleIA
  const itens = base.itens.slice(0, Math.min(limit, 300))
  return {
    resumo: {
      ...base.resumo,
      total_registros: itens.length,
      fraudes_ml: itens.filter((i) => i.ml_fraude_detectada).length,
    },
    itens,
  }
}
