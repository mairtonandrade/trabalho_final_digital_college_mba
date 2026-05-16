import { useEffect, useState } from 'react'
import MlFraudAlert from './MlFraudAlert'
import RiskBadge from './RiskBadge'
import { apiClient, type Pagamento } from '../api/client'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

export default function PagamentoDetalheModal({
  pagamentoId,
  onClose,
}: {
  pagamentoId: number
  onClose: () => void
}) {
  const [pagamento, setPagamento] = useState<Pagamento | null>(null)
  const [remessaInfo, setRemessaInfo] = useState<{
    titulo?: string
    status?: string
    gerente_justificativa?: string
  } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    apiClient
      .pagamentoDetalheExecutivo(pagamentoId)
      .then((r) => {
        setPagamento(r.data.pagamento)
        setRemessaInfo(r.data.remessa)
      })
      .catch(() => apiClient.pagamento(pagamentoId).then((r) => setPagamento(r.data)))
      .finally(() => setLoading(false))
  }, [pagamentoId])

  const urlAnexo = (anexoId: number) =>
    `${API_BASE}/pagamentos/${pagamentoId}/anexos/${anexoId}/download`

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/70">
      <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl border border-slate-700 bg-slate-900 shadow-xl">
        <div className="sticky top-0 flex justify-between items-center p-4 border-b border-slate-800 bg-slate-900">
          <h3 className="font-semibold text-white">Detalhe do pagamento #{pagamentoId}</h3>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-white px-2 py-1"
          >
            Fechar
          </button>
        </div>
        <div className="p-5 text-sm space-y-4">
          {loading && <p className="text-slate-500">Carregando...</p>}
          {pagamento && (
            <>
              {remessaInfo && (
                <p className="text-xs text-slate-500">
                  Remessa: {remessaInfo.titulo} · {remessaInfo.status}
                </p>
              )}
              <div className="flex flex-wrap gap-2 justify-between">
                <div>
                  <p className="font-medium text-white">
                    {pagamento.fornecedor_razao_social || pagamento.beneficiario_nome}
                  </p>
                  <p className="text-slate-400 text-xs">
                    {pagamento.tipo_beneficiario?.toUpperCase()} · {pagamento.tipo_despesa}
                    {pagamento.competencia ? ` · ${pagamento.competencia}` : ''}
                  </p>
                  <p className="text-lg font-bold text-emerald-400 mt-1">
                    R$ {pagamento.valor.toLocaleString('pt-BR')}
                  </p>
                </div>
                <RiskBadge level={pagamento.risk_level} score={pagamento.risk_score} />
              </div>
              {pagamento.revisado_gerente ? (
                <p className="text-emerald-400 text-xs border border-emerald-800/50 p-2 rounded">
                  Revisado pelo gerente
                  {pagamento.revisado_observacao ? `: ${pagamento.revisado_observacao}` : ''}
                </p>
              ) : null}
              {pagamento.ponto_atencao_diretoria ? (
                <p className="text-amber-400 text-xs border border-amber-700/50 p-2 rounded">
                  Ponto de atenção para a diretoria
                </p>
              ) : null}
              <MlFraudAlert
                detectada={pagamento.ml_fraude_detectada}
                score={pagamento.ml_score}
                motivos={pagamento.ml_motivos}
              />
              <div>
                <p className="text-xs uppercase text-slate-500 mb-2">Anexos</p>
                <ul className="space-y-2">
                  {(pagamento.anexos ?? []).map((a) => (
                    <li
                      key={`${a.id}-${a.tipo}`}
                      className="flex justify-between items-center p-2 rounded-lg bg-slate-800 border border-slate-700"
                    >
                      <span>
                        <span className="text-violet-300">{a.tipo_label}</span>
                        <br />
                        <span className="text-slate-400 text-xs">{a.nome_arquivo}</span>
                      </span>
                      <a
                        href={urlAnexo(a.id)}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs px-2 py-1 rounded border border-cyan-700 text-cyan-400 hover:bg-cyan-950"
                      >
                        Visualizar
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
              {pagamento.genai_parecer && (
                <div className="p-3 rounded-lg bg-slate-800/80 text-xs whitespace-pre-wrap text-slate-300">
                  {pagamento.genai_parecer}
                </div>
              )}
              {remessaInfo?.gerente_justificativa && (
                <p className="text-xs text-slate-400">
                  Justificativa gerente: {remessaInfo.gerente_justificativa}
                </p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
