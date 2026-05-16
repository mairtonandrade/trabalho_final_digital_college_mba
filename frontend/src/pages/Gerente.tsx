import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import PageHeader from '../components/ui/PageHeader'
import CadastrosPanel from '../components/CadastrosPanel'
import ContasPanel from '../components/ContasPanel'
import AnaliseHistorico from '../components/AnaliseHistorico'
import MlFraudAlert from '../components/MlFraudAlert'
import PagamentoRevisaoPanel from '../components/PagamentoRevisaoPanel'
import RiskBadge from '../components/RiskBadge'
import { apiClient, type Fornecedor, type FornecedorDetalhe, type Remessa } from '../api/client'

export default function Gerente() {
  const [pendentes, setPendentes] = useState<Fornecedor[]>([])
  const [todosFornecedores, setTodosFornecedores] = useState<Fornecedor[]>([])
  const [remessas, setRemessas] = useState<Remessa[]>([])
  const [justificativa, setJustificativa] = useState('')
  const [msg, setMsg] = useState('')
  const [emailPreview, setEmailPreview] = useState('')
  const [detalhe, setDetalhe] = useState<FornecedorDetalhe | null>(null)
  const [motivoDevolucao, setMotivoDevolucao] = useState('')
  const [reanalisando, setReanalisando] = useState(false)

  const load = async () => {
    const [f, all, r] = await Promise.all([
      apiClient.fornecedores('pendente'),
      apiClient.fornecedores(),
      apiClient.remessas('aguardando_gerente', true),
    ])
    setPendentes(f.data)
    setTodosFornecedores(all.data)
    setRemessas(r.data)
  }

  useEffect(() => {
    load()
  }, [])

  const aprovarFornecedor = async (id: number, aprovado: boolean) => {
    await apiClient.aprovarFornecedor(id, aprovado, aprovado ? undefined : 'Dados inconsistentes')
    setMsg(aprovado ? 'Fornecedor aprovado na whitelist.' : 'Fornecedor rejeitado.')
    setDetalhe(null)
    load()
  }

  const verHistorico = async (id: number) => {
    const r = await apiClient.fornecedorDetalhe(id)
    setDetalhe(r.data)
  }

  const temNaoCadastrado = (r: Remessa) =>
    r.pagamentos.some((p) => p.fornecedor_nao_cadastrado || p.pf_nao_cadastrado)

  const temMlFraude = (r: Remessa) => r.pagamentos.some((p) => p.ml_fraude_detectada)

  const todosRevisados = (r: Remessa) => r.pagamentos.every((p) => p.revisado_gerente)

  const devolverAnalista = async (id: number) => {
    if (!motivoDevolucao.trim()) {
      setMsg('Informe o motivo da devolução ao analista.')
      return
    }
    try {
      await apiClient.devolverRemessa(id, motivoDevolucao)
      setMsg('Remessa devolvida ao analista para correção.')
      setMotivoDevolucao('')
      load()
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      setMsg(e.response?.data?.detail || 'Erro ao devolver')
    }
  }

  const reanalisarIA = async (id: number) => {
    setReanalisando(true)
    setMsg('Nova análise IA em andamento…')
    try {
      await apiClient.reanalisarRemessa(id)
      setMsg('Reanálise concluída. Revise os novos resultados.')
      load()
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      setMsg(e.response?.data?.detail || 'Erro na reanálise')
    } finally {
      setReanalisando(false)
    }
  }

  const decisaoRemessa = async (id: number, aprovado: boolean, r: Remessa) => {
    if (aprovado && !todosRevisados(r)) {
      setMsg('Revise valores e documentos de todos os pagamentos antes de liberar a remessa.')
      return
    }
    const precisaJust =
      (r.risk_level === 'alto' || temNaoCadastrado(r) || temMlFraude(r)) && aprovado
    if (precisaJust && !justificativa.trim()) {
      setMsg(
        'Justificativa obrigatória: alto risco, fraude detectada pelo ML e/ou fornecedor NÃO CADASTRADO.'
      )
      return
    }
    try {
      const res = await apiClient.decisaoRemessa(id, aprovado, justificativa)
      if (res.data.email_auditoria) setEmailPreview(res.data.email_auditoria)
      setMsg(
        aprovado
          ? 'Remessa liberada. Saldo da conta debitado.'
          : 'Remessa rejeitada.'
      )
      setJustificativa('')
      load()
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      setMsg(e.response?.data?.detail || 'Erro na decisão')
    }
  }

  const statusColor: Record<string, string> = {
    aprovado: 'text-emerald-400',
    pendente: 'text-amber-400',
    rejeitado: 'text-red-400',
  }

  return (
    <Layout title="Painel do Gerente (Checker)">
      <PageHeader
        title="Aprovações e revisão IA"
        subtitle="Analise scores ML, parecer GenAI, documentos e libere ou devolva remessas ao analista."
      />
      {msg && (
        <div className="mb-6 p-4 rounded-lg bg-slate-800 border border-slate-700 text-sm">{msg}</div>
      )}

      <div className="mb-10">
        <ContasPanel />
      </div>

      <div className="mb-10">
        <CadastrosPanel modo="gerente" />
      </div>

      <section className="mb-10">
        <h2 className="text-lg font-semibold mb-4">Fornecedores pendentes (aprovação inicial)</h2>
        <div className="grid lg:grid-cols-2 gap-6">
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {todosFornecedores.map((f) => (
              <div
                key={f.id}
                className="p-4 rounded-xl border border-slate-800 bg-slate-900/50 flex justify-between items-start gap-2"
              >
                <div>
                  <p className="font-medium">{f.razao_social}</p>
                  <p className="text-sm text-slate-400">CNPJ {f.cnpj}</p>
                  <p className={`text-xs mt-1 ${statusColor[f.status] || ''}`}>{f.status}</p>
                </div>
                <button
                  onClick={() => verHistorico(f.id)}
                  className="text-xs px-2 py-1 rounded border border-slate-600 hover:bg-slate-700 shrink-0"
                >
                  Histórico
                </button>
              </div>
            ))}
          </div>
          {detalhe && (
            <div className="p-4 rounded-xl border border-violet-800/50 bg-slate-900/80">
              <h3 className="font-semibold mb-2">{detalhe.razao_social}</h3>
              <p className="text-sm text-slate-400 mb-4">Status: {detalhe.status}</p>
              {detalhe.status === 'pendente' && (
                <div className="flex gap-2 mb-4">
                  <button
                    onClick={() => aprovarFornecedor(detalhe.id, true)}
                    className="px-3 py-1.5 rounded-lg bg-emerald-600 text-sm"
                  >
                    Aprovar
                  </button>
                  <button
                    onClick={() => aprovarFornecedor(detalhe.id, false)}
                    className="px-3 py-1.5 rounded-lg bg-red-600/80 text-sm"
                  >
                    Rejeitar
                  </button>
                </div>
              )}
              <p className="text-xs text-slate-500 uppercase mb-2">Histórico de aprovação</p>
              <ul className="space-y-2 text-xs max-h-48 overflow-y-auto">
                {detalhe.historico.length === 0 && (
                  <li className="text-slate-500">Sem registros ainda.</li>
                )}
                {detalhe.historico.map((h) => (
                  <li key={h.id} className="border-b border-slate-800 pb-2">
                    <span className="text-slate-300">{h.action}</span>
                    <span className="text-slate-500"> · {h.user_role} · </span>
                    <span className="text-slate-600">
                      {new Date(h.created_at).toLocaleString('pt-BR')}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>

      <section className="mb-10">
        <h2 className="text-lg font-semibold mb-4">Fornecedores pendentes</h2>
        <div className="space-y-3">
          {pendentes.length === 0 && (
            <p className="text-slate-500 text-sm">Nenhum cadastro pendente.</p>
          )}
          {pendentes.map((f) => (
            <div
              key={f.id}
              className="p-4 rounded-xl border border-amber-800/40 bg-amber-950/20 flex flex-wrap gap-4 justify-between items-center"
            >
              <div>
                <p className="font-medium">{f.razao_social}</p>
                <p className="text-sm text-slate-400">
                  CNPJ {f.cnpj} · Banco {f.banco}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => aprovarFornecedor(f.id, true)}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-sm"
                >
                  Aprovar
                </button>
                <button
                  onClick={() => aprovarFornecedor(f.id, false)}
                  className="px-4 py-2 rounded-lg bg-red-600/80 hover:bg-red-500 text-sm"
                >
                  Rejeitar
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-4">Remessas — 2ª assinatura</h2>
        <p className="text-sm text-slate-400 mb-3">
          Resultados da análise IA (ML + GenAI) aparecem aqui. Revise anexos e marque cada pagamento antes de liberar.
          Em caso de fraude, devolva ao analista para correção e reenvio.
        </p>
        <textarea
          placeholder="Justificativa para liberar (obrigatória se alto risco / fraude ML / não cadastrado)"
          className="w-full mb-2 px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
          value={justificativa}
          onChange={(e) => setJustificativa(e.target.value)}
        />
        <textarea
          placeholder="Motivo para devolver ao analista (fraude / correção documental)"
          className="w-full mb-4 px-3 py-2 rounded-lg bg-amber-950/30 border border-amber-700/50 text-sm"
          value={motivoDevolucao}
          onChange={(e) => setMotivoDevolucao(e.target.value)}
        />
        <div className="space-y-4">
          {remessas.map((r) => (
            <div key={r.id} className="p-5 rounded-xl border border-slate-800 bg-slate-900/50">
              <div className="flex flex-wrap justify-between gap-2 mb-2">
                <h3 className="font-semibold">
                  #{r.id} — {r.titulo} · {r.conta_nome}
                </h3>
                <RiskBadge level={r.risk_level} score={r.risk_score_max} />
              </div>
              <p className="text-sm text-slate-400 mb-3">
                Total R$ {r.valor_total.toLocaleString('pt-BR')} · Saldo conta R{' '}
                {(r.saldo_conta_disponivel ?? 0).toLocaleString('pt-BR')}
              </p>
              {temNaoCadastrado(r) && (
                <p className="text-amber-400 text-sm mb-3 border border-amber-700/50 p-2 rounded">
                  Contém pagamento a fornecedor NÃO CADASTRADO — justificativa obrigatória para liberar.
                </p>
              )}
              {temMlFraude(r) && (
                <p className="text-red-400 text-sm mb-3 border border-red-700/50 p-2 rounded">
                  Modelo ML detectou fraude em um ou mais pagamentos — justificativa obrigatória para liberar.
                </p>
              )}
              {!todosRevisados(r) && (
                <p className="text-violet-400 text-sm mb-3 border border-violet-700/50 p-2 rounded">
                  Revise todos os pagamentos (anexos + valores) antes de liberar.
                </p>
              )}
              {r.pagamentos.map((p) => (
                <div
                  key={p.id}
                  className="mt-2 p-3 rounded-lg bg-slate-800 text-sm border border-slate-700"
                >
                  <p>
                    <span className="font-mono text-cyan-400">{p.codigo_pagamento || `PAY-${p.id}`}</span>
                    {' · '}
                    {p.fornecedor_razao_social}: R$ {p.valor.toLocaleString('pt-BR')}
                    {p.pf_nao_cadastrado ? ' · PF NÃO CADASTRADA' : ''}
                    {p.fornecedor_nao_cadastrado ? ' · PJ NÃO CADASTRADO' : ''}
                    {p.tipo_despesa === 'salario' && p.competencia ? ` · Sal. ${p.competencia}` : ''}
                  </p>
                  {p.ia_analisado ? <RiskBadge level={p.risk_level} score={p.risk_score} /> : null}
                  <MlFraudAlert
                    detectada={p.ml_fraude_detectada}
                    score={p.ml_score}
                    motivos={p.ml_motivos}
                  />
                  {p.genai_parecer && (
                    <p className="text-slate-400 text-xs mt-2 whitespace-pre-wrap max-h-40 overflow-y-auto">
                      {p.genai_parecer}
                    </p>
                  )}
                  <AnaliseHistorico itens={p.historico_analises} />
                  <PagamentoRevisaoPanel pagamento={p} onRevisado={load} />
                </div>
              ))}
              <div className="flex flex-wrap gap-2 mt-4">
                <button
                  onClick={() => decisaoRemessa(r.id, true, r)}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-sm"
                >
                  Liberar (debita conta)
                </button>
                <button
                  onClick={() => decisaoRemessa(r.id, false, r)}
                  className="px-4 py-2 rounded-lg bg-red-600/80 hover:bg-red-500 text-sm"
                >
                  Rejeitar
                </button>
                <button
                  onClick={() => reanalisarIA(r.id)}
                  disabled={reanalisando}
                  className="px-4 py-2 rounded-lg border border-violet-600 text-violet-300 text-sm disabled:opacity-50"
                >
                  {reanalisando ? 'Analisando…' : 'Nova análise IA'}
                </button>
                <button
                  onClick={() => devolverAnalista(r.id)}
                  className="px-4 py-2 rounded-lg border border-amber-600 text-amber-300 text-sm"
                >
                  Devolver ao analista
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {emailPreview && (
        <section className="mt-8 p-4 rounded-xl border border-emerald-800/50 bg-emerald-950/30">
          <h3 className="font-semibold text-emerald-400 mb-2">E-mail de auditoria</h3>
          <pre className="text-xs text-slate-300 whitespace-pre-wrap">{emailPreview}</pre>
        </section>
      )}
    </Layout>
  )
}
