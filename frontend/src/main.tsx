import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { isDemoMode } from './api/apiConfig'
import { initDemoSnapshot } from './api/demoSnapshotData'
import './index.css'

async function bootstrap() {
  if (isDemoMode()) {
    await initDemoSnapshot()
  }
  const { default: App } = await import('./App.tsx')
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <App />
    </StrictMode>
  )
}

bootstrap().catch((err) => {
  console.error(err)
  const root = document.getElementById('root')
  if (root) {
    root.innerHTML = `<div style="padding:2rem;font-family:system-ui;color:#fecaca;background:#450a0a;min-height:100vh">
      <h1>Erro ao carregar demonstração</h1>
      <p>${err instanceof Error ? err.message : String(err)}</p>
      <p style="color:#94a3b8;margin-top:1rem">Tente atualizar a página (Ctrl+F5). Se persistir, o deploy pode estar incompleto.</p>
    </div>`
  }
})
