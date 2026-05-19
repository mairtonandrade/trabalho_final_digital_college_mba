# 07 — Mapa de dados de demonstração

## Onde cada perfil vê o quê

| Dado | Analista | Gerente | Diretoria |
|------|----------|---------|-----------|
| Remessas 6 meses | Lista / devolvidas | Aguardando + catálogo IA | KPIs total remessas |
| Histórico IA (PAY-XXXXXX) | — | Por pagamento | Detecções IA |
| Cadastros + histórico | CadastrosPanel | Aprovações KYC | Auditoria WORM |
| Fraudes ML/GenAI | — | Badges + reanálise | Detecções + alertas |
| Contas bancárias | ContasPanel | ContasPanel | Saldo total + ContasPanel |
| PJ/PF não cadastrados | — | Revisão | Tabelas dedicadas |
| Pontos de atenção | — | Revisão doc. | Tabela executiva |

## Saldos operacionais (após seed)

| Conta | Saldo ~ |
|-------|---------|
| Operacional Principal | R$ 1.180.000 |
| Folha de Pagamento | R$ 355.000 |
| Fornecedores | R$ 590.000 |
| **Total** | **R$ 2.125.000** |

## Recriar banco local

```powershell
# Pare o uvicorn antes
cd backend
.\venv_mba\Scripts\python.exe scripts\reseed_demo.py
.\venv_mba\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

## KPIs da Diretoria (seed padrão)

Com banco recriado (`reseed_demo.py`) ou Netlify em modo demo (`/demoSnapshot.json`):

| Indicador | Valor |
|-----------|-------|
| Pagamentos analisados (IA) | **96** |
| Execuções IA | **110** |
| Fraudes ML | **24** |
| PJ não cadastrados | **9** |
| PF não cadastradas | **6** |
| Valor analisado (histórico) | ~**R$ 5,81 mi** |

## Paridade local × Netlify

O Netlify usa `frontend/public/demoSnapshot.json` (servido em `/demoSnapshot.json`), exportado do **mesmo seed** do backend:

```powershell
python scripts/export_demo_snapshot.py
cd frontend
npm run demo:verify
```

Após alterar `seed_demo_historico.py` ou `seed_catalogo_fraude.py`, rode o export e faça commit do JSON.

**Local com API:** `VITE_API_URL` no `.env` (proxy `/api` → uvicorn). Se os números divergirem, recrie o banco com `backend/scripts/reseed_demo.py`.
