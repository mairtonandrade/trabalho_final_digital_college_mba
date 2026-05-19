/**
 * Snapshot do seed do backend — carregado em runtime de /demoSnapshot.json
 * (evita bundle antigo em cache no Netlify e facilita validar o deploy).
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

let snapshot: DemoSnapshot | null = null
let loadPromise: Promise<DemoSnapshot> | null = null

export function getDemoSnapshot(): DemoSnapshot {
  if (!snapshot) {
    throw new Error('demoSnapshot ainda não carregado — chame initDemoSnapshot() antes.')
  }
  return snapshot
}

export async function initDemoSnapshot(): Promise<DemoSnapshot> {
  if (snapshot) return snapshot
  if (loadPromise) return loadPromise

  loadPromise = fetch(`${import.meta.env.BASE_URL}demoSnapshot.json`, { cache: 'no-store' })
    .then(async (res) => {
      if (!res.ok) {
        throw new Error(`Falha ao carregar demoSnapshot.json (${res.status})`)
      }
      return res.json() as Promise<DemoSnapshot>
    })
    .then((data) => {
      const k = data.meta?.kpis_diretoria_esperados
      if (!k || k.pagamentos_analisados < 50) {
        throw new Error(
          `demoSnapshot inválido ou desatualizado (pagamentos=${k?.pagamentos_analisados ?? 0}). Rode: python scripts/export_demo_snapshot.py`
        )
      }
      snapshot = data
      return data
    })

  return loadPromise
}

export function demoSnapshotMeta(): DemoSnapshot['meta'] | null {
  return snapshot?.meta ?? null
}

export function findPagamentoDemo(id: number): Pagamento | undefined {
  const data = getDemoSnapshot()
  for (const r of data.remessas) {
    const p = r.pagamentos.find((x) => x.id === id)
    if (p) return p
  }
  return undefined
}

export function remessasDemo(status?: string): Remessa[] {
  const data = getDemoSnapshot()
  if (status) return data.remessas.filter((r) => r.status === status)
  return data.remessas
}

export function historicoControleDemo(limit = 150): HistoricoControleIAResponse {
  const base = getDemoSnapshot().historicoControleIA
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
