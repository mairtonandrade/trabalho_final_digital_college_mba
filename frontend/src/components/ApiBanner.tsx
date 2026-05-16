import { isDemoMode, apiBaseLabel } from '../api/apiConfig'

export default function ApiBanner() {
  if (!isDemoMode()) return null

  return (
    <div className="mb-6 p-4 rounded-xl border border-amber-500/40 bg-amber-950/30 text-amber-100 text-sm">
      <strong>Modo demonstração</strong> — os dados exibidos são de exemplo. Para dados reais do
      backend, configure <code className="text-amber-300">VITE_API_URL</code> no Netlify e faça
      redeploy. Atual: {apiBaseLabel()}
    </div>
  )
}
