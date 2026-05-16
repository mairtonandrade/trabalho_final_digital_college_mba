import { useState } from 'react'
import { apiClient, type Pagamento } from '../api/client'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

export default function PagamentoRevisaoPanel({
  pagamento,
  onRevisado,
}: {
  pagamento: Pagamento
  onRevisado: () => void
}) {
  const [valoresOk, setValoresOk] = useState(false)
  const [documentosOk, setDocumentosOk] = useState(false)
  const [obs, setObs] = useState('')
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)

  const urlAnexo = (anexoId: number) =>
    `${API_BASE}/pagamentos/${pagamento.id}/anexos/${anexoId}/download`

  const revisar = async () => {
    if (!valoresOk || !documentosOk) {
      setMsg('Marque valores e documentos em conformidade.')
      return
    }
    setLoading(true)
    setMsg('')
    try {
      await apiClient.revisarPagamento(pagamento.id, {
        valores_ok: valoresOk,
        documentos_ok: documentosOk,
        observacao: obs || undefined,
      })
      setMsg('Pagamento marcado como revisado. Diretoria será notificada como ponto de atenção.')
      onRevisado()
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      setMsg(e.response?.data?.detail || 'Erro ao revisar')
    } finally {
      setLoading(false)
    }
  }

  if (pagamento.revisado_gerente) {
    return (
      <p className="text-emerald-400 text-xs mt-2 border border-emerald-800/40 p-2 rounded">
        ✓ Revisado — valores e documentos conferidos
        {pagamento.revisado_observacao ? ` (${pagamento.revisado_observacao})` : ''}
      </p>
    )
  }

  const docsPf =
    pagamento.tipo_beneficiario === 'pf' && pagamento.tipo_despesa !== 'salario'
  const docsPj = pagamento.tipo_beneficiario === 'pj'

  return (
    <div className="mt-3 p-3 rounded-lg border border-violet-800/50 bg-violet-950/20 text-xs space-y-3">
      <p className="font-semibold text-violet-300">Revisão documental (gerente)</p>
      <p className="text-slate-400">
        {docsPf &&
          'PF: conferir Contrato do serviço, NF Avulsa e RPA.'}
        {docsPj && 'PJ: conferir Nota fiscal padrão.'}
        {pagamento.tipo_despesa === 'salario' && 'Salário: conferir holerite da competência.'}
      </p>
      <ul className="space-y-1">
        {(pagamento.anexos ?? []).map((a) => (
          <li key={a.id} className="flex justify-between gap-2">
            <span className="text-slate-300">{a.tipo_label}</span>
            <a
              href={urlAnexo(a.id)}
              target="_blank"
              rel="noreferrer"
              className="text-cyan-400 hover:underline shrink-0"
            >
              Abrir
            </a>
          </li>
        ))}
      </ul>
      <label className="flex items-center gap-2 cursor-pointer">
        <input type="checkbox" checked={valoresOk} onChange={(e) => setValoresOk(e.target.checked)} />
        Valores conferidos (beneficiário, valor, conta)
      </label>
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={documentosOk}
          onChange={(e) => setDocumentosOk(e.target.checked)}
        />
        Documentos em conformidade
      </label>
      <input
        placeholder="Observação da revisão (opcional)"
        className="w-full px-2 py-1.5 rounded bg-slate-800 border border-slate-700"
        value={obs}
        onChange={(e) => setObs(e.target.value)}
      />
      {msg && <p className="text-amber-400">{msg}</p>}
      <button
        type="button"
        disabled={loading}
        onClick={revisar}
        className="w-full py-1.5 rounded bg-violet-600 hover:bg-violet-500 disabled:opacity-50"
      >
        Marcar como revisado
      </button>
    </div>
  )
}
