import { Link, useNavigate } from 'react-router-dom'
import { useRole } from '../context/RoleContext'

const personas = [
  {
    role: 'analista' as const,
    title: 'Analista Financeiro',
    desc: 'Monte remessas com vários pagamentos, anexe documentos e envie para análise IA em lote.',
    icon: '📋',
    color: 'from-cyan-500 to-blue-600',
    border: 'hover:border-cyan-500/40',
    path: '/analista',
  },
  {
    role: 'gerente' as const,
    title: 'Gerente Financeiro',
    desc: 'Revise resultados ML + GenAI, documentos, devolva correções e libere com dupla assinatura.',
    icon: '🛡️',
    color: 'from-violet-500 to-purple-600',
    border: 'hover:border-violet-500/40',
    path: '/gerente',
  },
  {
    role: 'diretoria' as const,
    title: 'Diretoria',
    desc: 'KPIs executivos, detecções de fraude, pontos de atenção e trilha de auditoria WORM.',
    icon: '📊',
    color: 'from-emerald-500 to-teal-600',
    border: 'hover:border-emerald-500/40',
    path: '/diretoria',
  },
]

const features = [
  { label: 'XGBoost anti-fraude', desc: 'Score e classificação' },
  { label: 'GenAI auditoria', desc: 'Pareceres automáticos' },
  { label: 'Dupla aprovação', desc: 'Analista + Gerente' },
  { label: 'Trilha WORM', desc: 'Histórico imutável' },
]

export default function Home() {
  const navigate = useNavigate()
  const { setRole } = useRole()

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-white/5 bg-slate-950/50 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-4 py-6 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center font-bold text-white">
              GP
            </div>
            <span className="font-semibold text-white">Guardião de Pagamentos</span>
          </div>
          <Link to="/guia" className="text-sm text-emerald-400 hover:text-emerald-300 transition">
            Documentação →
          </Link>
        </div>
      </header>

      <section className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="text-center max-w-3xl mb-10">
          <p className="inline-block mb-4 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            MBA Digital College · Ciência de Dados & GenAI
          </p>
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-5 leading-tight tracking-tight">
            Governança financeira com{' '}
            <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              inteligência artificial
            </span>
          </h1>
          <p className="text-slate-200 text-lg leading-relaxed">
            Plataforma corporativa para aprovação de pagamentos com detecção de fraudes,
            revisão documental e auditoria em conformidade com as melhores práticas.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full max-w-3xl mb-12">
          {features.map((f) => (
            <div key={f.label} className="glass-card p-3 text-center">
              <p className="text-xs font-semibold text-emerald-400">{f.label}</p>
              <p className="text-[10px] text-slate-300 mt-0.5">{f.desc}</p>
            </div>
          ))}
        </div>

        <p className="text-sm text-slate-300 mb-6 font-medium">Selecione seu perfil para continuar</p>

        <div className="grid md:grid-cols-3 gap-5 w-full max-w-5xl">
          {personas.map((p) => (
            <button
              key={p.role}
              type="button"
              onClick={() => {
                setRole(p.role)
                navigate(p.path)
              }}
              className={`glass-card group text-left p-6 ${p.border} hover:scale-[1.02] hover:shadow-2xl hover:shadow-black/30`}
            >
              <span className="text-3xl mb-4 block">{p.icon}</span>
              <div className={`h-1 w-12 rounded-full bg-gradient-to-r ${p.color} mb-4`} />
              <h2 className="text-lg font-bold text-white mb-2">{p.title}</h2>
              <p className="text-slate-200 text-sm leading-relaxed mb-4">{p.desc}</p>
              <span
                className={`text-sm font-semibold bg-gradient-to-r ${p.color} bg-clip-text text-transparent`}
              >
                Acessar painel →
              </span>
            </button>
          ))}
        </div>
      </section>
    </div>
  )
}
