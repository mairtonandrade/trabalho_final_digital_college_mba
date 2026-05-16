import { Link } from 'react-router-dom'
import Layout from '../components/Layout'

export default function Guia() {
  return (
    <Layout title="Guia do Sistema">
      <div className="max-w-4xl mx-auto space-y-10 text-slate-300 text-sm leading-relaxed">
        <section>
          <h2 className="text-xl font-bold text-white mb-3">Visão geral</h2>
          <p>
            O <strong className="text-emerald-400">Guardião de Pagamentos</strong> é uma plataforma de
            governança financeira com dupla assinatura (Analista + Gerente), validação de saldo bancário,
            cadastro de fornecedores (PJ) e colaboradores (PF), e{' '}
            <strong className="text-red-300">detecção de fraudes por Machine Learning (XGBoost)</strong>{' '}
            complementada por IA generativa (LLaMA) para pareceres de auditoria.
          </p>
        </section>

        <section className="p-5 rounded-xl border border-violet-800/50 bg-violet-950/20">
          <h2 className="text-lg font-bold text-violet-300 mb-3">O que o modelo ML faz</h2>
          <ul className="list-disc list-inside space-y-2">
            <li>Treinado com dataset Kaggle (fraudes em pagamentos online) ou dados sintéticos equivalentes.</li>
            <li>
              Analisa cada pagamento: valor, impacto no saldo, velocity (repetição no dia), beneficiário não
              cadastrado e padrões do dataset.
            </li>
            <li>
              Retorna <strong>score 0–100%</strong> e classifica <strong>FRAUDE</strong> se ≥ 55% (limiar
              calibrado).
            </li>
            <li>Bloqueia envio da remessa se houver pagamento com fraude detectada pelo modelo.</li>
            <li>Gerente precisa justificar para liberar remessas com alerta ML, PF/PJ não cadastrados ou alto risco.</li>
          </ul>
          <p className="mt-3 text-xs text-slate-500">
            Retreinar: <code className="text-slate-400">python ai_models/train_model.py</code>
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-blue-300 mb-3">Perfil: Analista Financeiro</h2>
          <ol className="list-decimal list-inside space-y-2">
            <li>Visualize saldos e registre receitas nas contas bancárias.</li>
            <li>Cadastre fornecedores (KYC) — aguardam aprovação do gerente.</li>
            <li>Selecione conta → Nova remessa → adicione pagamentos (PJ ou PF).</li>
            <li>
              Para <strong>salário</strong>: use PF, tipo despesa Salário e informe competência (MM/AAAA).
            </li>
            <li>
              <strong>PF (serviços):</strong> anexe Contrato, NF Avulsa e RPA. <strong>PJ:</strong> NF padrão.{' '}
              <strong>Salário:</strong> holerite + competência.
            </li>
            <li>O ML analisa na hora; envie à gerência se não houver fraude ML bloqueando.</li>
          </ol>
          <p className="mt-2 text-amber-400 text-xs">
            Demo fraude: valor &gt; R$ 150.000, ou CPF não cadastrado com valor alto, ou nome de arquivo com
            &quot;fake&quot;.
          </p>
        </section>

        <section>
          <h2 className="text-lg font-bold text-purple-300 mb-3">Perfil: Gerente Financeiro</h2>
          <ol className="list-decimal list-inside space-y-2">
            <li>Aprove ou rejeite cadastros de fornecedores e colaboradores (consulte histórico).</li>
            <li>Abra cada anexo, confira valores e documentos e marque o pagamento como revisado.</li>
            <li>Libere a remessa somente após revisar todos os pagamentos (PF: 3 docs · PJ: NF).</li>
            <li>Justificativa obrigatória se ML/fraude ou beneficiário não cadastrado.</li>
          </ol>
        </section>

        <section>
          <h2 className="text-lg font-bold text-emerald-300 mb-3">Perfil: Diretoria</h2>
          <ol className="list-decimal list-inside space-y-2">
            <li>KPIs: saldo total, fraudes IA, pagamentos não cadastrados (PJ e PF).</li>
            <li>Painel <strong>Pontos de atenção</strong>: pagamentos revisados pelo gerente (acompanhamento).</li>
            <li>Botão <strong>Ver pagamento</strong> abre anexos, parecer IA e justificativas.</li>
            <li>Trilha de auditoria imutável (WORM) de todas as ações.</li>
          </ol>
        </section>

        <section>
          <h2 className="text-lg font-bold text-white mb-3">Fluxo do modelo em cada etapa</h2>
          <table className="w-full text-left border border-slate-800 rounded-lg overflow-hidden">
            <thead className="bg-slate-800 text-slate-400">
              <tr>
                <th className="p-2">Etapa</th>
                <th className="p-2">ML</th>
                <th className="p-2">GenAI</th>
              </tr>
            </thead>
            <tbody>
              {[
                ['Cadastro fornecedor', '—', '—'],
                ['Adicionar pagamento', 'Score + classificação fraude', 'Parecer auditoria'],
                ['Enviar remessa', 'Bloqueio se fraude ML', '—'],
                ['Aprovação gerente', 'Exige justificativa se alerta', 'E-mail auditoria'],
                ['Dashboard diretoria', 'KPIs e listagens', 'Resumos executivos'],
              ].map(([e, ml, ai]) => (
                <tr key={e} className="border-t border-slate-800">
                  <td className="p-2">{e}</td>
                  <td className="p-2 text-red-300">{ml}</td>
                  <td className="p-2 text-cyan-300">{ai}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <Link to="/" className="inline-block text-emerald-400 hover:underline">
          ← Voltar à seleção de perfil
        </Link>
      </div>
    </Layout>
  )
}
