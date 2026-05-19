# 04 — Deploy no Netlify

## Diagnóstico rápido (produção)

| Teste | URL | Resultado esperado |
|-------|-----|-------------------|
| Snapshot | `/demoSnapshot.json` | JSON ~1 MB, início com `{"meta":` |
| Versão do build | `/version.json` | `{"commit":"abc1234",...}` |
| Bundle | Ver código-fonte de `/` | `index-*.js` **diferente** do deploy anterior |
| Header app | Qualquer painel | `Demo 96 pag. · 110 IA · 24 fraudes · build xxx` |

Se `/demoSnapshot.json` abrir como **página HTML** do app → redirect SPA engoliu o arquivo (corrigido em `_redirects`) ou deploy antigo ainda em produção.

---

## Opções em *Trigger deploy*

| Opção | O que faz | Quando usar |
|-------|-----------|-------------|
| **Deploy project** | Build normal reutilizando **cache** de dependências (`node_modules`) e artefatos de builds anteriores do Netlify | Deploy rotineiro após push; mais rápido |
| **Deploy project without cache** | Build **do zero**: baixa dependências de novo, ignora cache do Netlify | KPIs errados (4 em vez de 96), JS antigo, ou após mudar `demoSnapshot.json` / `package-lock.json` |

**Recomendação para este projeto:** após alterar dados demo ou dependências, use **Deploy project without cache**. Depois confira no site:

- Header: `Demo 96 pag. · 110 IA · 24 fraudes`
- URL: `https://SEU-SITE.netlify.app/demoSnapshot.json` (JSON grande com `"pagamentos_analisados": 96`)

Se o deploy concluir mas a produção não mudar, clique em **Publish deploy** (quando aparecer) e faça **Ctrl+F5** no navegador.

---

## Problemas comuns no Netlify

### Perfis redirecionam para a home ou tela escura

1. **Build antigo em cache** — *Trigger deploy* → **Deploy project without cache** (equivalente a limpar cache de build).
2. **Modo demo** — o `netlify.toml` define `VITE_DEMO_MODE=true` para funcionar sem backend. Os KPIs vêm de `/demoSnapshot.json` (mesmos 96 / 110 / 24 do seed local). No header da app aparece `Demo 96 pag. · 110 IA · 24 fraudes` quando o snapshot carregou.
3. **Publicar o deploy** — após build, clique em **Publish deploy** se o painel Netlify mostrar essa opção (senão a produção continua no bundle antigo).
4. **Cache** — use *Clear cache and deploy site* se os números não mudarem; depois Ctrl+F5 no navegador.
5. **Rotas SPA** — `/* → /index.html` (200) em `netlify.toml` e `frontend/public/_redirects`.

### API retorna HTML em vez de JSON

Sem modo demo, chamadas a `/api` no Netlify recebem o `index.html` e o app quebra. Use `VITE_DEMO_MODE=true` (padrão no repo) ou configure `VITE_API_URL` com API hospedada.

## Frontend (Netlify)

1. Conecte o repositório GitHub no [Netlify](https://app.netlify.com)
2. Configuração automática via `netlify.toml`:
   - Base: `frontend`
   - Build: `npm ci && npm run demo:verify && npm run build`
   - Publish: `dist`
   - `VITE_DEMO_MODE=true` (modo demo padrão)
3. Variável de ambiente:

```
VITE_API_URL=https://SUA-API.em.render.com
```

4. Deploy — a SPA usa `_redirects` para rotas React.

## Backend (Render / Railway / similar)

O SQLite em disco **não** é ideal para serverless. Para apresentação:

**Opção A — Demo local + Netlify só UI**  
Apresente o frontend no Netlify apontando para API local via túnel (ngrok) — apenas para banca presencial.

**Opção B — API hospedada (recomendado)**  
1. Deploy `backend/` com `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
2. Volume persistente para `backend/data/`
3. `VITE_API_URL` no Netlify = URL pública da API
4. CORS já liberado (`allow_origins=["*"]`)

## Checklist pós-deploy

**Modo demo (padrão, sem API):**

- [ ] `/demoSnapshot.json` abre no navegador (não 404)
- [ ] Header mostra `Demo 96 pag. · 110 IA · 24 fraudes`
- [ ] Diretoria → Visão executiva: **96** / **110** / **24**
- [ ] Perfis `/analista`, `/gerente`, `/diretoria` abrem sem tela branca

**Com API hospedada (`VITE_API_URL`):**

- [ ] `GET {API}/api/health` retorna `ok`
- [ ] Gerente vê remessas do seed
- [ ] Diretoria exibe KPIs alinhados ao banco (reseed se necessário)

## Build local (validação)

```powershell
cd frontend
npm run build
```

Artefatos em `frontend/dist/` — mesmo conteúdo publicado no Netlify.
