# Documentação do modelo de IA — Guardião de Pagamentos

Pasta dedicada ao **treinamento**, **resultados**, **dicionário de detecções** e **mapa operacional** do motor anti-fraude (heurísticas + XGBoost + GenAI).

> **Escopo:** governança de pagamentos corporativos — MBA Digital College (Ciência de Dados & GenAI).

## Índice

| Documento | Conteúdo |
|-----------|----------|
| [**08 — Vínculo treino → runtime**](08-vinculo-treinamento-e-runtime.md) | **Base de treino, features, `.pkl` e atuação no sistema (documento principal de rastreio)** |
| [01 — Treinamento do modelo](01-treinamento-do-modelo.md) | Dataset, features, hiperparâmetros, como retreinar |
| [02 — Resultados e métricas](02-resultados-e-metricas.md) | F1, AUC, limiar, métricas da demo |
| [03 — Dicionário de detecções](03-dicionario-de-deteccoes.md) | Todos os códigos, campos e tipos de alerta |
| [04 — Processo completo](04-processo-completo-ia.md) | Pipeline ponta a ponta no dia a dia |
| [05 — Mapa de nomenclaturas](05-mapa-de-nomenclaturas.md) | Glossário, tabelas, quem dispara o quê |

## Artefatos no repositório

| Arquivo | Descrição |
|---------|-----------|
| `ai_models/train_model.py` | Script de treinamento |
| `ai_models/detector_fraudes_v1.pkl` | Modelo serializado (joblib) |
| `ai_models/model_metadata.json` | Métricas e features do último treino |
| `backend/app/services/fraud_engine.py` | Inferência XGBoost em produção |
| `backend/app/services/heuristics.py` | Regras heurísticas |
| `backend/app/services/ia_analise.py` | Orquestração ML + GenAI |
| `backend/app/seed_cenarios_fraude.py` | Catálogo de cenários de demonstração |

## Diagrama do fluxo

![Fluxo completo](../assets/06-fluxo-completo.svg)

## Comandos rápidos

```powershell
# Treinar / retreinar o modelo
.\backend\venv_mba\Scripts\python.exe ai_models\train_model.py

# Status do modelo via API (com backend rodando)
curl http://127.0.0.1:8000/api/ml/status

# Recriar catálogo de fraudes na base demo
cd backend
.\venv_mba\Scripts\python.exe scripts\reseed_demo.py
```
