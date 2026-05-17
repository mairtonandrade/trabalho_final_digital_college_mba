/**
 * Captura screenshots reais da UI para docs/assets/.
 * Pré-requisitos: backend :8000, frontend :5173 (npm run dev).
 *
 * Uso: node scripts/capture_doc_screenshots.mjs
 */
import { createRequire } from 'module'
import { mkdir } from 'fs/promises'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const require = createRequire(join(__dirname, '../frontend/package.json'))
const { chromium } = require('playwright')
const OUT = join(__dirname, '..', 'docs', 'assets')
const BASE = process.env.GP_BASE_URL || 'http://localhost:5173'

async function waitForApp(page) {
  await page.waitForLoadState('networkidle', { timeout: 20000 }).catch(() => {})
  await page.waitForTimeout(1500)
}

async function gotoPerfil(page, perfil, path) {
  await page.goto(BASE)
  await page.evaluate((p) => localStorage.setItem('mba_role', p), perfil)
  await page.goto(`${BASE}${path}`)
  await waitForApp(page)
}

async function main() {
  await mkdir(OUT, { recursive: true })

  const browser = await chromium.launch({ headless: true })
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    colorScheme: 'dark',
  })
  const page = await context.newPage()

  console.log('Capturando', BASE, '→', OUT)

  await page.goto(BASE)
  await waitForApp(page)
  await page.screenshot({ path: join(OUT, '01-home.png') })
  console.log('OK 01-home.png')

  await gotoPerfil(page, 'analista', '/analista')
  await page.waitForSelector('text=Remessas e pagamentos', { timeout: 15000 })
  await page.screenshot({ path: join(OUT, '02-analista.png') })
  console.log('OK 02-analista.png')

  await gotoPerfil(page, 'gerente', '/gerente')
  await page.waitForSelector('text=Aprovações e revisão IA', { timeout: 15000 })
  const remessas = page.getByText('Remessas — 2ª assinatura').first()
  if (await remessas.isVisible().catch(() => false)) {
    await remessas.scrollIntoViewIfNeeded()
    await page.waitForTimeout(800)
  }
  await page.screenshot({ path: join(OUT, '03-gerente-ia.png') })
  console.log('OK 03-gerente-ia.png')

  await gotoPerfil(page, 'diretoria', '/diretoria')
  await page.waitForSelector('text=Visão executiva', { timeout: 15000 })
  await page.screenshot({ path: join(OUT, '04-diretoria.png') })
  console.log('OK 04-diretoria.png')

  const paineis = page.getByRole('heading', { name: 'Painéis de detecção IA' })
  await paineis.scrollIntoViewIfNeeded({ timeout: 10000 }).catch(() => {})
  await page.waitForTimeout(2000)
  await page.screenshot({ path: join(OUT, '05-paineis-ia.png') })
  console.log('OK 05-paineis-ia.png')

  await browser.close()
  console.log('Concluído. Regere 06-fluxo-completo.png com scripts/regenerate_doc_assets.ps1')
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
