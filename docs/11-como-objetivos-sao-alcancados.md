# 11 — Como os objetivos do projeto são alcançados

Rastreabilidade entre **problema de negócio**, **objetivo**, **funcionalidade**, **implementação** e **como validar** (demo ou tela).

---

## Problema e visão

| Problema | Objetivo do Guardião | Indicador de sucesso na demo |
|----------|----------------------|------------------------------|
| Fraude e beneficiário indevido | Detectar antes da liberação | `ml_fraude_detectada`, catálogo MBA |
| Falta de trilha única | Auditoria WORM + histórico IA versionado | `audit_logs`, `PagamentoAnaliseIA` |
| Gerente sobrecarregado | ML + GenAI + motivos explicáveis | Tela gerente com badge e parecer |
| Diretoria sem visão | KPIs e gráficos coerentes | Dashboard executivo |
| IA “caixa-preta” | Copiloto: humano decide | Justificativa obrigatória em alto risco |

---

## Matriz objetivo → entrega

### O1 — Dupla aprovação (segregação de funções)

| Objetivo | Funcionalidade | Backend | Frontend | Documentação |
|----------|----------------|---------|----------|----------------|
| Analista ≠ quem libera | Perfis separados + fluxo remessa | `remessas.py` status | `Home.tsx`, `Analista.tsx`, `Gerente.tsx` | [GUIA](../GUIA_UTILIZACAO.md) §3 |
| Rastro de quem fez o quê | `audit_logs`, `user_role` | `audit_service.py` | Histórico IA | [modelo-ia/04](modelo-ia/04-processo-completo-ia.md) |

**Como validar:** analista envia → gerente libera ou devolve; logs na Diretoria (Auditoria).

---

### O2 — IA no momento certo (eficiência + consistência)

| Objetivo | Funcionalidade | Backend | Frontend | Documentação |
|----------|----------------|---------|----------|----------------|
| Não travar digitação | IA só no envio | `POST .../enviar` → `analisar_remessa_completa` | Sem IA ao adicionar pagamento | [03-fluxo-ia](03-fluxo-ia.md) |
| Reanálise após correção | Nova versão IA | `reanalise_gerente` | Botão gerente | [modelo-ia/05](modelo-ia/05-mapa-de-nomenclaturas.md) |

**Como validar:** adicionar 3 pagamentos rápido; IA só após “Enviar ao gerente”.

---

### O3 — Detecção de fraude e risco (ML + regras)

| Objetivo | Funcionalidade | Backend | Frontend | Documentação |
|----------|----------------|---------|----------|----------------|
| Score probabilístico | XGBoost | `fraud_engine.py` + `.pkl` | `ml_score`, `RiskBadge` | [modelo-ia/08](modelo-ia/08-vinculo-treinamento-e-runtime.md) |
| Explicabilidade | Motivos + heurísticas | `ml_motivos`, `heuristic_flags` | Lista no gerente | [modelo-ia/03](modelo-ia/03-dicionario-de-deteccoes.md) |
| Cenários didáticos | Catálogo MBA | `seed_cenarios_fraude.py` | Remessa catálogo | [06-catalogo-fraudes](06-catalogo-fraudes.md) |

**Como validar:** remessa “Catálogo MBA”; filtro “Somente fraudes ML” na Diretoria.

---

### O4 — Revisão documental e parecer (GenAI)

| Objetivo | Funcionalidade | Backend | Frontend | Documentação |
|----------|----------------|---------|----------|----------------|
| Conferência anexo | OCR simulado | `genai_audit.conferir_dados_documento` | Upload analista | [modelo-ia/03](modelo-ia/03-dicionario-de-deteccoes.md) |
| Parecer para gerente | Template ou Ollama | `gerar_parecer_auditoria` | Textarea parecer | [GUIA](../GUIA_UTILIZACAO.md) |
| Penalidade se não confere | +0,25 no `score_final` | `fraud_detector.score_final` | `dados_conferem` | [modelo-ia/08](modelo-ia/08-vinculo-treinamento-e-runtime.md) §5 |

**Como validar:** anexo com `fake` no nome → parecer e risco elevados.

---

### O5 — Governança executiva (Diretoria)

| Objetivo | Funcionalidade | Backend | Frontend | Documentação |
|----------|----------------|---------|----------|----------------|
| KPIs alinhados aos gráficos | Mesma base de dados | `dashboard_ia_metrics.py` | `IndicadoresExecutivos`, `PainelGraficosIA` | [07-mapa-dados-demo](07-mapa-dados-demo.md) |
| Histórico por pagamento | PAY + versões | `historico-controle-ia` | `HistoricoControleIA` | [modelo-ia/04](modelo-ia/04-processo-completo-ia.md) |
| Filtro por período | De/Até | `filtrosMovimentacao` (FE+BE) | `FiltrosMovimentacao` | [10-frontend](10-construcao-frontend.md) |

**Como validar:** alterar período → KPIs e gráficos mudam juntos.

---

### O6 — Operacionalização (contas, cadastros, limites)

| Objetivo | Funcionalidade | Backend | Frontend | Documentação |
|----------|----------------|---------|----------|----------------|
| Saldo real | Contas + débito na liberação | `conta_service.py` | `ContasPanel` | [GUIA](../GUIA_UTILIZACAO.md) |
| PJ/PF não cadastrado | Flags + limites | `models.LIMITE_*` | Alertas laranja | [06-catalogo-fraudes](06-catalogo-fraudes.md) |
| KYC fornecedor | Aprovação gerente | `fornecedores.py` | Módulo cadastros gerente | [09-backend](09-construcao-backend.md) |

---

## Entregas MBA (checklist acadêmico)

| Entrega declarada | Evidência no repositório |
|-------------------|-------------------------|
| Frontend React | `frontend/`, deploy Netlify |
| API FastAPI | `backend/`, Swagger `/docs` |
| XGBoost treinável | `ai_models/train_model.py`, `.pkl` |
| GenAI | `genai_audit.py`, Ollama opcional |
| Histórico 6 meses | `seed_demo_historico.py` |
| Documentação | `docs/`, `GUIA`, `modelo-ia/` |

---

## O que o sistema **não** promete (transparência)

- Substituir ERP ou internet banking
- Pagamento automático sem humano
- 100% de detecção de fraude
- Multi-empresa em produção (MVP single-tenant; ver [comercial-saas](comercial-saas/06-roadmap-produto-para-producao.md))

---

## Fluxo “objetivo alcançado” em uma remessa feliz

```text
1. Analista monta remessa (objetivo: operação eficiente)
2. Envia → IA analisa todos os pagamentos (objetivo: risco antes do gerente)
3. Gerente vê ML + GenAI, libera com ou sem justificativa (objetivo: dupla aprovação)
4. Saldo debitado + e-mail auditoria + WORM (objetivo: trilha)
5. Diretoria vê KPIs e histórico (objetivo: governança)
```

Cada passo mapeado em [04-processo-completo IA](modelo-ia/04-processo-completo-ia.md) e nas telas [01–05 em assets](README.md#telas-do-sistema).
