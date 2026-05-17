# Plano comercial e operacional — Guardião de Pagamentos (SaaS B2B)

Guia para **disponibilizar o produto a vários clientes finais** com segurança, confiabilidade e escala — do modelo de negócio à infraestrutura, suporte e treinamento.

> Produto atual: MVP demonstrável (MBA Digital College). Este plano descreve a **evolução para SaaS multi-cliente** em produção.

## Índice

| Documento | Conteúdo |
|-----------|----------|
| [01 — Visão e proposta de valor](01-visao-e-proposta-de-valor.md) | Para quem vender, dores, diferenciais |
| [02 — Modelo de negócios e precificação](02-modelo-de-negocios-e-precificacao.md) | Planos, receitas, unit economics |
| [03 — Arquitetura multi-cliente e infraestrutura](03-arquitetura-multi-cliente-e-infraestrutura.md) | Tenants, banco, deploy, escala |
| [04 — Segurança, compliance e LGPD](04-seguranca-compliance-e-lgpd.md) | Dados financeiros, auditoria, contratos |
| [05 — Operação, suporte e treinamento](05-operacao-suporte-e-treinamento.md) | N1/N2, SLA, onboarding, capacitação |
| [06 — Roadmap produto → produção](06-roadmap-produto-para-producao.md) | O que falta no código atual |
| [07 — Implantação por cliente](07-implantacao-por-cliente.md) | Checklist de go-live (30–60 dias) |

## Resumo executivo (1 página)

| Dimensão | Recomendação inicial |
|----------|----------------------|
| **Modelo** | SaaS B2B por assinatura mensal + implantação |
| **Público** | PME/médias com 20–500 pagamentos/mês e dupla aprovação |
| **Infra** | Frontend CDN (Netlify/Vercel) + API container (Render/Railway/AWS) + PostgreSQL gerenciado |
| **Isolamento** | Um **tenant** por empresa (CNPJ); dados segregados por `tenant_id` |
| **Segurança** | HTTPS, RBAC, logs WORM, backup diário, LGPD (DPA + política) |
| **Suporte** | Horário comercial + portal de chamados; plano Enterprise com SLA |
| **Receita** | Starter R$ 1.990 · Professional R$ 4.990 · Enterprise sob consulta |

## Relação com a documentação técnica

| Recurso | Link |
|---------|------|
| Arquitetura atual | [02-arquitetura.md](../02-arquitetura.md) |
| Modelo de IA | [modelo-ia/](../modelo-ia/README.md) |
| Deploy frontend | [04-deploy-netlify.md](../04-deploy-netlify.md) |
