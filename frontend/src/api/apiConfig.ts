/** Detecta modo demo (Netlify sem API configurada). */

export function isDemoMode(): boolean {
  if (import.meta.env.VITE_DEMO_MODE === 'true') return true
  if (import.meta.env.VITE_DEMO_MODE === 'false') return false
  // Produção sem URL de API → usa dados demo (evita tela branca no Netlify)
  return import.meta.env.PROD && !import.meta.env.VITE_API_URL
}

