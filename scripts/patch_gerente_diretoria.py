# -*- coding: utf-8 -*-
from pathlib import Path

# --- Gerente ---
gp = Path(r"c:\trabalho_final_digital_college_mba\frontend\src\pages\Gerente.tsx")
gt = gp.read_text(encoding="utf-8")

if "ModuloSelector" not in gt:
    gt = gt.replace(
        "import PageHeader from '../components/ui/PageHeader'",
        "import PageHeader from '../components/ui/PageHeader'\nimport ModuloSelector, { type ModuloItem } from '../components/ui/ModuloSelector'\n\nconst MODULOS_GERENTE: ModuloItem[] = [\n  { id: 'remessas', titulo: 'Remessas', descricao: 'Aprovar, devolver e liberar pagamentos', icone: '✅' },\n  { id: 'fornecedores', titulo: 'Fornecedores', descricao: 'Aprovar cadastros e KYC', icone: '🏢' },\n  { id: 'cadastros', titulo: 'Cadastros', descricao: 'Colaboradores e solicitações', icone: '📁' },\n  { id: 'contas', titulo: 'Contas e extrato', descricao: 'Saldos e movimentação', icone: '🏦' },\n]",
    )
    gt = gt.replace(
        "  const [reanalisando, setReanalisando] = useState(false)",
        "  const [reanalisando, setReanalisando] = useState(false)\n  const [modulo, setModulo] = useState('remessas')",
    )

    insert_after = """      {msg && (
        <div className="mb-6 p-4 rounded-lg bg-slate-800 border border-slate-700 text-sm">{msg}</div>
      )}

      <FiltrosMovimentacao"""

    replacement = """      {msg && (
        <div className="mb-6 p-4 rounded-lg bg-slate-800/90 border border-slate-500 text-sm text-slate-100">{msg}</div>
      )}

      <ModuloSelector modulos={MODULOS_GERENTE} ativo={modulo} onChange={setModulo} />

      {(modulo === 'remessas' || modulo === 'fornecedores') && (
      <FiltrosMovimentacao"""

    gt = gt.replace(insert_after, replacement, 1)

    gt = gt.replace(
        """      <div className="mb-10">
        <ContasPanel />
      </div>

      <div className="mb-10">
        <CadastrosPanel modo="gerente" />
      </div>

      <section className="mb-10">
        <h2 className="text-lg font-semibold mb-4">Fornecedores pendentes (aprovação inicial)</h2>""",
        """      {modulo === 'contas' && (
        <div className="mb-10">
          <ContasPanel />
        </motion.div>
      )}

      {modulo === 'cadastros' && (
        <motion.div className="mb-10">
          <CadastrosPanel modo="gerente" />
        </motion.div>
      )}

      {modulo === 'fornecedores' && (
      <section className="mb-10 panel-surface">
        <h2 className="section-title mb-4">Fornecedores — aprovação e histórico</h2>""",
    )
    gt = gt.replace("motion.div", "div")

    # Close fornecedores section before remessas section
    gt = gt.replace(
        """      </section>

      <section className="mb-10">
        <h2 className="text-lg font-semibold mb-4">Fornecedores pendentes</h2>""",
        """      </section>
      )}

      {modulo === 'fornecedores' && (
      <section className="mb-10 panel-surface">
        <h2 className="section-title mb-4">Cadastros aguardando aprovação</h2>""",
    )

    gt = gt.replace(
        """      </section>

      <section>
        <h2 className="text-lg font-semibold mb-4">Remessas — 2ª assinatura</h2>""",
        """      </section>
      )}

      {modulo === 'remessas' && (
      <section className="panel-surface">
        <h2 className="section-title mb-4">Remessas — 2ª assinatura</h2>""",
    )

    gt = gt.replace(
        "      {emailPreview && (",
        "      )}\n\n      {emailPreview && (",
    )

    gp.write_text(gt, encoding="utf-8")
    print("gerente patched")

# --- Diretoria ---
dp = Path(r"c:\trabalho_final_digital_college_mba\frontend\src\pages\Diretoria.tsx")
dt = dp.read_text(encoding="utf-8")

