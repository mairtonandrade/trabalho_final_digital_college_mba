import {
  boundsDoMes,
  buildMesesOpcoes,
  PERIODO_TODOS,
  periodoAtivo,
  presetUltimosDias,
  type PeriodoFiltro,
} from '../utils/filtrosMovimentacao'

export default function FiltrosMovimentacao({
  periodo,
  onPeriodoChange,
  datasReferencia,
  somenteFraude,
  onSomenteFraudeChange,
  totalVisivel,
  totalGeral,
}: {
  periodo: PeriodoFiltro
  onPeriodoChange: (p: PeriodoFiltro) => void
  datasReferencia: (string | null | undefined)[]
  somenteFraude: boolean
  onSomenteFraudeChange: (v: boolean) => void
  totalVisivel?: number
  totalGeral?: number
}) {
  const meses = buildMesesOpcoes(datasReferencia)

  const onAtalho = (v: string) => {
    if (!v) return
    if (v === 'todos') onPeriodoChange(PERIODO_TODOS)
    else if (v === '30d') onPeriodoChange(presetUltimosDias(30))
    else if (v === '90d') onPeriodoChange(presetUltimosDias(90))
    else if (v === '180d') onPeriodoChange(presetUltimosDias(180))
    else if (v.startsWith('mes:')) onPeriodoChange(boundsDoMes(v.slice(4)))
  }

  return (
    <div className="mb-6 p-4 rounded-xl border border-slate-700 bg-slate-900/60 space-y-4">
      <div className="flex flex-wrap items-end gap-4">
        <div className="flex flex-col gap-1 min-w-[160px]">
          <label className="text-xs text-slate-500 uppercase tracking-wide">Atalho de período</label>
          <select className="input-field" defaultValue="" onChange={(e) => onAtalho(e.target.value)}>
            <option value="">Selecionar atalho…</option>
            <option value="todos">Todo o histórico</option>
            <option value="30d">Últimos 30 dias</option>
            <option value="90d">Últimos 90 dias</option>
            <option value="180d">Últimos 6 meses</option>
            {meses.map((m) => (
              <option key={m.value} value={`mes:${m.value}`}>
                Mês {m.label}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="periodo-de" className="text-xs text-slate-500 uppercase tracking-wide">
            De
          </label>
          <input
            id="periodo-de"
            type="date"
            className="input-field"
            value={periodo.de}
            onChange={(e) => onPeriodoChange({ ...periodo, de: e.target.value })}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="periodo-ate" className="text-xs text-slate-500 uppercase tracking-wide">
            Até
          </label>
          <input
            id="periodo-ate"
            type="date"
            className="input-field"
            value={periodo.ate}
            onChange={(e) => onPeriodoChange({ ...periodo, ate: e.target.value })}
          />
        </div>

        {periodoAtivo(periodo) && (
          <button
            type="button"
            onClick={() => onPeriodoChange(PERIODO_TODOS)}
            className="text-xs text-cyan-400 hover:underline pb-2"
          >
            Limpar período
          </button>
        )}

        <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer pb-2">
          <input
            type="checkbox"
            checked={somenteFraude}
            onChange={(e) => onSomenteFraudeChange(e.target.checked)}
            className="rounded border-slate-600"
          />
          Somente fraudes ML
        </label>
      </div>

      {totalVisivel !== undefined && totalGeral !== undefined && (
        <p className="text-xs text-slate-500">
          Exibindo <span className="text-cyan-400 font-medium">{totalVisivel}</span> de {totalGeral}{' '}
          registro(s)
          {periodoAtivo(periodo) && (
            <span className="text-slate-600">
              {' '}
              · {periodo.de || '…'} até {periodo.ate || '…'}
            </span>
          )}
        </p>
      )}
    </div>
  )
}
