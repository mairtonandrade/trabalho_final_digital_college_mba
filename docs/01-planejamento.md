# 01 — Planejamento do projeto

## Problema

Empresas de médio porte processam dezenas de remessas de pagamento por mês. Sem governança, há risco de fraude, pagamentos a beneficiários não cadastrados e falta de trilha para auditoria.

## Solução

**Guardião de Pagamentos** — plataforma web com:

1. **Dupla aprovação** (analista monta → gerente libera)
2. **IA no envio** — XGBoost + heurísticas + parecer GenAI
3. **Três perfis** — operação, checker e diretoria executiva

## Entregas do MBA

| Entrega | Status |
|---------|--------|
| Frontend React responsivo | ✅ |
| API FastAPI + SQLite | ✅ |
| Modelo XGBoost treinável | ✅ |
| GenAI (Ollama ou template) | ✅ |
| Seed 6 meses + histórico IA | ✅ |
| Documentação e deploy Netlify | ✅ |

## Cronograma sugerido (apresentação)

1. Contexto e problema (2 min)
2. Demo analista — remessa + envio IA (5 min)
3. Demo gerente — revisão ML/GenAI e liberação (5 min)
4. Demo diretoria — KPIs e detecções (3 min)
5. Arquitetura técnica e IA (5 min)

Documento de planejamento original: [`Planejamento_Projeto_Aprovacao_Pagamentos.md`](../Planejamento_Projeto_Aprovacao_Pagamentos.md)
