/** Detecta modo demo (Netlify sem API configurada). */

function isNetlifyDemoHost(): boolean {
  if (typeof window === 'undefined') return false
  const h = window.location.hostname
  return h.endsWith('.netlify.app') || h.endsWith('.netlify.live')
}

export function isDemoMode(): boolean {
  if (import.meta.env.VITE_DEMO_MODE === 'true') return true
  if (import.meta.env.VITE_DEMO_MODE === 'false') return false
  // Netlify sem API configurada → sempre demo
  if (isNetlifyDemoHost() && !import.meta.env.VITE_API_URL) return true
  // Produção sem URL de API → usa dados demo (evita tela branca no Netlify)
  return import.meta.env.PROD && !import.meta.env.VITE_API_URL
}

