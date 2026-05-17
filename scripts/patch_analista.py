from pathlib import Path

p = Path(r"c:\trabalho_final_digital_college_mba\frontend\src\pages\Analista.tsx")
t = p.read_text(encoding="utf-8")

old = """      <motion.div className="mb-8">
        <CadastrosPanel modo="analista" />
      </motion.div>

      <motion.div className="grid lg:grid-cols-2 gap-8 mb-8">
        <ContasPanel onSelectConta={(id) => setContaSelecionada(id)} />
        <section className="space-y-6">
          <motion.div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <h2 className="font-semibold text-lg mb-4">Novo Fornecedor (KYC)</h2>
            <form onSubmit={criarFornecedor} className="space-y-3">
              {(['cnpj', 'razao_social', 'banco', 'agencia', 'conta'] as const).map((f) => (
                <input
                  key={f}
                  required
                  placeholder={f.replace('_', ' ')}
                  className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm"
                  value={novoForn[f]}
                  onChange={(e) => setNovoForn({ ...novoForn, [f]: e.target.value })}
                />
              ))}
              <button type="submit" className="w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-sm font-medium">
                Solicitar cadastro
              </button>
            </form>
          </motion.div>
        </section>
      </motion.div>

      <section className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">"""

old = old.replace("motion.div", "div")

new = """      <ModuloSelector modulos={MODULOS_ANALISTA} ativo={modulo} onChange={setModulo} />

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
        <motion.div className="mb-8">
          <CadastrosPanel modo="analista" secao="consulta" />
        </motion.div>
      )}

      {modulo === 'contas' && (
        <motion.div className="mb-8">
          <ContasPanel onSelectConta={(id) => setContaSelecionada(id)} />
        </motion.div>
      )}

      {modulo === 'remessas' && (
      <section className="panel-surface">"""

new = new.replace("motion.div", "motion.div").replace("<motion.div", "<motion.div")
new = new.replace("motion.div", "div")

if old not in t:
    raise SystemExit("block not found")

t = t.replace(old, new, 1)
t = t.replace("      </section>\n    </Layout>", "      </section>\n      )}\n    </Layout>", 1)
p.write_text(t, encoding="utf-8")
print("patched")
