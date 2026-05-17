# 06 — Roadmap produto → produção

Evolução do MVP atual para SaaS multi-cliente seguro. Estimativas para **1 dev full-time** (ajustar conforme equipe).

## Fase 0 — Hoje (MVP MBA) ✅

- [x] Frontend React + 3 perfis
- [x] API FastAPI + SQLite
- [x] XGBoost + heurísticas + GenAI template
- [x] Trilha auditoria + histórico IA versionado
- [x] Deploy Netlify (modo demo ou API)
- [x] Documentação técnica e modelo-ia

## Fase 1 — Fundação SaaS (4–6 semanas)

| Item | Esforço | Prioridade |
|------|---------|------------|
| Migrar SQLite → **PostgreSQL** | 1 sem | P0 |
| Tabela `tenants`, `users` com senha hash | 1 sem | P0 |
| `tenant_id` em todas as entidades | 1 sem | P0 |
| Login JWT (substituir localStorage role) | 1 sem | P0 |
| Middleware tenant em todos os routers | 3 dias | P0 |
| Testes isolamento tenant | 3 dias | P0 |
| CI/CD (GitHub Actions → deploy) | 3 dias | P1 |

## Fase 2 — Dados e anexos (3–4 semanas)

| Item | Esforço | Prioridade |
|------|---------|------------|
| Upload anexos → S3/R2 | 1 sem | P0 |
| URLs assinadas download | 2 dias | P0 |
| Filas Redis: IA assíncrona no envio | 1 sem | P1 |
| Limites por plano (pagamentos/mês) | 3 dias | P1 |
| Export CSV auditoria / remessas | 3 dias | P1 |

## Fase 3 — Comercial e operação (2–3 semanas)

| Item | Esforço | Prioridade |
|------|---------|------------|
| Portal admin tenants (interno) | 1 sem | P1 |
| Billing Stripe / Asaas (assinatura) | 1 sem | P2 |
| E-mails transacionais (envio, liberação) | 3 dias | P2 |
| Ambiente staging por cliente piloto | 2 dias | P1 |

## Fase 4 — Enterprise e escala (contínuo)

| Item | Esforço | Prioridade |
|------|---------|------------|
| SSO SAML/OIDC | 2 sem | P2 |
| MFA | 1 sem | P2 |
| Modelo ML por tenant | 2 sem | P3 |
| Webhooks ERP | 2 sem | P2 |
| Status page + alertas PagerDuty | 3 dias | P1 |
| SOC2 / ISO (processo) | meses | P3 |

## Matriz esforço × impacto

```
Impacto alto
    │
    │  PostgreSQL+tenant   Login JWT      Filas IA
    │  S3 anexos           Portal admin   SSO
    │
    │  Billing             Webhooks
    └──────────────────────────────────► Esforço
```

## O que **não** mudar no core

- Fluxo Analista → envio IA → Gerente → Diretoria
- Versionamento `PagamentoAnaliseIA`
- Trilha WORM conceitual
- Pipeline heurística → XGBoost → GenAI

## Critérios de “pronto para 1º cliente pagante”

- [ ] Dois tenants em staging sem vazamento de dados
- [ ] Backup/restore testado
- [ ] DPA e Termos publicados
- [ ] Treinamento M1–M4 aplicado
- [ ] Suporte N1 com runbook
- [ ] Pentest básico ou checklist OWASP ASVS nível 1
