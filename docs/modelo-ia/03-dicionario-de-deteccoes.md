# 03 — Dicionário de detecções e funcionalidades do modelo

## Camadas do motor

| Camada | Módulo | Função |
|--------|--------|--------|
| **Heurísticas avançadas** | `heuristics.py` | Regras explicáveis (Benford, velocity, limites, cadastro) |
| **XGBoost anti-fraude** | `fraud_engine.py` | Classificação probabilística de fraude |
| **GenAI** | `genai_audit.py` | Parecer técnico de auditoria + conferência documental simulada |
| **Orquestração** | `ia_analise.py` | Executa pipeline e persiste resultados |
| **Auditoria WORM** | `audit_logs` | Cada ação registrada de forma imutável (Write Once, Read Many) |

---

## Códigos de cenário (catálogo MBA)

Cenários criados em `seed_cenarios_fraude.py` para demonstração e testes.

| Código | Tipo | O que detecta | `ml_fraude` típico |
|--------|------|---------------|-------------------|
| `ML_XGBOOST_FRAUDE` | ML | Probabilidade XGBoost ≥ 55% — classificação FRAUDE | 1 |
| `ML_VALOR_ELEVADO` | ML + regra | Valor > R$ 150.000 | 1 |
| `HEU_VALOR_LIMITE_200K` | Heurística | Valor > R$ 200.000 | 1 |
| `ML_RISCO_LIQUIDEZ_SALDO` | ML + regra | Pagamento > ~40% do saldo da conta | 1 |
| `HEU_BENFORD_ATIPICO` | Heurística | Padrão Benford / valor atípico | 0 |
| `REGRA_FORNECEDOR_NAO_CAD` | Regra negócio | PJ fora da whitelist de fornecedores | 0 |
| `REGRA_PF_NAO_CAD` | Regra negócio | CPF não cadastrado no RH | 0 |
| `ML_SALARIO_ATIPICO` | ML + regra | Salário acima do padrão / competência | 1 |
| `GENAI_DOCUMENTO_DIVERGENTE` | GenAI/OCR | Arquivo `fake` ou dados não conferem | 0 |
| `HEU_RAZAO_SOCIAL_INCOMPLETA` | Heurística | Razão social com menos de 5 caracteres | 0 |
| `HEU_VELOCITY_PRE_1` / `_2` | Heurística | 1º e 2º pagamento no mesmo dia (pré-catálogo) | 0 |
| `HEU_VELOCITY_3O_PAGAMENTO` | Heurística | 3º pagamento no dia + fracionamento | 1 |
| `HEU_FRACIONAMENTO_1` / `_2` | Heurística | Parcelas somando > R$ 100k para burlar alçada | 0 / 1 |
| `ML_HORARIO_RISCO` | Feature ML | Operação fora do horário comercial (22h–06h) | 0 |

---

## Regras heurísticas (runtime)

| Regra | Condição | Flag / efeito |
|-------|----------|----------------|
| Benford | Valor com padrão estatístico atípico | `Valor com padrão atípico (Benford/heurística)` — +0,15 no score heurístico |
| Velocity | 2+ pagamentos ao mesmo fornecedor no dia | Mensagem `Velocity: Nº pagamento...` — +0,25 |
| Fracionamento | Total do dia > R$ 100k com parcelas < R$ 50k | `Possível fracionamento para burlar alçada` |
| Limite operacional | Valor > R$ 200.000 | `Valor acima do limite operacional padrão` — +0,20 |
| Razão social | Nome < 5 caracteres | `Razão social incompleta` — +0,10 |
| PJ não cadastrado | `fornecedor_nao_cadastrado = 1` | `ALERTA: Fornecedor PJ NÃO CADASTRADO` — até +0,35 heurística |
| PF não cadastrado | `pf_nao_cadastrado = 1` | `ALERTA: PF com CPF NÃO CADASTRADO` — até +0,40 heurística |
| Salário | `tipo_despesa = salario` | Flag de competência; validação de holerite |

---

## Regras pós-modelo (explicabilidade)

Aplicadas em `analisar_fraude()` além da predição XGBoost:

