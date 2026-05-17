import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import Layout from '../components/Layout'
import PageHeader from '../components/ui/PageHeader'
import ContasPanel from '../components/ContasPanel'
import HistoricoControleIA from '../components/HistoricoControleIA'
import PainelGraficosIA from '../components/PainelGraficosIA'
import PagamentoDetalheModal from '../components/PagamentoDetalheModal'
import RiskBadge from '../components/RiskBadge'
import {
  apiClient,
  type AuditLog,
  type KPIs,
  type PagamentoNaoCadastrado,
  type PagamentoPFNaoCadastrado,
  type DeteccaoIA,
  type HistoricoControleIAResponse,
  type MetricasIAResponse,
  type PontoAtencao,
} from '../api/client'

interface Alerta {
  id: number
  remessa_id: number
  valor: number
  risk_score: number
  risk_level: string
  genai_parecer?: string
  fornecedor_nao_cadastrado?: boolean
  fornecedor_razao_social?: string
  fornecedor_status?: string
}

export default function Diretoria() {
  const [kpis, setKpis] = useState<KPIs | null>(null)
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [alertas, setAlertas] = useState<Alerta[]>([])
  const [naoCad, setNaoCad] = useState<PagamentoNaoCadastrado[]>([])
  const [pfNaoCad, setPfNaoCad] = useState<PagamentoPFNaoCadastrado[]>([])
  const [selected, setSelected] = useState<Alerta | null>(null)
  const [pontosAtencao, setPontosAtencao] = useState<PontoAtencao[]>([])
  const [detalhePagamentoId, setDetalhePagamentoId] = useState<number | null>(null)
  const [deteccoes, setDeteccoes] = useState<DeteccaoIA[]>([])
  const [historicoIA, setHistoricoIA] = useState<HistoricoControleIAResponse | null>(null)
  const [metricasIA, setMetricasIA] = useState<MetricasIAResponse | null>(null)

  useEffect(() => {
    Promise.all([
      apiClient.kpis(),
      apiClient.auditoria(),
      apiClient.alertas(),
      apiClient.pagamentosNaoCadastrados(),
      apiClient.pagamentosPFNaoCadastrados(),
      apiClient.pontosAtencao(),
      apiClient.deteccoesIA(),
      apiClient.historicoControleIA(150),
      apiClient.metricasIA(6),
    ])
      .then(([k, a, al, nc, pf, pa, det, hist, met]) => {
        setKpis(k.data)
        setLogs(Array.isArray(a.data) ? a.data : [])
        setAlertas(Array.isArray(al.data) ? al.data : [])
        setNaoCad(Array.isArray(nc.data) ? nc.data : [])
        setPfNaoCad(Array.isArray(pf.data) ? pf.data : [])
        setPontosAtencao(Array.isArray(pa.data) ? pa.data : [])
        setDeteccoes(Array.isArray(det.data) ? det.data : [])
        setHistoricoIA(hist.data)
        setMetricasIA(met.data)
      })
      .catch(() => {
        setLogs([])
        setDeteccoes([])
        setHistoricoIA(null)
        setMetricasIA(null)
      })
  }, [])

  const chartData = kpis
    ? [
        { name: 'Pagamentos', valor: kpis.total_pagamentos },
        { name: 'Não cadastrados', valor: kpis.pagamentos_nao_cadastrados },
        { name: 'Fraudes IA', valor: kpis.fraudes_detectadas },
      ]
    : []

  return (
    <Layout title="Dashboard Executivo — Diretoria">
      <PageHeader
        title="Visão executiva"
        subtitle="Controle total dos fluxos financeiros: histórico de tudo que a IA detectou nos perfis Analista e Gerente, com trilha para questionamentos."
      />

      <PainelGraficosIA data={metricasIA} />

      <HistoricoControleIA
        data={historicoIA}
        onVerPagamento={(id) => setDetalhePagamentoId(id)}
      />
      {kpis && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          {[
            { label: 'Saldo total contas', value: `R$ ${kpis.saldo_total_contas.toLocaleString('pt-BR')}` },
            { label: 'Remessas', value: kpis.total_remessas },
            { label: 'Valor aprovado', value: `R$ ${kpis.valor_total_aprovado.toLocaleString('pt-BR')}` },
            { label: 'PJ não cadastrados', value: kpis.pagamentos_nao_cadastrados },
            { label: 'PF não cadastradas', value: kpis.pagamentos_pf_nao_cadastrados ?? 0 },
            { label: 'Fraudes IA', value: kpis.fraudes_detectadas },
          ].map((c) => (
            <div
              key={c.label}
              className="p-4 rounded-xl border border-slate-800 bg-gradient-to-br from-slate-900 to-slate-950"
            >
              <p className="text-xs text-slate-500 uppercase">{c.label}</p>
              <p className="text-xl font-bold mt-1">{c.value}</p>
            </div>
          ))}
        </div>
      )}

      <div className="mb-8">
        <ContasPanel />
      </div>

      <section className="mb-8 rounded-xl border border-red-800/50 bg-red-950/20 p-5">
        <h2 className="font-semibold text-red-300 mb-4">Detecções da IA (ML + GenAI)</h2>
        <p className="text-sm text-slate-400 mb-4">
          Alertas gerados após envio ao gerente, com justificativas e histórico de reanálises.
        </p>
        {deteccoes.length === 0 ? (
          <p className="text-slate-500 text-sm">Nenhuma detecção registrada.</p>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {deteccoes.map((d) => (
              <div key={d.pagamento_id} className="p-3 rounded-lg bg-slate-900 border border-slate-700 text-sm">
                <div className="flex justify-between gap-2 flex-wrap">
                  <span>
                    <span className="font-mono text-cyan-400">{d.codigo_pagamento}</span> · {d.beneficiario_nome}
                  </span>
                  <RiskBadge level={d.risk_level} score={d.risk_score} />
                </div>
                <p className="text-slate-400 mt-1">R$ {d.valor.toLocaleString('pt-BR')} · Remessa #{d.remessa_id}</p>
                {d.ml_fraude_detectada && (
                  <p className="text-red-400 text-xs mt-1">Fraude ML: {d.ml_motivos}</p>
                )}
                {d.gerente_justificativa && (
                  <p className="text-emerald-400/80 text-xs mt-1">Justificativa gerente: {d.gerente_justificativa}</p>
                )}
                {d.motivo_devolucao && (
                  <p className="text-amber-400 text-xs mt-1">Devolução: {d.motivo_devolucao}</p>
                )}
                {d.historico_analises?.length > 0 && (
                  <p className="text-slate-500 text-xs mt-1">
                    Histórico IA: {d.historico_analises.map((h) => `v${h.versao}`).join(', ')}
                  </p>
                )}
                <button
                  type="button"
                  onClick={() => setDetalhePagamentoId(d.pagamento_id)}
                  className="mt-2 text-xs text-cyan-400 hover:underline"
                >
                  Ver pagamento completo
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="mb-8 rounded-xl border border-violet-800/50 bg-violet-950/20 p-5">
        <h2 className="font-semibold text-violet-300 mb-4">
          Pontos de atenção — pagamentos revisados pelo gerente
        </h2>
        <p className="text-sm text-slate-400 mb-4">
          Todos os pagamentos com documentação conferida pelo gerente aparecem aqui para acompanhamento
          executivo, mesmo após revisão em conformidade.
        </p>
        {pontosAtencao.length === 0 ? (
          <p className="text-slate-500 text-sm">Nenhum ponto de atenção registrado.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-slate-500 border-b border-slate-800">
                  <th className="text-left py-2">Beneficiário</th>
                  <th className="text-left py-2">Valor</th>
                  <th className="text-left py-2">Tipo</th>
                  <th className="text-left py-2">Revisão</th>
                  <th className="text-left py-2">Ação</th>
                </tr>
              </thead>
              <tbody>
                {pontosAtencao.map((p) => (
                  <tr key={p.pagamento_id} className="border-b border-slate-800/50">
                    <td className="py-2">
                      {p.beneficiario_nome}
                      <br />
                      <span className="text-slate-500 text-xs">{p.beneficiario_documento}</span>
                    </td>
                    <td className="py-2">R$ {p.valor.toLocaleString('pt-BR')}</td>
                    <td className="py-2 text-xs">
                      {p.tipo_beneficiario.toUpperCase()} · {p.tipo_despesa}
                      <br />
                      Remessa #{p.remessa_id} ({p.remessa_status})
                    </td>
                    <td className="py-2 text-emerald-400 text-xs">
                      {p.revisado_gerente ? 'Revisado' : 'Pendente'}
                      {p.revisado_observacao && (
                        <>
                          <br />
                          <span className="text-slate-500">{p.revisado_observacao}</span>
                        </>
                      )}
                    </td>
                    <td className="py-2">
                      <button
                        type="button"
                        onClick={() => setDetalhePagamentoId(p.pagamento_id)}
                        className="text-xs px-2 py-1 rounded border border-cyan-700 text-cyan-400 hover:bg-cyan-950"
                      >
                        Ver pagamento
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="mb-8 rounded-xl border border-red-800/50 bg-red-950/20 p-5">
        <h2 className="font-semibold text-red-300 mb-4">
          Alertas: PF com CPF não cadastrado como colaborador
        </h2>
        <p className="text-sm text-slate-400 mb-4">
          Pagamentos a pessoas físicas fora da base de RH. Limite R$ 10.000. Salário exige competência (MM/AAAA).
        </p>
        {pfNaoCad.length === 0 ? (
          <p className="text-slate-500 text-sm">Nenhum alerta de PF não cadastrada.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-500 border-b border-slate-800">
                <th className="text-left py-2">Nome / CPF</th>
                <th className="text-left py-2">Valor</th>
                <th className="text-left py-2">Despesa</th>
                <th className="text-left py-2">Justificativa</th>
              </tr>
            </thead>
            <tbody>
              {pfNaoCad.map((p) => (
                <tr key={p.pagamento_id} className="border-b border-slate-800/50">
                  <td className="py-2">
                    {p.nome}
                    <br />
                    <span className="text-slate-500">{p.cpf}</span>
                  </td>
                  <td className="py-2">R$ {p.valor.toLocaleString('pt-BR')}</td>
                  <td className="py-2 text-blue-300">
                    {p.tipo_despesa === 'salario' ? `Salário ${p.competencia}` : p.tipo_despesa}
                  </td>
                  <td className="py-2 text-slate-400">{p.gerente_justificativa || 'Pendente'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section className="mb-8 rounded-xl border border-amber-800/50 bg-amber-950/20 p-5">
        <h2 className="font-semibold text-amber-300 mb-4">
          Pagamentos a fornecedores PJ NÃO CADASTRADOS (IA)
        </h2>
        <p className="text-sm text-slate-400 mb-4">
          Limite R$ 10.000 por operação. Exige justificativa gerencial e aparece neste painel.
        </p>
        {naoCad.length === 0 ? (
          <p className="text-slate-500 text-sm">Nenhum pagamento excepcional registrado.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-slate-500 border-b border-slate-800">
                  <th className="text-left py-2">Fornecedor</th>
                  <th className="text-left py-2">Valor</th>
                  <th className="text-left py-2">Status forn.</th>
                  <th className="text-left py-2">Remessa</th>
                  <th className="text-left py-2">Justificativa gerente</th>
                </tr>
              </thead>
              <tbody>
                {naoCad.map((p) => (
                  <tr key={p.pagamento_id} className="border-b border-slate-800/50">
                    <td className="py-2">{p.fornecedor}</td>
                    <td className="py-2">R$ {p.valor.toLocaleString('pt-BR')}</td>
                    <td className="py-2 text-amber-400">{p.status_fornecedor}</td>
                    <td className="py-2">
                      #{p.remessa_id} ({p.remessa_status})
                    </td>
                    <td className="py-2 text-slate-400 max-w-xs truncate">
                      {p.gerente_justificativa || '— pendente —'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <div className="grid lg:grid-cols-2 gap-8 mb-8">
        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50 h-72">
          <h2 className="font-semibold mb-4">Visão operacional</h2>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155' }} />
              <Bar dataKey="valor" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/50">
          <h2 className="font-semibold mb-4">Alertas IA</h2>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {alertas.map((a) => (
              <button
                key={a.id}
                onClick={() => setSelected(a)}
                className="w-full text-left p-3 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-sm"
              >
                <div className="flex justify-between gap-2">
                  <span>
                    #{a.remessa_id}
                    {a.fornecedor_nao_cadastrado && (
                      <span className="text-amber-400 ml-1">· NÃO CAD.</span>
                    )}
                  </span>
                  <RiskBadge level={a.risk_level} score={a.risk_score} />
                </div>
                <p className="text-slate-400 mt-1 text-xs">{a.fornecedor_razao_social}</p>
              </button>
            ))}
          </div>
          {selected?.genai_parecer && (
            <div className="mt-4 p-3 rounded-lg bg-red-950/30 border border-red-800/40 text-xs">
              <p className="font-semibold text-red-300 mb-2">Parecer IA</p>
              <p className="text-slate-300 whitespace-pre-wrap">{selected.genai_parecer}</p>
            </div>
          )}
        </div>
      </div>

      <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-5">
        <h2 className="font-semibold mb-4">Trilha de auditoria (WORM)</h2>
        <div className="overflow-x-auto max-h-64 overflow-y-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-500 border-b border-slate-800">
                <th className="text-left py-2">Data</th>
                <th className="text-left py-2">Ação</th>
                <th className="text-left py-2">Perfil</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.id} className="border-b border-slate-800/50">
                  <td className="py-2 text-slate-400">
                    {new Date(l.created_at).toLocaleString('pt-BR')}
                  </td>
                  <td className="py-2">{l.action}</td>
                  <td className="py-2">{l.user_role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {detalhePagamentoId && (
        <PagamentoDetalheModal
          pagamentoId={detalhePagamentoId}
          onClose={() => setDetalhePagamentoId(null)}
        />
      )}
    </Layout>
  )
}
