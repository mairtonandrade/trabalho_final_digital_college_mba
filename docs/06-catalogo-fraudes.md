# 06 — Catálogo de detecções de fraude

Remessa dedicada no seed: **"Catálogo MBA — Todos os tipos de detecção IA"** (`aguardando_gerente`).

## Cenários registrados

| Código | Tipo | O que detecta |
|--------|------|----------------|
| `ML_XGBOOST_FRAUDE` | ML | XGBoost ≥ 55% — classificação FRAUDE |
| `ML_VALOR_ELEVADO` | ML | Valor > R$ 150.000 |
| `HEU_VALOR_LIMITE_200K` | Heurística | Valor > R$ 200.000 |
| `ML_RISCO_LIQUIDEZ_SALDO` | ML | Pagamento > 40% do saldo da conta |
| `HEU_BENFORD_ATIPICO` | Heurística | Padrão Benford / valor atípico |
| `REGRA_FORNECEDOR_NAO_CAD` | Regra | PJ fora da whitelist |
| `REGRA_PF_NAO_CAD` | Regra | CPF não cadastrado no RH |
| `ML_SALARIO_ATIPICO` | ML | Salário acima do padrão |
| `GENAI_DOCUMENTO_DIVERGENTE` | GenAI/OCR | Arquivo `fake` / dados não conferem |
| `HEU_RAZAO_SOCIAL_INCOMPLETA` | Heurística | Razão social incompleta |
| `HEU_VELOCITY_*` | Heurística | Múltiplos pagamentos no mesmo dia |
| `HEU_FRACIONAMENTO_*` | Heurística | Fracionamento > R$ 100k |
| `ML_HORARIO_RISCO` | ML feature | Horário fora do comercial |

Cada pagamento possui: `heuristic_flags`, `ml_motivos`, `genai_parecer`, `PagamentoAnaliseIA` e log `catalogo_fraude_registrado`.

## Recriar localmente

```powershell
cd backend
.\venv_mba\Scripts\python.exe scripts\reseed_demo.py
```
