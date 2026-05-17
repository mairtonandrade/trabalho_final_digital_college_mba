# 02 — Modelo de negócios e precificação

## Modelo de receita

| Fonte | Descrição | Recorrência |
|-------|-----------|-------------|
| **Assinatura SaaS** | Acesso à plataforma por tenant | Mensal/anual |
| **Implantação (setup)** | Configuração inicial, cadastros, treinamento | Uma vez |
| **Treinamento extra** | Workshops por perfil ou turno | Sob demanda |
| **Retreino ML** | Modelo XGBoost por segmento/setor | Anual ou projeto |
| **Consultoria compliance** | Adequação de processos e políticas | Projeto |
| **API / integração ERP** | Conector customizado | Mensal + setup |

## Planos sugeridos (referência Brasil)

| Plano | Público | Preço/mês* | Limites | Inclui |
|-------|---------|------------|---------|--------|
| **Starter** | PME | R$ 1.990 | até 50 pagamentos/mês, 2 perfis ativos | IA básica, auditoria 90 dias, e-mail suporte |
| **Professional** | Médio porte | R$ 4.990 | até 500 pagamentos/mês, 3 perfis | GenAI, API leitura, suporte prioritário, backup 1 ano |
| **Enterprise** | Grande / multi-CNPJ | Sob consulta | Volume ilimitado negociado | SSO, SLA 99,5%, ambiente dedicado opcional, DPA customizado |

\* Valores ilustrativos — ajustar por CAC, custo de infra e concorrência local.

### Desconto anual

- Pagamento anual: **2 meses grátis** (≈17% desconto) — melhora fluxo de caixa e reduz churn.

## Unit economics (planejamento)

| Métrica | Meta inicial | Observação |
|---------|--------------|------------|
| CAC | < 3× MRR do plano | Demo + piloto reduzem CAC |
| Churn mensal | < 3% | Suporte e onboarding fortes |
| LTV | > 18 meses | Expansão para Professional |
| Margem bruta | > 70% | SaaS padrão após escala |
| Payback CAC | < 12 meses | |

## Custos operacionais mensais (estimativa MVP produção)

| Item | Faixa (R$/mês) |
|------|----------------|
| PostgreSQL gerenciado (3–5 tenants pequenos) | 150–400 |
| API + workers (Render/Railway) | 100–300 |
| Frontend CDN (Netlify) | 0–100 |
| Object storage (anexos NF) | 50–200 |
| Monitoramento (Sentry, uptime) | 50–150 |
| GenAI (API cloud ou Ollama dedicado) | 100–500 |
| **Total infra inicial** | **~500–1.500** |

Com 3 clientes Professional (≈R$ 15k MRR), margem operacional positiva antes de salários.

## Contrato comercial (itens mínimos)

- Objeto: licença de uso SaaS não exclusiva
- SLA e suporte por plano
- Limite de usuários e volume de pagamentos
- Confidencialidade e LGPD (DPA anexo)
- Propriedade dos dados do cliente
- Rescisão, exportação de dados e prazo de retenção pós-cancelamento
- Reajuste anual (IPCA ou índice acordado)

## Política de piloto

| Item | Regra |
|------|--------|
| Duração | 30 dias |
| Volume | até 100 pagamentos |
| Preço | gratuito ou R$ 990 simbólico |
| Conversão | desconto 20% no 1º ano se assinar em 15 dias após piloto |
| Dados | ambiente isolado; exportação ao fim se não converter |

## Métricas de sucesso do cliente (para QBR)

- % pagamentos com IA analisada
- Nº fraudes ML detectadas vs. liberadas com justificativa
- Tempo médio analista → liberação
- Nº devoluções por documento inválido
- Uso do painel Diretoria (logins/mês)
