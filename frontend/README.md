# Frontend — Guardião de Pagamentos

Interface React (Vite + Tailwind) dos perfis **Analista**, **Gerente** e **Diretoria**.

Documentação completa: [docs/10-construcao-frontend.md](../docs/10-construcao-frontend.md) · [Guia mestre](../docs/00-guia-mestre.md)

## Comandos

```powershell
npm install
npm run dev          # http://localhost:5173
npm run build
npm run demo:verify  # valida demoSnapshot.json (96/110/24)
npm run demo:export  # regera snapshot a partir do seed do backend
```

## Modo demo (Netlify)

Sem backend: carrega `/demoSnapshot.json` e mocka a API via `demoResolver.ts`.  
Confirme no header: `Demo 96 pag. · 110 IA · 24 fraudes`.

Ver [04-deploy-netlify.md](../docs/04-deploy-netlify.md).

## Variáveis de ambiente

| Variável | Uso |
|----------|-----|
| `VITE_API_URL` | URL da API (ex.: `http://127.0.0.1:8000/api`) |
| `VITE_DEMO_MODE` | `true` força demo; `false` desliga |

Arquivo exemplo: `.env.example`
