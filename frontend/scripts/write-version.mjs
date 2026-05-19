import { execSync } from 'node:child_process'
import { writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
let commit = 'unknown'
try {
  commit = execSync('git rev-parse --short HEAD', { cwd: join(root, '..'), encoding: 'utf8' }).trim()
} catch {
  /* fora do git */
}

const payload = {
  commit,
  builtAt: new Date().toISOString(),
  demoSnapshot: 'public/demoSnapshot.json',
}

writeFileSync(join(root, 'public', 'version.json'), JSON.stringify(payload, null, 2))
console.log('version.json ->', commit)
