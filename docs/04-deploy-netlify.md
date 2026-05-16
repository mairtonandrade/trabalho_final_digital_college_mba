# 04 — Deploy no Netlify

## Frontend (Netlify)

1. Conecte o repositório GitHub no [Netlify](https://app.netlify.com)
2. Configuração automática via `netlify.toml`:
   - Base: `frontend`
   - Build: `npm run build`
   - Publish: `dist`
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

- [ ] `GET {API}/api/health` retorna `ok`
- [ ] Login por perfil na home funciona
- [ ] Gerente vê remessas do seed
- [ ] Diretoria exibe KPIs e detecções IA

## Build local (validação)

```powershell
cd frontend
npm run build
```

Artefatos em `frontend/dist/` — mesmo conteúdo publicado no Netlify.
