import { useMemo, useState } from 'react'
import RiskBadge from './RiskBadge'
import type { HistoricoControleIAItem, HistoricoControleIAResponse } from '../api/client'

const PERFIL_COR: Record<string, string> = {
  analista: 'text-cyan-400 bg-cyan-950/40 border-cyan-800',
  gerente: 'text-violet-400 bg-violet-950/40 border-violet-800',
  diretoria: 'text-emerald-400 bg-emerald-950/40 border-emerald-800',
  sistema: 'text-amber-400 bg-amber-950/40 border-amber-800',
}

export default function HistoricoControleIA({
  data,
  onVerPagamento,
}: {
  data: HistoricoControleIAResponse | null
  onVerPagamento: (id: number) => void
}) {
  const [filtroPerfil, setFiltroPerfil] = useState<string>('todos')
  const [somenteFraude, setSomenteFraude] = useState(false)
  const [busca, setBusca] = useState('')
  const [expandido, setExpandido] = useState<number | null>(null)

  const itens = useMemo(() => {
    if (!data?.itens) return []
    return data.itens.filter((item) => {
      if (somenteFraude && !item.ml_fraude_detectada) return false
      if (busca) {
        const q = busca.toLowerCase()
        if (
          !item.codigo_pagamento.toLowerCase().includes(q) &&
          !(item.beneficiario_nome || '').toLowerCase().includes(q) &&
          !String(item.remessa_id).includes(q)
        ) {
          return false
        }
      }
      if (filtroPerfil !== 'todos') {
        const tem = item.eventos_fluxo?.some((e) => e.perfil === filtroPerfil)
        if (!tem && filtroPerfil !== 'sistema') return false
        if (filtroPerfil === 'sistema' && !item.analises_ia?.length) return false
      }
      return true
    })
  }, [data, filtroPerfil, somenteFraude, busca])

  if (!data) {
    return <p className="text-slate-500 text-sm">Carregando histórico de controle...</p>
  }

  return (
    <section className="mb-8 rounded-xl border border-cyan-800/50 bg-gradient-to-br from-cyan-950/20 to-slate-950 p-5">
      <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
        <div>
          <h2 className="font-semibold text-cyan-300 text-lg">Controle total — Histórico IA e fluxos financeiros</h2>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Visão unificada do que o modelo detectou e de cada etapa do fluxo (Analista, IA, Gerente e
            Diretoria). Use para acompanhamento, questionamentos e auditoria dos últimos 6 meses.
          </p>
        </div>
        {data.resumo && (
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="badge border border-slate-600 text-slate-300">
              {data.resumo.total_registros} pagamentos analisados
            </span>
            <span className="badge border border-red-800 text-red-300">
              {data.resumo.fraudes_ml} fraudes ML
            </span>
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="search"
          placeholder="Buscar PAY, beneficiário, remessa..."
          className="input-field max-w-xs"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
        />
        <select
          className="input-field max-w-[180px]"
          value={filtroPerfil}
          onChange={(e) => setFiltroPerfil(e.target.value)}
        >
          <option value="todos">Todos os perfis</option>
          <option value="analista">Analista</option>
          <option value="gerente">Gerente</option>
          <option value="sistema">Sistema / IA</option>
          <option value="diretoria">Diretoria</option>
        </select>
        <label className="flex items-center gap-2 text-sm text-slate-400 cursor-pointer">
          <input
            type="checkbox"
            checked={somenteFraude}
            onChange={(e) => setSomenteFraude(e.target.checked)}
            className="rounded border-slate-600"
          />
          Somente fraude ML
        </label>
      </div>

      {itens.length === 0 ? (
        <p className="text-slate-500 text-sm">Nenhum registro para os filtros selecionados.</p>
      ) : (
        <div className="space-y-3 max-h-[32rem] overflow-y-auto pr-1">
          {itens.map((item) => (
            <HistoricoCard
              key={item.pagamento_id}
              item={item}
              aberto={expandido === item.pagamento_id}
              onToggle={() =>
                setExpandido(expandido === item.pagamento_id ? null : item.pagamento_id)
              }
              onVerPagamento={() => onVerPagamento(item.pagamento_id)}
            />
          ))}
        </div>
      )}
    </section>
  )
}

function HistoricoCard({
  item,
  aberto,
  onToggle,
  onVerPagamento,
}: {
  item: HistoricoControleIAItem
  aberto: boolean
  onToggle: () => void
  onVerPagamento: () => void
}) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900/80 overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        className="w-full text-left p-4 hover:bg-slate-800/50 transition"
      >
        <div className="flex flex-wrap justify-between gap-2 items-start">
          <div>
            <span className="font-mono text-cyan-400">{item.codigo_pagamento}</span>
            <span className="text-slate-500 mx-2">·</span>
            <span className="text-white">{item.beneficiario_nome}</span>
            <p className="text-slate-400 text-xs mt-1">
              Remessa #{item.remessa_id}
              {item.remessa_titulo ? ` — ${item.remessa_titulo}` : ''} ·{' '}
              <span className="text-slate-500">{item.remessa_status}</span>
            </p>
          </div>
          <div className="flex items-center gap-2">
            <RiskBadge level={item.risk_level} score={item.risk_score} />
            {item.ml_fraude_detectada && (
              <span className="badge bg-red-950 text-red-300 border border-red-800">ML Fraude</span>
            )}
          </div>
        </div>
        <p className="text-sm text-slate-400 mt-2">
          R$ {item.valor.toLocaleString('pt-BR')} · {item.analises_ia?.length ?? 0} versão(ões) IA ·{' '}
          {item.eventos_fluxo?.length ?? 0} evento(s) de fluxo
        </p>
      </button>

      {aberto && (
        <div className="px-4 pb-4 border-t border-slate-800 space-y-4">
          {item.ml_motivos && (
            <p className="text-xs text-red-300/90">
              <strong>ML:</strong> {item.ml_motivos}
            </p>
          )}
          {item.genai_parecer && (
            <p className="text-xs text-slate-300 whitespace-pre-wrap border-l-2 border-violet-600 pl-3">
              <strong className="text-violet-400">GenAI:</strong> {item.genai_parecer}
            </p>
          )}
          {item.gerente_justificativa && (
            <p className="text-xs text-emerald-400/90">
              <strong>Gerente:</strong> {item.gerente_justificativa}
            </p>
          )}
          {item.motivo_devolucao && (
            <p className="text-xs text-amber-400">
              <strong>Devolução:</strong> {item.motivo_devolucao}
            </p>
          )}

          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase mb-2">Linha do tempo do fluxo</p>
            <ul className="space-y-2">
              {item.eventos_fluxo?.map((ev, idx) => (
                <li
                  key={`${ev.acao}-${idx}`}
                  className="flex gap-3 text-xs border-l-2 border-slate-700 pl-3 py-1"
                >
                  <span
                    className={`shrink-0 px-2 py-0.5 rounded border ${PERFIL_COR[ev.perfil] || 'text-slate-400 border-slate-600'}`}
                  >
                    {ev.perfil}
                  </span>
                  <div>
                    <p className="text-slate-200">{ev.acao_label}</p>
                    <p className="text-slate-500">
                      {ev.data ? new Date(ev.data).toLocaleString('pt-BR') : '—'}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase mb-2">Versões da análise IA</p>
            <ul className="space-y-2">
              {item.analises_ia?.map((a) => (
                <li key={a.id} className="p-2 rounded bg-slate-950 border border-slate-800 text-xs">
                  <div className="flex justify-between gap-2">
                    <span>
                      v{a.versao} · {a.triggered_label || a.triggered_by}
                    </span>
                    <RiskBadge level={a.risk_level} score={a.risk_score} />
                  </div>
                  {a.ml_fraude_detectada ? (
                    <p className="text-red-400 mt-1">Fraude ML detectada</p>
                  ) : null}
                  {a.genai_parecer && (
                    <p className="text-slate-400 mt-1 line-clamp-3">{a.genai_parecer}</p>
                  )}
                  <p className="text-slate-600 mt-1">
                    {a.created_at ? new Date(a.created_at).toLocaleString('pt-BR') : ''}
                  </p>
                </li>
              ))}
            </ul>
          </div>

          <button type="button" onClick={onVerPagamento} className="btn-secondary text-xs">
            Ver detalhe completo do pagamento
          </button>
        </div>
      )}
    </div>
  )
}
