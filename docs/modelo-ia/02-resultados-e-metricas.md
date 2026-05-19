# 02 — Resultados e métricas alcançados

## Métricas do último treino (artefato versionado)

Valores em `ai_models/model_metadata.json` (treino com dados **sintéticos**, seed 42):

| Métrica | Valor | Interpretação |
|---------|-------|----------------|
| **F1-score** | **0,845** | Equilíbrio entre precisão e recall na classe fraude |
| **AUC-ROC** | **0,939** | Boa separação entre classes no hold-out 20% |
| **Limiar operacional** | **0,55** | Probabilidade ≥ 55% → `ml_fraude_detectada = 1` |
| **Fonte do treino** | `synthetic` | Substituível por `kaggle` após `train_model.py` com Kaggle OK |
| **Algoritmo** | XGBoost | 150 árvores, profundidade 6 |

> Para reproduzir: execute `python ai_models/train_model.py` e compare o novo `model_metadata.json`.

## O que o modelo prediz vs. o que o sistema exibe

| Saída do modelo | Campo no banco / API | Uso na interface |
|-----------------|----------------------|------------------|
| Probabilidade 0–1 | `ml_score` | Barra / badge de risco no Gerente |
| Classe fraude (≥ 55%) | `ml_fraude_detectada` | Filtro “Somente fraudes ML” na Diretoria |
| Motivos textuais | `ml_motivos` | Lista no painel do gerente e histórico PAY |
| Score combinado | `risk_score` | 30% heurística + 50% ML + penalidade documento |
| Nível | `risk_level` | `baixo` \| `medio` \| `alto` |
| Parecer narrativo | `genai_parecer` | Texto de auditoria (GenAI ou template) |

### Fórmula do score final

```text
score_final = 0,30 × heuristic_score + 0,50 × ml_score + (0,25 se documento NÃO conferir)
risk_level = baixo (< 0,4) | medio (< 0,7) | alto (≥ 0,7)
```

Implementação: `backend/app/services/fraud_detector.py` → `score_final()`.

## Resultados na demonstração (seed ~6 meses)

Métricas típicas exibidas no **Dashboard Diretoria** (podem variar conforme filtros de período):

| Indicador | Ordem de grandeza | Observação |
|-----------|-------------------|------------|
| Pagamentos analisados (IA) | ~96 | Última análise por pagamento no período |
| Execuções IA | ~110 | Inclui reanálises e catálogo |
| Fraudes ML | ~24 | `ml_fraude_detectada = 1` |
| PJ não cadastrados | ~9 | Regra de negócio + alerta |
| PF não cadastradas | ~6 | Regra de negócio + alerta |
| Valor analisado (histórico) | ~R$ 5,8 mi | Soma dos pagamentos com IA no histórico |
| Trilha WORM | 140+ eventos | `audit_logs` imutáveis |

### Distribuição “Quem disparou a IA” (gráfico Diretoria)

| Perfil | % aproximado | Gatilho |
|--------|--------------|---------|
| Analista | ~67% | Envio / reenvio da remessa ao gerente |
| Sistema / IA | ~20% | Catálogo MBA, pipelines, reprocessamento |
| Gerente | ~13% | Botão “Nova análise IA” / remessa corrigida |

### Tipos de detecção (gráfico donut)

| Tipo | Significado |
|------|-------------|
| Fraude ML | `ml_fraude_detectada = 1` |
| Conformidade | Sem fraude ML e sem alerta cadastral crítico |
| Risco médio | `risk_level = medio` sem fraude ML |
| PJ não cadastrado | `fornecedor_nao_cadastrado = 1` |
| PF não cadastrado | `pf_nao_cadastrado = 1` |

## Remessa catálogo MBA

A remessa **“Catálogo MBA — Todos os tipos de detecção IA”** concentra **15+ cenários** documentados para banca e demo ao vivo. Resumo no [dicionário de detecções](03-dicionario-de-deteccoes.md).

## Limitações declaradas (governança)

- O modelo é **assistivo** — decisão humana (gerente) é obrigatória.
- Treino sintético/Kaggle **não substitui** dados reais da empresa sem validação.
- GenAI pode operar em **modo template** sem Ollama — parecer ainda é gerado.
- Netlify em modo demo usa `frontend/src/api/demoSnapshot.json`, exportado do mesmo seed (`python scripts/export_demo_snapshot.py`).

## Como validar após mudanças

```powershell
# 1. Treinar
.\backend\venv_mba\Scripts\python.exe ai_models\train_model.py

# 2. Subir API e conferir status
.\backend\venv_mba\Scripts\uvicorn.exe app.main:app --port 8000
curl http://127.0.0.1:8000/api/ml/status

# 3. Enviar remessa de teste e inspecionar pagamentos no Gerente
```
