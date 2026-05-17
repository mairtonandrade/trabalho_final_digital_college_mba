# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"c:\trabalho_final_digital_college_mba\frontend\src\components\CadastrosPanel.tsx")
t = p.read_text(encoding="utf-8")

start = t.find('      {mostrarConsulta && (\n      <motion.div className="grid lg:grid-cols-2 gap-6">')
if start < 0:
    start = t.find('      {mostrarConsulta && (\n      <div className="grid lg:grid-cols-2 gap-6">')
end = t.find("      {mostrarConsulta && (editCol || editForn)")
if start < 0 or end < 0:
    raise SystemExit(f"markers not found start={start} end={end}")

new_block = """      {mostrarConsulta && (
      <div className="space-y-8">
        <div className="rounded-xl border border-blue-800/40 bg-slate-950/50 p-5 sm:p-6 min-h-[min(70vh,520px)] flex flex-col">
          <motion.div className="flex flex-wrap items-center justify-between gap-2 mb-4">
            <h3 className="text-lg font-semibold text-white">Colaboradores</h3>
            <span className="text-sm text-slate-300 px-3 py-1 rounded-full border border-slate-600 bg-slate-800/80">
              {colaboradores.length} cadastrado(s)
            </span>
          </motion.div>
          <motion.div className="flex-1 space-y-3 overflow-y-auto pr-1 min-h-[360px] max-h-[min(65vh,480px)]">
            {colaboradores.map((c) => (
              <motion.div
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
                <motion.div className="flex flex-wrap gap-2 mt-3">
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
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        <motion.div className="rounded-xl border border-amber-800/40 bg-slate-950/50 p-5 sm:p-6 min-h-[min(70vh,520px)] flex flex-col">
          <motion.div className="flex flex-wrap items-center justify-between gap-2 mb-4">
            <h3 className="text-lg font-semibold text-white">Fornecedores</h3>
            <span className="text-sm text-slate-300 px-3 py-1 rounded-full border border-slate-600 bg-slate-800/80">
              {fornecedores.length} cadastrado(s)
            </span>
          </motion.div>
          <motion.div className="flex-1 space-y-3 overflow-y-auto pr-1 min-h-[360px] max-h-[min(65vh,480px)]">
            {fornecedores.map((f) => (
              <motion.div
                key={f.id}
                className="p-4 rounded-xl bg-slate-800/90 text-sm border border-slate-600/70 hover:border-amber-600/40 transition"
              >
                <p className="font-semibold text-white text-base">{f.razao_social}</p>
                <p className="text-slate-300 mt-1">CNPJ {f.cnpj}</p>
                <p className={`mt-1 font-medium ${statusClass[f.status] || ''}`}>
                  {statusLabel[f.status] || f.status}
                </p>
                <motion.div className="flex flex-wrap gap-2 mt-3">
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
                </motion.div>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </motion.div>
      )}

"""

new_block = new_block.replace("motion.div", "div")
p.write_text(t[:start] + new_block + t[end:], encoding="utf-8")
print("ok")
