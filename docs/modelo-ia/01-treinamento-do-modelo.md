# 01 — Treinamento do modelo XGBoost

## Objetivo

Treinar um classificador binário (**fraude / não fraude**) para apoiar a aprovação de pagamentos. O modelo **não libera nem bloqueia sozinho** — ele gera `ml_score`, `ml_fraude_detectada` e motivos explicáveis para o gerente decidir.

## Algoritmo e stack

| Item | Valor |
|------|--------|
| Algoritmo | **XGBoost** (`XGBClassifier`) |
| Biblioteca | `xgboost`, `scikit-learn`, `joblib` |
| Balanceamento | **SMOTE** (quando `imbalanced-learn` está instalado) |
| Saída | `ai_models/detector_fraudes_v1.pkl` + `ai_models/model_metadata.json` |

## Fontes de dados

O script `ai_models/train_model.py` tenta, nesta ordem:

1. **Kaggle** — dataset [Online Payments Fraud Detection](https://www.kaggle.com/datasets/rupakroy/online-payments-fraud-detection-dataset) via `kagglehub` (até 200.000 linhas).
2. **Sintético** — 60.000 registros gerados localmente se o Kaggle não estiver disponível.

### Features de entrada (6 variáveis)

| Feature | Significado no Guardião | Origem no treino |
|---------|-------------------------|------------------|
| `amount` | Valor do pagamento (R$) | Valor da transação |
| `balance_diff` | Diferença de saldo simulada | `oldbalanceOrg - newbalanceOrig` (Kaggle) ou proxy |
| `hour_risk` | Risco por horário da operação | Feature derivada / simulada |
| `velocity_proxy` | Múltiplos pagamentos ao mesmo beneficiário no dia | Heurística de velocity |
| `nao_cadastrado` | Beneficiário fora da whitelist (PJ/PF) | Flag 0/1 |
| `valor_sobre_saldo` | Pagamento ÷ saldo da conta | Risco de liquidez |

No **runtime** (`fraud_engine.extrair_features`), essas features são calculadas a partir do pagamento real, saldo da conta e histórico do dia.

## Hiperparâmetros

```text
n_estimators = 150
max_depth = 6
learning_rate = 0.08
scale_pos_weight = 2
random_state = 42
test_size = 0.2 (estratificado)
```

## Como executar o treinamento

```powershell
cd c:\trabalho_final_digital_college_mba
.\backend\venv_mba\Scripts\pip.exe install xgboost scikit-learn joblib imbalanced-learn pandas numpy kagglehub
.\backend\venv_mba\Scripts\python.exe ai_models\train_model.py
```

Saída esperada:

- Relatório `classification_report` no console
- `F1` e `AUC` no console e em `model_metadata.json`
- Arquivo `detector_fraudes_v1.pkl` atualizado

## Integração em produção

Após o treino, reinicie o backend. O motor carrega o modelo em memória na primeira inferência:

- **Caminho:** `backend/app/services/fraud_engine.py` → `MODEL_PATH = ai_models/detector_fraudes_v1.pkl`
- **Limiar de fraude:** `THRESHOLD_FRAUDE = 0.55` (55% de probabilidade)
- **Fallback:** se o `.pkl` não existir, usa score heurístico e registra aviso nos motivos

## Retreino recomendado

| Situação | Ação |
|----------|------|
| Novo segmento (varejo, saúde) | Retreinar com dados do segmento ou ajustar features |
| Muitos falsos positivos | Subir limiar (ex.: 0.60) em `fraud_engine.py` e validar |
| Muitos falsos negativos | Retreinar com mais exemplos de fraude; revisar SMOTE |
| Apresentação acadêmica | Manter sintético + catálogo MBA no seed |

## Relação com heurísticas e GenAI

O treinamento cobre **apenas a camada XGBoost**. As demais camadas não são “treinadas” neste script:

- **Heurísticas** — regras em `heuristics.py` (Benford, velocity, limites).
- **GenAI** — parecer em `genai_audit.py` (Ollama local ou template automático).

As três camadas são combinadas em `ia_analise.executar_analise_ia_pagamento`.
