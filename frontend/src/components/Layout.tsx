import { Link, useLocation } from 'react-router-dom'
import ApiBanner from './ApiBanner'
import { useRole } from '../context/RoleContext'

const roleLabels: Record<string, string> = {
  analista: 'Analista Financeiro',
  gerente: 'Gerente Financeiro',
  diretoria: 'Diretoria',
}

const navByRole: Record<string, { to: string; label: string }[]> = {
  analista: [
    { to: '/analista', label: 'Remessas' },
    { to: '/guia', label: 'Guia' },
  ],
  gerente: [
    { to: '/gerente', label: 'Aprovações' },
    { to: '/guia', label: 'Guia' },
  ],
  diretoria: [
    { to: '/diretoria', label: 'Executivo' },
    { to: '/guia', label: 'Guia' },
  ],
}

export default function Layout({
  children,
  title,
}: {
  children: React.ReactNode
  title: string
}) {
  const { role, setRole } = useRole()
  const location = useLocation()
  const nav = role ? navByRole[role] : []

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-50 border-b border-white/5 bg-slate-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-900/40">
                <span className="text-white font-bold text-sm">GP</span>
              </div>
              <div className="hidden sm:block">
                <p className="text-xs font-semibold tracking-wider text-emerald-400 uppercase">
                  Guardião de Pagamentos
                </p>
                <p className="text-sm text-slate-200 group-hover:text-white transition">
                  {title}
                </p>
              </div>
            </Link>

            <nav className="hidden md:flex items-center gap-1">
              {nav.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                    location.pathname === item.to
                      ? 'bg-emerald-500/15 text-emerald-300'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </nav>

            <div className="flex items-center gap-2">
              {role && (
                <span className="hidden lg:inline text-xs text-slate-500 border border-slate-700 px-2 py-1 rounded-lg">
                  {roleLabels[role]}
                </span>
              )}
              <Link to="/guia" className="btn-secondary text-xs py-2 hidden sm:inline-flex">
                Guia
              </Link>
              <Link
                to="/"
                onClick={() => setRole(null)}
                className="btn-secondary text-xs py-2"
              >
                Sair
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">
        <ApiBanner />
        {children}
      </main>

      <footer className="border-t border-white/5 py-6 mt-auto">
        <p className="text-center text-xs text-slate-600 max-w-7xl mx-auto px-4">
          Guardião de Pagamentos · MBA Digital College · Dupla aprovação + ML (XGBoost) + GenAI
        </p>
      </footer>
    </div>
  )
}
