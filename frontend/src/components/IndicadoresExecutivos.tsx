import type { KPIsPainel } from '../utils/filtrosMovimentacao'
import { periodoAtivo, type PeriodoFiltro } from '../utils/filtrosMovimentacao'

export default function IndicadoresExecutivos({
  kpis,
  periodo,
}: {
  kpis: KPIsPainel
  periodo: PeriodoFiltro
}) {
  const cards: {
    label: string
    value: string
    hint?: string
    destaque?: boolean
  }[] = [
    {
      label: 'Pagamentos analisados (IA)',
      value: String(kpis.pagamentosAnalisados),
      hint: 'Igual à soma do gráfico "Tipo de detecção"',
    },
    {
      label: 'Execuções IA',
      value: String(kpis.execucoesIA),
      hint: 'Igual à soma do gráfico "Quem disparou a IA"',
    },
    {
      label: 'Fraudes ML',
      value: String(kpis.fraudesMl),
      hint: 'Alinhado ao gráfico de detecção',
      destaque: true,
    },
    {
      label: 'PJ não cadastrados',
      value: String(kpis.pjNaoCadastrados),
    },
    {
      label: 'PF não cadastradas',
      value: String(kpis.pfNaoCadastrados),
    },
    {
      label: periodoAtivo(periodo) ? 'Valor analisado no período' : 'Valor analisado (histórico)',
      value: `R$ ${kpis.valorAnalisado.toLocaleString('pt-BR')}`,
    },
    ...(kpis.saldoContas != null
      ? [
          {
            label: 'Saldo total contas',
            value: `R$ ${kpis.saldoContas.toLocaleString('pt-BR')}`,
            hint: 'Posição atual (não filtrada por período)',
          },
        ]
      : []),
  ]

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 mb-6">
      {cards.map((c) => (
        <div
          key={c.label}
          className={`p-4 rounded-xl border bg-gradient-to-br from-slate-900 to-slate-950 ${
            c.destaque ? 'border-red-800/60' : 'border-slate-800'
          }`}
        >
          <p className="text-xs text-slate-500 uppercase leading-tight">{c.label}</p>
          <p className={`text-xl font-bold mt-1 ${c.destaque ? 'text-red-300' : ''}`}>{c.value}</p>
          {c.hint && <p className="text-[10px] text-slate-600 mt-1">{c.hint}</p>}
        </div>
      ))}
    </div>
  )
}
