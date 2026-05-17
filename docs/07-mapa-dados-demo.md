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

## Netlify (modo demo)

Sem `VITE_API_URL`, o frontend usa `demoResolver.ts` com os mesmos tipos de dados (auditoria, detecções, saldos).
