# 05 — Operação, suporte e treinamento

## Estrutura operacional mínima (fase 1)

| Função | Responsabilidade | Dedicação inicial |
|--------|------------------|-------------------|
| **Produto / founder** | Vendas, demo, roadmap | Parcial |
| **Tech lead** | API, infra, incidentes P1 | Parcial → full |
| **CS / onboarding** | Implantação, treinamento | Por projeto |
| **Suporte N1** | Dúvidas de uso, reset senha | Terceirizável |
| **Compliance advisor** | DPA, políticas (consultor) | Pontual |

## Suporte ao cliente

### Canais

| Canal | Plano | SLA 1ª resposta |
|-------|-------|-----------------|
| E-mail `suporte@` | Starter | 24h úteis |
| E-mail + chat | Professional | 8h úteis |
| E-mail + chat + telefone | Enterprise | 4h; P1 em 1h |

### Classificação de incidentes

| Prioridade | Exemplo | Meta resolução |
|------------|---------|----------------|
| **P1** | Sistema fora, vazamento suspeito | 4h |
| **P2** | IA não roda no envio, erro 500 frequente | 1 dia útil |
| **P3** | Dúvida de tela, relatório incorreto | 3 dias úteis |
| **P4** | Melhoria, cosmético | Backlog |

### Base de conhecimento

Publicar artigos (Notion / GitBook):

1. Como criar remessa e enviar ao gerente
2. O que significa score ML e fraude detectada
3. Como devolver remessa ao analista
4. Filtros da Diretoria (período, fraudes ML)
5. Exportação e auditoria WORM
6. FAQ LGPD e segurança

## Gestão de clientes (CRM + CS)

| Etapa | Ferramenta sugerida | Ação |
|-------|---------------------|------|
| Lead | Planilha / HubSpot free | Demo agendada |
| Piloto | Notion checklist | Acompanhamento semanal |
| Ativo | Portal admin interno | Tenant, plano, usuários |
| Renovação | QBR trimestral | Métricas de valor |
| Churn | Entrevista exit | Aprender causa |

### Portal admin (a construir)

- Criar tenant, CNPJ, plano
- Usuários e papéis
- Uso: pagamentos/mês vs. limite
- Suspender por inadimplência
- Logs de acesso (Enterprise)

## Treinamento

### Programa padrão (incluso na implantação)

| Módulo | Público | Duração | Formato |
|--------|---------|---------|---------|
| **M1 — Visão geral** | Todos | 1h | Remoto gravado + live |
| **M2 — Analista** | Tesouraria AP | 2h | Hands-on: remessa + anexos |
| **M3 — Gerente** | Aprovadores | 2h | ML, GenAI, devolução, justificativa |
| **M4 — Diretoria** | CFO / controller | 1h | KPIs, filtros, auditoria |
| **M5 — Admin** | TI / compliance | 1h | Usuários, export, LGPD |

### Materiais entregues

- PDF guia por perfil (base: `GUIA_UTILIZACAO.md` do repo)
- Vídeos curtos (5–10 min) por fluxo
- Ambiente **sandbox** (tenant demo) por 14 dias pós-treino
- Certificado de conclusão (opcional — marketing)

### Treinamento contínuo

- Release notes por versão (e-mail mensal)
- Webinar trimestral “Novidades IA”
- Treinamento de recrutas: pacote R$ 800/sessão (receita extra)

## Operação do dia a dia (runbook)

| Rotina | Frequência | Responsável |
|--------|------------|-------------|
| Verificar uptime e alertas | Diário | Tech |
| Revisar fila IA travada | Diário | Tech |
| Backup OK? | Diário (automático + spot check) | Tech |
| Tickets suporte abertos | Diário | N1 |
| Uso vs. limite por tenant | Semanal | CS |
| Patch segurança dependências | Semanal | Tech |
| Revisão métricas produto | Mensal | Produto |
| Teste restore backup | Trimestral | Tech |
| QBR clientes Pro/Enterprise | Trimestral | CS + founder |

## Comunicação de incidentes

Template para P1:

1. Reconhecer em até X min (SLA)
2. Impacto e workaround
3. Causa raiz (post-mortem em 5 dias úteis)
4. Ações preventivas

Status page pública (opcional): Instatus, Better Uptime.

## Indicadores operacionais (internos)

| KPI | Meta |
|-----|------|
| Uptime mensal | > 99% |
| Tickets P1 no SLA | 100% |
| NPS pós-onboarding | > 40 |
| Time-to-go-live | < 30 dias |
| Churn por “não usou” | < 50% dos churns |
