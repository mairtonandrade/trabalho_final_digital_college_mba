import type { PagamentoAnaliseIA } from '../api/client'

export default function AnaliseHistorico({ itens }: { itens?: PagamentoAnaliseIA[] }) {
  if (!itens?.length) return null
  return (
    <div className="mt-2 p-2 rounded border border-slate-700 bg-slate-900/60 text-xs">
      <p className="text-slate-400 uppercase mb-1">Histórico de análises IA</p>
      <ul className="space-y-1 max-h-32 overflow-y-auto">
        {itens.map((h) => (
          <li key={h.id} className="text-slate-300 border-b border-slate-800 pb-1">
            v{h.versao} · {h.triggered_by} · risco {h.risk_level}
            {h.ml_fraude_detectada ? ' · FRAUDE ML' : ''}
            <span className="text-slate-500 block">
              {new Date(h.created_at).toLocaleString('pt-BR')}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