| Condição | Motivo gerado |
|----------|----------------|
| `amount > 150_000` | Valor elevado acima do padrão operacional |
| `valor_sobre_saldo > 0,4` | Pagamento consome X% do saldo — risco de liquidez |
| `velocity_proxy > 0,25` | Velocity rule: múltiplos pagamentos no dia |
| `fornecedor_nao_cad` | Beneficiário PJ fora da whitelist |
| `pf_nao_cad` | CPF não cadastrado no RH |
| `tipo_despesa = salario` e valor > 50k | Salário atípico para competência |
| `ml_score ≥ 0,55` | `ml_fraude_detectada = 1` |

---

## GenAI — funcionalidades

| Função | Entrada | Saída |
|--------|---------|--------|
| `gerar_parecer_auditoria` | Nome, CNPJ/CPF, valor, risk, flags, conferência doc | Texto de parecer (Ollama ou template) |
| `conferir_dados_documento` | Nome arquivo, cadastro | `dados_conferem` 0 ou 1 |

**Simulação OCR:** arquivos com `fake` no nome → `dados_conferem = 0` → penalidade no score final (+0,25).

**Variáveis de ambiente (opcional):**

- `OLLAMA_URL`, `OLLAMA_MODEL` — LLM local
- `GROQ_API_KEY` — reservado para integração futura

---

## Campos persistidos por pagamento

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `heuristic_flags` | JSON/texto | Lista de flags heurísticas unidas por `;` |
| `ml_score` | float 0–1 | Probabilidade de fraude (XGBoost) |
| `ml_fraude_detectada` | 0/1 | 1 se `ml_score ≥ 0,55` |
| `ml_motivos` | JSON/texto | Motivos explicáveis (lista serializada) |
| `genai_parecer` | texto | Parecer de auditoria |
| `dados_conferem` | 0/1 | Cruzamento documental |
| `risk_score` | float 0–1 | Score final combinado |
| `risk_level` | string | `baixo`, `medio`, `alto` |
| `ia_analisado` | 0/1 | IA já executou neste pagamento |
| `ponto_atencao_diretoria` | 0/1 | Destaca no dashboard executivo |

---

## Histórico versionado (`PagamentoAnaliseIA`)

Cada execução da IA grava uma versão:

| Campo | Descrição |
|-------|-----------|
| `versao` | 1, 2, 3… por pagamento |
| `triggered_by` | Quem disparou a análise (ver mapa de nomenclaturas) |
| Demais campos | Cópia do estado IA naquele momento |

---

## Gatilhos de execução (`triggered_by`)

| Valor | Quem dispara | Quando |
|-------|--------------|--------|
| `envio_gerente` | Analista | `POST /remessas/{id}/enviar` |
| `reenvio_gerente` | Analista | Reenvio após correção |
| `reanalise_gerente` | Gerente | `POST /remessas/{id}/reanalisar-ia` |
| `catalogo_mba` | Sistema | Seed do catálogo de fraudes |
| `pipeline` / automático | Sistema | Jobs internos / reprocessamento |

---

## Endpoints da API relacionados à IA

| Método | Rota | Função |
|--------|------|--------|
| GET | `/api/ml/status` | Status do modelo (features, F1, limiar) |
| POST | `/api/remessas/{id}/enviar` | Dispara IA em lote |
| POST | `/api/remessas/{id}/reanalisar-ia` | Reanálise pelo gerente |
| GET | `/api/dashboard/kpis` | KPIs executivos |
| GET | `/api/dashboard/metricas-ia` | Gráficos por perfil / mês / tipo |
| GET | `/api/dashboard/deteccoes-ia` | Lista de detecções |
| GET | `/api/dashboard/historico-controle-ia` | Histórico PAY + eventos |
| GET | `/api/dashboard/auditoria` | Trilha WORM |

---

## Ações de auditoria (WORM)

Exemplos registrados em `audit_logs`:

| `action` | Significado |
|----------|-------------|
| `remessa_enviada` | Analista enviou ao gerente |
| `remessa_liberada` | Gerente aprovou |
| `remessa_devolvida` | Gerente devolveu ao analista |
| `catalogo_fraude_registrado` | Pagamento do catálogo MBA criado |
| `ia_reanalise` | Nova rodada de IA |

> Cada ação é registrada em trilha **WORM (Write Once, Read Many) imutável** — não há UPDATE/DELETE na trilha de compliance.
