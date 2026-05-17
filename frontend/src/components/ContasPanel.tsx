import { useEffect, useState } from 'react'
import { apiClient, type ContaBancaria, type MovimentoConta } from '../api/client'

export default function ContasPanel({
  onSelectConta,
  ocultarReceita = false,
}: {
  onSelectConta?: (id: number) => void
  /** Diretoria: apenas consulta de saldos, sem formulário de crédito */
  ocultarReceita?: boolean
}) {
  const [contas, setContas] = useState<ContaBancaria[]>([])
  const [receita, setReceita] = useState({ contaId: '', valor: '', descricao: '' })
  const [msg, setMsg] = useState('')
  const [movimentos, setMovimentos] = useState<MovimentoConta[]>([])
  const [contaMov, setContaMov] = useState<number | null>(null)

  const load = async () => {
    const r = await apiClient.contas()
    setContas(r.data)
  }

  useEffect(() => {
    load()
  }, [])

  const creditar = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!receita.contaId || !receita.valor) return
    try {
      await apiClient.registrarReceita(
        Number(receita.contaId),
        Number(receita.valor),
        receita.descricao || 'Receita'
      )
      setMsg('Receita creditada com sucesso.')
      setReceita({ contaId: '', valor: '', descricao: '' })
      load()
    } catch (err: unknown) {
      const ex = err as { response?: { data?: { detail?: string } } }
      setMsg(ex.response?.data?.detail || 'Erro ao creditar')
    }
  }

  const verMovimentos = async (id: number) => {
    setContaMov(id)
    const r = await apiClient.movimentosConta(id)
    setMovimentos(r.data)
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
      <h2 className="font-semibold text-lg">Contas bancárias (saldo)</h2>
      {msg && <p className="text-sm text-emerald-400">{msg}</p>}
      <div className="grid sm:grid-cols-2 gap-3">
        {contas.map((c) => (
          <div
            key={c.id}
            className="p-4 rounded-lg bg-slate-800 border border-slate-700"
          >
            <p className="font-medium text-white">{c.nome}</p>
            <p className="text-xs text-slate-500 mt-1">
              Banco {c.banco} · Ag {c.agencia} · Cc {c.conta}
            </p>
            <p className="text-2xl font-bold text-emerald-400 mt-2">
              R$ {c.saldo.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </p>
            <div className="flex gap-2 mt-2">
              {onSelectConta && (
                <button
                  type="button"
                  onClick={() => onSelectConta(c.id)}
                  className="text-xs px-2 py-1 rounded bg-violet-600 hover:bg-violet-500"
                >
                  Usar na remessa
                </button>
              )}
              <button
                type="button"
                onClick={() => verMovimentos(c.id)}
                className="text-xs px-2 py-1 rounded border border-slate-600 hover:bg-slate-700"
              >
                Extrato
              </button>
            </div>
          </div>
        ))}
      </div>

      {!ocultarReceita && (
      <form onSubmit={creditar} className="border-t border-slate-800 pt-4 space-y-2">
        <p className="text-sm font-medium text-slate-300">Registrar receita</p>
        <select
          required
          className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
          value={receita.contaId}
          onChange={(e) => setReceita({ ...receita, contaId: e.target.value })}
        >
          <option value="">Conta destino</option>
          {contas.map((c) => (
            <option key={c.id} value={c.id}>
              {c.nome}
            </option>
          ))}
        </select>
        <input
          type="number"
          step="0.01"
          required
          placeholder="Valor (R$)"
          className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
          value={receita.valor}
          onChange={(e) => setReceita({ ...receita, valor: e.target.value })}
        />
        <input
          placeholder="Descrição"
          className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
          value={receita.descricao}
          onChange={(e) => setReceita({ ...receita, descricao: e.target.value })}
        />
        <button
          type="submit"
          className="w-full py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-sm font-medium"
        >
          Creditar receita
        </button>
      </form>
      )}

      {contaMov && movimentos.length > 0 && (
        <div className="border-t border-slate-800 pt-3 max-h-40 overflow-y-auto text-xs">
          <p className="text-slate-400 mb-2">Últimos movimentos</p>
          {movimentos.map((m) => (
            <div key={m.id} className="py-1 border-b border-slate-800/50">
              <span className={m.tipo === 'receita' ? 'text-emerald-400' : 'text-red-400'}>
                {m.tipo === 'receita' ? '+' : '-'} R$ {m.valor.toLocaleString('pt-BR')}
              </span>
              <span className="text-slate-500 ml-2">{m.descricao}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
