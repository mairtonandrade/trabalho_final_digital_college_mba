import { useEffect, useState } from 'react'
import {
  apiClient,
  type CadastroSolicitacao,
  type Colaborador,
  type Fornecedor,
  type HistoricoCadastroItem,
} from '../api/client'

type Modo = 'analista' | 'gerente'
type SecaoCadastro = 'novo' | 'consulta' | 'tudo'

export default function CadastrosPanel({
  modo,
  secao = 'tudo',
}: {
  modo: Modo
  secao?: SecaoCadastro
}) {
  const mostrarNovo = secao === 'novo' || secao === 'tudo'
  const mostrarConsulta = secao === 'consulta' || secao === 'tudo'
  const [colaboradores, setColaboradores] = useState<Colaborador[]>([])
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([])
  const [solicitacoes, setSolicitacoes] = useState<CadastroSolicitacao[]>([])
  const [msg, setMsg] = useState('')
  const [hist, setHist] = useState<HistoricoCadastroItem[] | null>(null)
  const [editCol, setEditCol] = useState<Colaborador | null>(null)
  const [editForn, setEditForn] = useState<Fornecedor | null>(null)

  const [novoCol, setNovoCol] = useState({
    cpf: '',
    nome_completo: '',
    cargo: '',
    banco: '',
    agencia: '',
    conta: '',
  })

  const load = async () => {
    const [c, f] = await Promise.all([apiClient.colaboradores(), apiClient.fornecedores()])
    setColaboradores(c.data)
    setFornecedores(f.data)
    if (modo === 'gerente') {
      const s = await apiClient.solicitacoesCadastro()
      setSolicitacoes(s.data)
    }
  }

  useEffect(() => {
    load()
  }, [modo])

  const statusLabel: Record<string, string> = {
    ativo: 'Ativo',
    aprovado: 'Ativo',
    pendente: 'Pendente',
    inativo: 'Inativo',
    rejeitado: 'Rejeitado',
  }

  const statusClass: Record<string, string> = {
    ativo: 'text-emerald-400',
    aprovado: 'text-emerald-400',
    pendente: 'text-amber-400',
    inativo: 'text-slate-500',
    rejeitado: 'text-red-400',
  }

  const criarColaborador = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiClient.criarColaborador(novoCol)
      setMsg('Colaborador cadastrado — aguarda aprovação do gerente.')
      setNovoCol({ cpf: '', nome_completo: '', cargo: '', banco: '', agencia: '', conta: '' })
      load()
    } catch (err: unknown) {
      const ex = err as { response?: { data?: { detail?: string } } }
      setMsg(ex.response?.data?.detail || 'Erro ao cadastrar colaborador')
    }
  }

  const verHistorico = async (tipo: 'colaborador' | 'fornecedor', id: number) => {
    const r =
      tipo === 'colaborador'
        ? await apiClient.colaboradorDetalhe(id)
        : await apiClient.fornecedorDetalhe(id)
    setHist(r.data.historico)
  }

  const toggleStatus = async (tipo: 'colaborador' | 'fornecedor', id: number, ativo: boolean) => {
    if (modo !== 'gerente') return
    if (tipo === 'colaborador') await apiClient.colaboradorStatus(id, ativo)
    else await apiClient.fornecedorStatus(id, ativo)
    setMsg(ativo ? 'Cadastro reativado.' : 'Cadastro inativado.')
    load()
  }

  const salvarEdicaoDireta = async () => {
    if (modo !== 'gerente') return
    try {
      if (editCol) {
        await apiClient.editarColaborador(editCol.id, {
          nome_completo: editCol.nome_completo,
          cargo: editCol.cargo,
          banco: editCol.banco,
          agencia: editCol.agencia,
          conta: editCol.conta,
        })
        setEditCol(null)
      }
      if (editForn) {
        await apiClient.editarFornecedor(editForn.id, {
          razao_social: editForn.razao_social,
          banco: editForn.banco,
          agencia: editForn.agencia,
          conta: editForn.conta,
        })
        setEditForn(null)
      }
      setMsg('Cadastro atualizado.')
      load()
    } catch (err: unknown) {
      const ex = err as { response?: { data?: { detail?: string } } }
      setMsg(ex.response?.data?.detail || 'Erro ao salvar')
    }
  }

  const solicitar = async (
    tipo: 'colaborador' | 'fornecedor',
    id: number,
    operacao: 'editar' | 'excluir',
    dados?: Record<string, string>
  ) => {
    try {
      const r =
        tipo === 'colaborador'
          ? await apiClient.solicitarColaborador(id, operacao, dados)
          : await apiClient.solicitarFornecedor(id, operacao, dados)
      setMsg(
        `Solicitação de ${operacao} enviada ao gerente.` +
          (r.data.alertas_ia?.length ? ` Alertas IA: ${r.data.alertas_ia.join('; ')}` : '')
      )
      load()
    } catch (err: unknown) {
      const ex = err as { response?: { data?: { detail?: string } } }
      setMsg(ex.response?.data?.detail || 'Erro na solicitação')
    }
  }

  const decidirSol = async (id: number, aprovada: boolean) => {
    await apiClient.decidirSolicitacao(id, aprovada)
    setMsg(aprovada ? 'Solicitação aprovada.' : 'Solicitação rejeitada.')
    load()
  }

  return (
    <section className="panel-surface space-y-6">
      <h2 className="section-title">
        {secao === 'novo'
          ? 'Novos cadastros'
          : secao === 'consulta'
            ? 'Cadastros existentes'
            : 'Cadastros — Colaboradores e Fornecedores'}
      </h2>
      {msg && (
        <p className="text-sm text-slate-100 border border-slate-500/60 bg-slate-800/80 p-3 rounded-lg">
          {msg}
        </p>
      )}

      {mostrarNovo && modo === 'analista' && (
        <form onSubmit={criarColaborador} className="space-y-2 border border-slate-700 p-4 rounded-lg">
          <p className="text-sm font-medium text-blue-300">Novo colaborador (PF)</p>
          {(['nome_completo', 'cpf', 'cargo', 'banco', 'agencia', 'conta'] as const).map((f) => (
            <input
              key={f}
              required={f !== 'cargo'}
              placeholder={f.replace('_', ' ')}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
              value={novoCol[f]}
              onChange={(e) => setNovoCol({ ...novoCol, [f]: e.target.value })}
            />
          ))}
          <button type="submit" className="w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-sm">
            Cadastrar colaborador
          </button>
        </form>
      )}

      {mostrarNovo && modo === 'gerente' && solicitacoes.length > 0 && (
        <div className="border border-amber-700/50 p-4 rounded-lg bg-amber-950/20">
          <p className="text-amber-300 font-medium mb-2">Solicitações do analista</p>
          {solicitacoes.map((s) => (
            <div key={s.id} className="text-sm mb-3 p-2 bg-slate-900 rounded border border-slate-700">
              <p>
                {s.operacao.toUpperCase()} · {s.entity_type} {s.entidade_nome} (#{s.entity_id})
              </p>
              {s.alertas_ia && <p className="text-red-400 text-xs mt-1">IA: {s.alertas_ia}</p>}
              <div className="flex gap-2 mt-2">
                <button
                  type="button"
                  onClick={() => decidirSol(s.id, true)}
                  className="px-2 py-1 rounded bg-emerald-700 text-xs"
                >
                  Aprovar
                </button>
                <button
                  type="button"
                  onClick={() => decidirSol(s.id, false)}
                  className="px-2 py-1 rounded bg-red-800 text-xs"
                >
                  Rejeitar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {mostrarConsulta && (
      <div className="space-y-8">
        <div className="rounded-xl border border-blue-800/40 bg-slate-950/50 p-5 sm:p-6 min-h-[min(70vh,520px)] flex flex-col">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
            <h3 className="text-lg font-semibold text-white">Colaboradores</h3>
            <span className="text-sm text-slate-300 px-3 py-1 rounded-full border border-slate-600 bg-slate-800/80">
              {colaboradores.length} cadastrado(s)
            </span>
          </div>
          <div className="flex-1 space-y-3 overflow-y-auto pr-1 min-h-[360px] max-h-[min(65vh,480px)]">
            {colaboradores.map((c) => (
              <div
                key={c.id}
                className="p-4 rounded-xl bg-slate-800/90 text-sm border border-slate-600/70 hover:border-blue-600/40 transition"
              >
                <p className="font-semibold text-white text-base">{c.nome_completo}</p>
                <p className="text-slate-300 mt-1">
                  CPF {c.cpf} · {c.banco} ag {c.agencia} cc {c.conta}
                </p>
                <p className={`mt-1 font-medium ${statusClass[c.status] || ''}`}>
                  {statusLabel[c.status] || c.status}
                </p>
                <div className="flex flex-wrap gap-2 mt-3">
                  <button
                    type="button"
                    onClick={() => verHistorico('colaborador', c.id)}
                    className="text-sm px-2 py-1 rounded border border-cyan-700/50 text-cyan-300 hover:bg-cyan-950/40"
                  >
                    Histórico
                  </button>
                  {modo === 'gerente' && (
                    <>
                      <button type="button" onClick={() => setEditCol(c)} className="text-sm text-violet-300 hover:underline">
                        Editar
                      </button>
                      <button type="button" onClick={() => toggleStatus('colaborador', c.id, c.status === 'inativo')} className="text-sm text-amber-300 hover:underline">
                        {c.status === 'inativo' ? 'Ativar' : 'Inativar'}
                      </button>
                      {c.status === 'pendente' && (
                        <button type="button" onClick={() => apiClient.aprovarColaborador(c.id, true).then(load)} className="text-sm text-emerald-300 hover:underline">
                          Aprovar
                        </button>
                      )}
                    </>
                  )}
                  {modo === 'analista' && c.status !== 'inativo' && (
                    <button type="button" onClick={() => solicitar('colaborador', c.id, 'excluir')} className="text-sm text-red-300 hover:underline">
                      Solicitar exclusão
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-amber-800/40 bg-slate-950/50 p-5 sm:p-6 min-h-[min(70vh,520px)] flex flex-col">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-4">
            <h3 className="text-lg font-semibold text-white">Fornecedores</h3>
            <span className="text-sm text-slate-300 px-3 py-1 rounded-full border border-slate-600 bg-slate-800/80">
              {fornecedores.length} cadastrado(s)
            </span>
          </div>
          <div className="flex-1 space-y-3 overflow-y-auto pr-1 min-h-[360px] max-h-[min(65vh,480px)]">
            {fornecedores.map((f) => (
              <div
                key={f.id}
                className="p-4 rounded-xl bg-slate-800/90 text-sm border border-slate-600/70 hover:border-amber-600/40 transition"
              >
                <p className="font-semibold text-white text-base">{f.razao_social}</p>
                <p className="text-slate-300 mt-1">CNPJ {f.cnpj}</p>
                <p className={`mt-1 font-medium ${statusClass[f.status] || ''}`}>
                  {statusLabel[f.status] || f.status}
                </p>
                <div className="flex flex-wrap gap-2 mt-3">
                  <button
                    type="button"
                    onClick={() => verHistorico('fornecedor', f.id)}
                    className="text-sm px-2 py-1 rounded border border-cyan-700/50 text-cyan-300 hover:bg-cyan-950/40"
                  >
                    Histórico
                  </button>
                  {modo === 'gerente' && (
                    <>
                      <button type="button" onClick={() => setEditForn(f)} className="text-sm text-violet-300 hover:underline">
                        Editar
                      </button>
                      <button type="button" onClick={() => toggleStatus('fornecedor', f.id, f.status === 'inativo')} className="text-sm text-amber-300 hover:underline">
                        {f.status === 'inativo' ? 'Ativar' : 'Inativar'}
                      </button>
                    </>
                  )}
                  {modo === 'analista' && f.status !== 'inativo' && (
                    <button type="button" onClick={() => solicitar('fornecedor', f.id, 'excluir')} className="text-sm text-red-300 hover:underline">
                      Solicitar exclusão
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      )}

      {mostrarConsulta && (editCol || editForn) && modo === 'gerente' && (
        <div className="p-4 border border-violet-700 rounded-lg space-y-2">
          <p className="text-violet-300 text-sm font-medium">Edição direta (gerente)</p>
          {editCol &&
            (['nome_completo', 'cargo', 'banco', 'agencia', 'conta'] as const).map((k) => (
              <input
                key={k}
                className="w-full px-2 py-1 rounded bg-slate-800 text-sm"
                value={editCol[k] || ''}
                onChange={(e) => setEditCol({ ...editCol, [k]: e.target.value })}
              />
            ))}
          {editForn &&
            (['razao_social', 'banco', 'agencia', 'conta'] as const).map((k) => (
              <input
                key={k}
                className="w-full px-2 py-1 rounded bg-slate-800 text-sm"
                value={editForn[k]}
                onChange={(e) => setEditForn({ ...editForn, [k]: e.target.value })}
              />
            ))}
          <button type="button" onClick={salvarEdicaoDireta} className="px-3 py-1 rounded bg-violet-600 text-sm">
            Salvar
          </button>
        </div>
      )}

      {hist && (
        <div className="p-4 border border-cyan-800 rounded-lg max-h-48 overflow-y-auto text-xs">
          <p className="text-cyan-400 font-medium mb-2">Histórico (lido pela IA)</p>
          {hist.map((h) => (
            <div key={h.id} className="mb-2 border-b border-slate-800 pb-2">
              <p>
                {h.action} · {h.user_role} · {new Date(h.created_at).toLocaleString('pt-BR')}
              </p>
              {h.alertas_ia?.map((a) => (
                <p key={a} className="text-red-400">
                  ⚠ {a}
                </p>
              ))}
            </div>
          ))}
          <button type="button" onClick={() => setHist(null)} className="text-slate-500 mt-2">
            Fechar
          </button>
        </div>
      )}
    </section>
  )
}