if "ModuloSelector" not in dt:
    dt = dt.replace(
        "import PageHeader from '../components/ui/PageHeader'",
        "import PageHeader from '../components/ui/PageHeader'\nimport ModuloSelector, { type ModuloItem } from '../components/ui/ModuloSelector'\n\nconst MODULOS_DIRETORIA: ModuloItem[] = [\n  { id: 'dashboard', titulo: 'Visão executiva', descricao: 'Indicadores e gráficos IA', icone: '📊' },\n  { id: 'historico', titulo: 'Histórico IA', descricao: 'Fluxos e trilha por pagamento', icone: '🔍' },\n  { id: 'contas', titulo: 'Contas', descricao: 'Saldos bancários', icone: '🏦' },\n  { id: 'alertas', titulo: 'Alertas e exceções', descricao: 'Fraudes, PF/PJ e pontos de atenção', icone: '⚠️' },\n  { id: 'auditoria', titulo: 'Auditoria', descricao: 'Trilha WORM e visão operacional', icone: '📜' },\n]",
    )
    dt = dt.replace(
        "  const [somenteFraude, setSomenteFraude] = useState(false)",
        "  const [somenteFraude, setSomenteFraude] = useState(false)\n  const [modulo, setModulo] = useState('dashboard')",
    )

    dt = dt.replace(
        """      <FiltrosMovimentacao
        periodo={periodo}
        onPeriodoChange={setPeriodo}
        datasReferencia={datasReferencia}
        somenteFraude={somenteFraude}
        onSomenteFraudeChange={setSomenteFraude}
        totalVisivel={totalVisivel}
        totalGeral={totalMovimentos}
      />

      <IndicadoresExecutivos kpis={kpisPainel} periodo={periodo} />

      <PainelGraficosIA data={metricasExibir} />

      <HistoricoControleIA""",
        """      <ModuloSelector modulos={MODULOS_DIRETORIA} ativo={modulo} onChange={setModulo} />

      {(modulo === 'dashboard' || modulo === 'historico' || modulo === 'alertas') && (
      <FiltrosMovimentacao
        periodo={periodo}
        onPeriodoChange={setPeriodo}
        datasReferencia={datasReferencia}
        somenteFraude={somenteFraude}
        onSomenteFraudeChange={setSomenteFraude}
        totalVisivel={totalVisivel}
        totalGeral={totalMovimentos}
      />
      )}

      {modulo === 'dashboard' && (
        <>
          <IndicadoresExecutivos kpis={kpisPainel} periodo={periodo} />
          <PainelGraficosIA data={metricasExibir} />
        </>
      )}

      {modulo === 'historico' && (
      <HistoricoControleIA""",
    )

    dt = dt.replace(
        """      />

      <div className="mb-8">
        <ContasPanel ocultarReceita />
      </div>

      <section className="mb-8 rounded-xl border border-red-800/50 bg-red-950/20 p-5">""",
        """      />
      )}

      {modulo === 'contas' && (
        <div className="mb-8">
          <ContasPanel ocultarReceita />
        </motion.div>
      )}

      {modulo === 'alertas' && (
      <>
      <section className="mb-8 rounded-xl border border-red-700/60 bg-red-950/30 p-5">""",
    )
    dt = dt.replace("motion.div", "motion.div").replace("<motion.div", "<motion.div")
    dt = dt.replace("motion.div", "motion.div")

    dt = dt.replace(
        """      <motion.div className="grid lg:grid-cols-2 gap-8 mb-8">""",
        """      </>
      )}

      {modulo === 'auditoria' && (
      <>
      <motion.div className="grid lg:grid-cols-2 gap-8 mb-8">""",
    )
    dt = dt.replace("motion.div", "div")

    dt = dt.replace(
        """      </section>

      {detalhePagamentoId && (""",
        """      </section>
      </>
      )}

      {detalhePagamentoId && (""",
    )

    dp.write_text(dt, encoding="utf-8")
    print("diretoria patched")
