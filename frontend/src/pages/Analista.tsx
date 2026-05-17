import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import PageHeader from '../components/ui/PageHeader'
import ModuloSelector, { type ModuloItem } from '../components/ui/ModuloSelector'
import CadastrosPanel from '../components/CadastrosPanel'
import ContasPanel from '../components/ContasPanel'

const MODULOS_ANALISTA: ModuloItem[] = [
  { id: 'remessas', titulo: 'Remessas', descricao: 'Criar pagamentos e enviar ao gerente', icone: '💸' },
  { id: 'cadastros-novo', titulo: 'Novos cadastros', descricao: 'Colaborador PF e fornecedor PJ', icone: '➕' },
  { id: 'cadastros-consulta', titulo: 'Consultar cadastros', descricao: 'Listar e solicitar alterações', icone: '📁' },
  { id: 'contas', titulo: 'Contas e extrato', descricao: 'Saldos, créditos e movimentação', icone: '🏦' },
]
import { apiClient, type Colaborador, type Fornecedor, type Remessa } from '../api/client'

const LIMITE_NAO_CAD = 10000

export default function Analista() {
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([])
  const [colaboradores, setColaboradores] = useState<Colaborador[]>([])
  const [remessaAtiva, setRemessaAtiva] = useState<Remessa | null>(null)
  const [contaSelecionada, setContaSelecionada] = useState<number | null>(null)
  const [msg, setMsg] = useState('')
  const [salvandoPagamento, setSalvandoPagamento] = useState(false)
  const [enviandoIA, setEnviandoIA] = useState(false)
  const [modulo, setModulo] = useState('remessas')

  const [novoForn, setNovoForn] = useState({
    cnpj: '',
    razao_social: '',
    banco: '',
    agencia: '',
    conta: '',
  })

  const [pagamento, setPagamento] = useState({
    tipo_beneficiario: 'pj' as 'pj' | 'pf',
    tipo_despesa: 'fornecedor' as 'fornecedor' | 'salario' | 'outros',
    fornecedor_id: '',
    colaborador_id: '',
    cpf_manual: '',
    nome_manual: '',
    competencia: '',
    valor: '',
    arquivo_nf_padrao: null as File | null,
    arquivo_contrato: null as File | null,
    arquivo_nf_avulsa: null as File | null,
    arquivo_rpa: null as File | null,
    arquivo_holerite: null as File | null,
  })

  const load = async () => {
    const [f, c] = await Promise.all([apiClient.fornecedoresAtivos(), apiClient.colaboradoresAtivos()])
    setFornecedores(f.data)
    setColaboradores(c.data)
  }

  useEffect(() => {
    load()
    apiClient.remessas('devolvida_analista').then((r) => {
      if (r.data.length > 0) setRemessaAtiva(r.data[0])
    })
  }, [])

  const criarFornecedor = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiClient.criarFornecedor(novoForn)
      setMsg('Fornecedor enviado para aprovação da gerência.')
      setNovoForn({ cnpj: '', razao_social: '', banco: '', agencia: '', conta: '' })
      load()
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      setMsg(e.response?.data?.detail || 'Erro ao cadastrar')
    }
  }

  const novaRemessa = async () => {
    if (!contaSelecionada) {
      setMsg('Selecione uma conta bancária de origem (clique em "Usar na remessa").')
      return
    }
    const titulo = `Remessa ${new Date().toLocaleDateString('pt-BR')}`
    const r = await apiClient.criarRemessa(titulo, contaSelecionada)
    setRemessaAtiva(r.data)
    setMsg(`Remessa #${r.data.id} na conta ${r.data.conta_nome}. Adicione pagamentos.`)
  }

  const adicionarPagamento = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!remessaAtiva) return
    const valor = Number(pagamento.valor)
    if (pagamento.tipo_beneficiario === 'pj' && !pagamento.arquivo_nf_padrao) {
      setMsg('Anexe a nota fiscal padrão (PJ).')
      return
    }
    if (
      pagamento.tipo_beneficiario === 'pf' &&
      pagamento.tipo_despesa === 'salario' &&
      !pagamento.arquivo_holerite
    ) {
      setMsg('Anexe o holerite/comprovante de salário.')
      return
    }
    if (
      pagamento.tipo_beneficiario === 'pf' &&
      pagamento.tipo_despesa !== 'salario' &&
      (!pagamento.arquivo_contrato || !pagamento.arquivo_nf_avulsa || !pagamento.arquivo_rpa)
    ) {
      setMsg('Transferência PF exige: Contrato, NF Avulsa e RPA.')
      return
    }
    const fd = new FormData()
    fd.append('tipo_beneficiario', pagamento.tipo_beneficiario)
    fd.append('tipo_despesa', pagamento.tipo_despesa)
    fd.append('valor', pagamento.valor)
    if (pagamento.arquivo_nf_padrao) fd.append('arquivo_nf_padrao', pagamento.arquivo_nf_padrao)
    if (pagamento.arquivo_contrato) fd.append('arquivo_contrato', pagamento.arquivo_contrato)
    if (pagamento.arquivo_nf_avulsa) fd.append('arquivo_nf_avulsa', pagamento.arquivo_nf_avulsa)
    if (pagamento.arquivo_rpa) fd.append('arquivo_rpa', pagamento.arquivo_rpa)
    if (pagamento.arquivo_holerite) fd.append('arquivo_holerite', pagamento.arquivo_holerite)
    if (pagamento.tipo_beneficiario === 'pj') {
      const forn = fornecedores.find((f) => f.id === Number(pagamento.fornecedor_id))
      if (forn && forn.status !== 'ativo' && forn.status !== 'aprovado' && valor > LIMITE_NAO_CAD) {
        setMsg(`Fornecedor não cadastrado: limite R$ ${LIMITE_NAO_CAD.toLocaleString('pt-BR')}.`)
        return
      }
      fd.append('fornecedor_id', pagamento.fornecedor_id)
    } else {
      if (pagamento.tipo_despesa === 'salario' && !pagamento.competencia) {
        setMsg('Informe a competência (MM/AAAA) para pagamento de salário.')
        return
      }
      if (pagamento.competencia) fd.append('competencia', pagamento.competencia)
      if (pagamento.colaborador_id) {
        fd.append('colaborador_id', pagamento.colaborador_id)
      } else if (pagamento.cpf_manual && pagamento.nome_manual) {
        fd.append('cpf_beneficiario', pagamento.cpf_manual)
        fd.append('nome_beneficiario', pagamento.nome_manual)
      } else {
        setMsg('Selecione colaborador ou informe CPF e nome (PF não cadastrado).')
        return
      }
    }
    setSalvandoPagamento(true)
    setMsg('Salvando pagamento na remessa…')
    try {
      const res = await apiClient.adicionarPagamento(remessaAtiva.id, fd)
      setMsg(
        `${res.data.codigo_pagamento || `PAY-${res.data.id}`} incluído na remessa.` +
          (res.data.pf_nao_cadastrado ? ' PF não cadastrada (alerta na análise IA).' : '') +
          (res.data.fornecedor_nao_cadastrado ? ' PJ não cadastrado.' : '') +
          ' A análise IA será feita ao enviar a remessa completa ao gerente.'
      )
      setPagamento({
        tipo_beneficiario: 'pj',
        tipo_despesa: 'fornecedor',
        fornecedor_id: '',
        colaborador_id: '',
        cpf_manual: '',
        nome_manual: '',
        competencia: '',
        valor: '',
        arquivo_nf_padrao: null,
        arquivo_contrato: null,
        arquivo_nf_avulsa: null,
        arquivo_rpa: null,
        arquivo_holerite: null,
      })
      const updated = await apiClient.remessas()
      const rem = updated.data.find((x) => x.id === remessaAtiva.id)
      if (rem) setRemessaAtiva(rem)
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      setMsg(e.response?.data?.detail || 'Erro no pagamento')
    } finally {
      setSalvandoPagamento(false)
    }
  }

  const enviarGerente = async () => {
    if (!remessaAtiva || enviandoIA) return
    setEnviandoIA(true)
    setMsg(
      'Analisando remessa com IA (ML + LLaMA)… Isso pode levar alguns minutos. Não feche a página nem clique novamente.'
    )
    try {
      await apiClient.enviarRemessa(remessaAtiva.id)
      setMsg('Remessa enviada ao gerente. A análise IA está disponível no painel dele.')
      setRemessaAtiva(null)
      setContaSelecionada(null)
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      setMsg(e.response?.data?.detail || 'Não foi possível enviar — verifique saldo e documentos.')
    } finally {
      setEnviandoIA(false)
    }
  }

  const totalRemessa = remessaAtiva?.pagamentos?.reduce((s, p) => s + p.valor, 0) ?? 0
  const saldoOk =
    remessaAtiva?.saldo_conta_disponivel != null &&
    remessaAtiva.saldo_conta_disponivel >= totalRemessa

  return (
    <Layout title="Painel do Analista">
      <PageHeader
        title="Remessas e pagamentos"
        subtitle="Monte a remessa, anexe documentos e envie para análise IA em lote. A IA só roda no envio ao gerente."
      />
      {(salvandoPagamento || enviandoIA) && (
        <div className="mb-4 p-4 rounded-lg bg-violet-950/50 border border-violet-600 animate-pulse text-sm text-violet-200">
          {enviandoIA
            ? '⏳ Análise IA em andamento — aguarde…'
            : '⏳ Salvando pagamento…'}
        </div>
      )}
      {msg && (
        <div className="mb-6 p-4 rounded-lg bg-slate-800 border border-slate-700 text-sm">
          {msg}
        </div>
      )}

      <ModuloSelector modulos={MODULOS_ANALISTA} ativo={modulo} onChange={setModulo} />

      {modulo === 'cadastros-novo' && (
        <div className="space-y-6 mb-8">
          <CadastrosPanel modo="analista" secao="novo" />
          <section className="panel-surface">
            <h2 className="section-title mb-4">Novo fornecedor (KYC)</h2>
            <form onSubmit={criarFornecedor} className="space-y-3">
              {(['cnpj', 'razao_social', 'banco', 'agencia', 'conta'] as const).map((f) => (
                <input
                  key={f}
                  required
                  placeholder={f.replace('_', ' ')}
                  className="input-field"
                  value={novoForn[f]}
                  onChange={(e) => setNovoForn({ ...novoForn, [f]: e.target.value })}
                />
              ))}
              <button type="submit" className="btn-primary w-full">
                Solicitar cadastro
              </button>
            </form>
          </section>
        </div>
      )}

      {modulo === 'cadastros-consulta' && (
        <div className="mb-8">
          <CadastrosPanel modo="analista" secao="consulta" />
        </div>
      )}

      {modulo === 'contas' && (
        <div className="mb-8">
          <ContasPanel onSelectConta={(id) => setContaSelecionada(id)} />
        </div>
      )}

      {modulo === 'remessas' && (
      <section className="panel-surface">
        <div className="flex flex-wrap justify-between items-center gap-4 mb-4">
          <div>
            <h2 className="font-semibold text-lg">Remessa de Pagamentos</h2>
            {contaSelecionada && (
              <p className="text-xs text-violet-400 mt-1">Conta origem selecionada #{contaSelecionada}</p>
            )}
          </div>
          <button onClick={novaRemessa} className="text-sm px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500">
            Nova remessa
          </button>
        </div>

        {remessaAtiva?.status === 'devolvida_analista' && remessaAtiva.motivo_devolucao && (
          <div className="mb-4 p-3 rounded-lg border border-amber-700/50 bg-amber-950/30 text-sm text-amber-200">
            <strong>Devolvida pelo gerente:</strong> {remessaAtiva.motivo_devolucao}
          </div>
        )}
        {remessaAtiva && (
          <div className="mb-4 p-3 rounded-lg bg-slate-800 text-sm flex flex-wrap gap-4 justify-between">
            <span>
              Remessa #{remessaAtiva.id} · {remessaAtiva.conta_nome} · {remessaAtiva.pagamentos?.length ?? 0} pag.
            </span>
            <span>
              Total: R$ {totalRemessa.toLocaleString('pt-BR')} · Saldo: R{' '}
              {(remessaAtiva.saldo_conta_disponivel ?? 0).toLocaleString('pt-BR')}
            </span>
            {!saldoOk && totalRemessa > 0 && (
              <span className="text-red-400 text-xs">Saldo insuficiente para enviar</span>
            )}
          </div>
        )}

        <form onSubmit={adicionarPagamento} className="space-y-3">
          <p className="text-xs text-slate-500">
            Inclua quantos pagamentos precisar; a análise IA (ML + GenAI) roda uma vez ao enviar a remessa ao gerente.
          </p>
          <div className="grid sm:grid-cols-2 gap-2">
            <select
              disabled={!remessaAtiva}
              className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
              value={pagamento.tipo_beneficiario}
              onChange={(e) =>
                setPagamento({
                  ...pagamento,
                  tipo_beneficiario: e.target.value as 'pj' | 'pf',
                  tipo_despesa: e.target.value === 'pf' ? pagamento.tipo_despesa : 'fornecedor',
                })
              }
            >
              <option value="pj">Pessoa Jurídica (Fornecedor)</option>
              <option value="pf">Pessoa Física (Colaborador)</option>
            </select>
            <select
              disabled={!remessaAtiva}
              className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
              value={pagamento.tipo_despesa}
              onChange={(e) =>
                setPagamento({
                  ...pagamento,
                  tipo_despesa: e.target.value as 'fornecedor' | 'salario' | 'outros',
                })
              }
            >
              <option value="fornecedor">Despesa fornecedor</option>
              <option value="salario" disabled={pagamento.tipo_beneficiario !== 'pf'}>
                Salário (exige competência)
              </option>
              <option value="outros">Outras despesas PF</option>
            </select>
          </div>

          {pagamento.tipo_beneficiario === 'pj' ? (
            <select
              required
              disabled={!remessaAtiva}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
              value={pagamento.fornecedor_id}
              onChange={(e) => setPagamento({ ...pagamento, fornecedor_id: e.target.value })}
            >
              <option value="">Fornecedor (máx. R$ 10 mil se não cadastrado)</option>
              {fornecedores.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.razao_social} — {f.status === 'ativo' || f.status === 'aprovado' ? '✓ ativo' : '⚠ não cadastrado'}
                </option>
              ))}
            </select>
          ) : (
            <>
              <select
                disabled={!remessaAtiva}
                className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
                value={pagamento.colaborador_id}
                onChange={(e) =>
                  setPagamento({ ...pagamento, colaborador_id: e.target.value, cpf_manual: '', nome_manual: '' })
                }
              >
                <option value="">Colaborador cadastrado (RH)</option>
                {colaboradores.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nome_completo} — {c.cpf} — {c.status}
                  </option>
                ))}
              </select>
              <p className="text-xs text-slate-500 text-center">— ou CPF não cadastrado —</p>
              <input
                placeholder="CPF (não cadastrado)"
                disabled={!remessaAtiva || !!pagamento.colaborador_id}
                className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
                value={pagamento.cpf_manual}
                onChange={(e) => setPagamento({ ...pagamento, cpf_manual: e.target.value })}
              />
              <input
                placeholder="Nome completo"
                disabled={!remessaAtiva || !!pagamento.colaborador_id}
                className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
                value={pagamento.nome_manual}
                onChange={(e) => setPagamento({ ...pagamento, nome_manual: e.target.value })}
              />
              {pagamento.tipo_despesa === 'salario' && (
                <input
                  required
                  placeholder="Competência MM/AAAA (ex: 05/2026)"
                  disabled={!remessaAtiva}
                  className="w-full px-3 py-2 rounded-lg bg-amber-950/30 border border-amber-700/50 text-sm"
                  value={pagamento.competencia}
                  onChange={(e) => setPagamento({ ...pagamento, competencia: e.target.value })}
                />
              )}
            </>
          )}
          <input
            type="number"
            step="0.01"
            required
            disabled={!remessaAtiva}
            placeholder="Valor (R$)"
            className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
            value={pagamento.valor}
            onChange={(e) => setPagamento({ ...pagamento, valor: e.target.value })}
          />
          {pagamento.tipo_beneficiario === 'pj' && (
            <label className="block text-xs text-slate-400">
              Nota fiscal padrão (obrigatório)
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                required
                disabled={!remessaAtiva}
                className="w-full mt-1 text-sm"
                onChange={(e) =>
                  setPagamento({ ...pagamento, arquivo_nf_padrao: e.target.files?.[0] || null })
                }
              />
            </label>
          )}
          {pagamento.tipo_beneficiario === 'pf' && pagamento.tipo_despesa === 'salario' && (
            <label className="block text-xs text-slate-400">
              Holerite / comprovante salário (obrigatório)
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                required
                disabled={!remessaAtiva}
                className="w-full mt-1 text-sm"
                onChange={(e) =>
                  setPagamento({ ...pagamento, arquivo_holerite: e.target.files?.[0] || null })
                }
              />
            </label>
          )}
          {pagamento.tipo_beneficiario === 'pf' && pagamento.tipo_despesa !== 'salario' && (
            <div className="space-y-2 p-3 rounded-lg border border-violet-800/40 bg-violet-950/20">
              <p className="text-xs text-violet-300 font-medium">
                Transferência PF — anexos obrigatórios
              </p>
              {[
                { key: 'arquivo_contrato' as const, label: 'Contrato do serviço prestado' },
                { key: 'arquivo_nf_avulsa' as const, label: 'Nota fiscal avulsa' },
                { key: 'arquivo_rpa' as const, label: 'RPA (Recibo Pagamento Autônomo)' },
              ].map(({ key, label }) => (
                <label key={key} className="block text-xs text-slate-400">
                  {label}
                  <input
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg"
                    required
                    disabled={!remessaAtiva}
                    className="w-full mt-1 text-sm"
                    onChange={(e) =>
                      setPagamento({ ...pagamento, [key]: e.target.files?.[0] || null })
                    }
                  />
                </label>
              ))}
            </div>
          )}
          <p className="text-xs text-amber-500">
            PF fora do cadastro RH: limite R$ 10.000. Salário: competência + holerite. Serviços PF: Contrato + NF
            Avulsa + RPA.
          </p>
          <button
            type="submit"
            disabled={!remessaAtiva || salvandoPagamento || enviandoIA}
            className="w-full py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-sm font-medium disabled:opacity-50"
          >
            {salvandoPagamento ? 'Salvando…' : 'Adicionar pagamento à remessa'}
          </button>
        </form>

        {remessaAtiva && remessaAtiva.pagamentos?.length > 0 && (
          <div className="mt-4 space-y-2">
            {remessaAtiva.pagamentos.map((p) => (
              <div key={p.id} className="p-3 rounded-lg bg-slate-800 text-sm border border-slate-700">
                <div className="flex justify-between flex-wrap gap-2">
                  <span>
                    {p.fornecedor_razao_social}: R$ {p.valor.toLocaleString('pt-BR')}
                  </span>
                  <div className="flex gap-2">
                    {p.pf_nao_cadastrado ? (
                      <span className="text-xs text-red-400 border border-red-600/50 px-2 py-0.5 rounded">
                        PF NÃO CADASTRADA
                      </span>
                    ) : null}
                    {p.fornecedor_nao_cadastrado ? (
                      <span className="text-xs text-amber-400 border border-amber-600/50 px-2 py-0.5 rounded">
                        PJ NÃO CADASTRADO
                      </span>
                    ) : null}
                    {p.tipo_despesa === 'salario' && p.competencia && (
                      <span className="text-xs text-blue-400">Sal. {p.competencia}</span>
                    )}
                  </div>
                </div>
                <p className="text-xs text-slate-500 mt-1 font-mono">{p.codigo_pagamento || `PAY-${String(p.id).padStart(6, '0')}`}</p>
                {p.anexos && p.anexos.length > 0 && (
                  <p className="mt-1 text-xs text-violet-400">
                    Anexos: {p.anexos.map((a) => a.tipo_label).join(' · ')}
                  </p>
                )}
              </div>
            ))}
            <button
              onClick={enviarGerente}
              disabled={!saldoOk || enviandoIA || salvandoPagamento}
              className="w-full mt-2 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 font-medium text-sm disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {enviandoIA ? 'Analisando com IA…' : 'Enviar remessa ao gerente (análise IA)'}
            </button>
          </div>
        )}
      </section>
      )}
    </Layout>
  )
}
