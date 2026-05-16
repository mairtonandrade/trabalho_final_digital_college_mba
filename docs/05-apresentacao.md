# 05 — Roteiro de apresentação

## Credenciais

Não há login — selecione o perfil na home.

## 1. Analista (5 min)

1. Abra `/analista`
2. Mostre cadastros ativos (colaboradores/fornecedores)
3. Crie remessa ou use **devolvida** do seed
4. Adicione 2–3 pagamentos com anexos
5. **Enviar para IA** — destaque o loading e que a IA roda em lote
6. Explique que o analista **não** vê score (evita viés)

## 2. Gerente (5 min)

1. Abra `/gerente`
2. Remessa **“aguardando gerente”** do seed (3 pagamentos, 1 com alerta ML)
3. Expanda ML + GenAI + histórico PAY
4. Marque revisão documental
5. Demonstre **devolver** ou **liberar** com justificativa se alto risco
6. **Reanalisar IA** após correção

## 3. Diretoria (3 min)

1. `/diretoria` — KPIs (25 remessas, valores aprovados)
2. Aba detecções IA — fraudes e pontos de atenção
3. Trilha de auditoria — ações analista/gerente/sistema

## 4. Fechamento técnico (2 min)

- XGBoost treinado em `ai_models/`
- Histórico versionado em `pagamento_analises_ia`
- Seed simula **6 meses** de operação

## Dados pré-carregados

| Métrica | ~Valor |
|---------|--------|
| Remessas | 25+ |
| Pagamentos | 90+ |
| Análises IA | 70+ |
| Logs auditoria | 140+ |
