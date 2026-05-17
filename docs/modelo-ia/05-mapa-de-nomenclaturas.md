# 05 — Mapa de nomenclaturas e atuação do modelo

Guia rápido para ler telas, APIs e relatórios sem confundir **execução IA**, **pagamento analisado** e **perfil responsável**.

---

## Mapa mental (1 página)

```
                    GUARDIÃO DE PAGAMENTOS
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
    ANALISTA              GERENTE              DIRETORIA
   (monta/envia)      (2ª assinatura)      (monitora)
        │                     │                     │
        └──────────┬──────────┘                     │
                   ▼                                 │
            ENVIO / REANÁLISE                        │
                   ▼                                 │
     ┌─────────────────────────────┐                 │
     │  PIPELINE IA (por PAY)     │                 │
     │  Heurística → XGBoost →    │                 │
     │  Score → GenAI → WORM      │                 │
     └─────────────────────────────┘                 │
                   │                                 │
                   └─────────────────────────────────┘
                              │
                    KPIs · Gráficos · PAY-XXXX
```

---

## Glossário A–Z

| Termo | Significado |
|-------|-------------|
| **ALTO / MÉDIO / BAIXO** | Faixas de `risk_level` derivadas de `risk_score` |
| **Analise IA** | Registro em `pagamento_analises_ia` (uma versão) |
| **Catálogo MBA** | Remessa seed com todos os tipos de detecção |
| **Conformidade** | Classificação na Diretoria: sem fraude ML e sem alerta cadastral grave |
| **dados_conferem** | 1 = documento OK; 0 = divergência (OCR simulado) |
| **Dupla aprovação** | Analista ≠ Gerente; segregação de funções |
| **Execução IA** | Uma rodada completa do pipeline (pode incluir N pagamentos) |
| **Fraude ML** | `ml_fraude_detectada = 1` (score ≥ 55%) |
| **GenAI** | Camada de parecer em linguagem natural |
| **Heurística** | Regra fixa explicável (não aprendida no XGBoost) |
| **ml_score** | Probabilidade 0–1 do XGBoost |
| **Pagamento analisado** | Pagamento com pelo menos uma `PagamentoAnaliseIA` (última versão conta para gráfico “tipo”) |
| **PAY-XXXX** | Identificador de pagamento no histórico (ID interno) |
| **Pipeline** | Sequência heurística → ML → score → GenAI → persistência |
| **Remessa** | Lote de pagamentos enviado junto ao gerente |
| **Reanálise** | Nova versão IA sem novo envio do analista |
| **risk_score** | Score final 0–1 exibido no badge do gerente |
| **Trilha WORM** | Log imutável: Write Once, Read Many |
| **Velocity** | Múltiplos pagamentos ao mesmo beneficiário no mesmo dia |
| **Whitelist** | Fornecedores com `status = ativo` |
| **XGBoost** | Modelo de gradient boosting para classificação de fraude |

---

## Tabela perfil × responsabilidade × IA

| Perfil | Papel no processo | Dispara IA? | Vê resultado IA? |
|--------|-------------------|-------------|------------------|
| **Analista** | Monta remessa, anexa docs, envia | Sim (`envio_gerente`) | Não (antes do envio) |
| **Gerente** | Revisa, devolve, libera, reanalisa | Sim (`reanalise_gerente`) | Sim (principal usuário) |
| **Diretoria** | KPIs, auditoria, questionamentos | Não (somente consulta) | Sim (agregado + PAY) |
| **Sistema** | Seed, catálogo, jobs | Sim (`catalogo_mba`, etc.) | Via Diretoria |

---

## Nomenclatura dos gráficos (Diretoria)

### “Quem disparou a análise IA”

Conta **execuções** (`PagamentoAnaliseIA`), não número de analistas.

| Rótulo no gráfico | `triggered_by` agrupado | Cor na UI |
|-------------------|-------------------------|-----------|
| Analista | `envio_gerente`, `reenvio_gerente` | Ciano `#22d3ee` |
| Gerente | `reanalise_gerente` | Violeta `#a78bfa` |
| Sistema / IA | `catalogo_mba`, pipeline, outros | Âmbar `#fbbf24` |

### “Tipo de detecção”

Baseado na **última análise por pagamento** no período filtrado:

| Rótulo | Regra simplificada |
|--------|-------------------|
| Fraude ML | `ml_fraude_detectada = 1` |
| Conformidade | Sem fraude ML e sem PJ/PF não cad. |
| Risco médio | `risk_level = medio` (sem fraude ML) |
| PJ não cadastrado | `fornecedor_nao_cadastrado = 1` |
| PF não cadastrado | `pf_nao_cadastrado = 1` |

### KPIs do topo

| Card | Deve bater com |
|------|----------------|
| Pagamentos analisados (IA) | Soma do gráfico “Tipo de detecção” |
| Execuções IA | Soma do gráfico “Quem disparou” |
| Fraudes ML | Segmento vermelho do donut |

---

## Status da remessa

| Status | Significado |
|--------|-------------|
| `rascunho` | Analista montando |
| `aguardando_gerente` | IA concluída; fila do gerente |
| `devolvida_analista` | Gerente devolveu para correção |
| `liberada_banco` | Aprovada (histórico) |
| `rejeitada` | Rejeitada pelo gerente |

---

## Tipos de beneficiário e despesa

| Campo | Valores | Impacto na IA |
|-------|---------|----------------|
| `tipo_beneficiario` | `pj`, `pf` | Regras de cadastro |
| `tipo_despesa` | `fornecedor`, `salario`, `outros` | Anexos obrigatórios; regra salário atípico |
| `fornecedor_nao_cadastrado` | 0/1 | +risco; alerta gerente |
| `pf_nao_cadastrado` | 0/1 | +risco; parecer prefixado |

---

## Árvore de decisão do gerente (simplificada)

```
Pagamento na fila
       │
       ├─ ml_fraude_detectada = 1 ──► Revisar motivos ML + justificativa se liberar
       │
       ├─ fornecedor/pf não cadastrado ──► Devolver OU justificar
       │
       ├─ dados_conferem = 0 ──► Devolver (documento)
       │
       └─ risk_level = baixo ──► Liberar com checklist padrão
```

---

## Arquivos de código por nomenclatura

| Conceito | Arquivo principal |
|----------|-------------------|
| Treino | `ai_models/train_model.py` |
| Inferência ML | `backend/app/services/fraud_engine.py` |
| Heurísticas | `backend/app/services/heuristics.py` |
| Orquestração | `backend/app/services/ia_analise.py` |
| GenAI | `backend/app/services/genai_audit.py` |
| Métricas Diretoria | `backend/app/services/dashboard_ia_metrics.py` |
| Cenários demo | `backend/app/seed_cenarios_fraude.py` |
| Modelo ORM | `backend/app/models.py` |

---

## Referências cruzadas

- [Treinamento](01-treinamento-do-modelo.md)
- [Métricas](02-resultados-e-metricas.md)
- [Dicionário completo](03-dicionario-de-deteccoes.md)
- [Processo](04-processo-completo-ia.md)
- [Catálogo resumido](../06-catalogo-fraudes.md)
- [Fluxo IA](../03-fluxo-ia.md)
