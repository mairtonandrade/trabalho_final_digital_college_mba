# Guia de Utilização — Guardião de Pagamentos

**MBA Digital College · Módulo GenAI e Ciência de Dados**

---

## 1. Visão geral do sistema

O **Guardião de Pagamentos** é uma plataforma web de governança financeira que combina:

| Camada | Tecnologia | Função |
|--------|------------|--------|
| Processo | Dupla assinatura (Maker/Checker) | Analista cria → Gerente aprova |
| Dados | SQLite + contas bancárias | Saldo real, receitas e débitos |
| ML | XGBoost (`detector_fraudes_v1.pkl`) | Classificação de fraude em cada pagamento |
| GenAI | LLaMA (Ollama) | Parecer textual de auditoria |
| Auditoria | Logs WORM | Rastreabilidade para diretoria |

### Perfis de acesso (sem senha — demo acadêmica)

- **Analista Financeiro** — operação diária
- **Gerente Financeiro** — segunda assinatura e KYC
- **Diretoria** — monitoramento e compliance

---

## 2. Arquitetura do modelo de Machine Learning

### 2.1 O que foi treinado

- **Dataset base:** [Online Payments Fraud Detection (Kaggle)](https://www.kaggle.com/datasets/rupakroy/online-payments-fraud-detection-dataset)
- **Algoritmo:** XGBoost (classificação binária: fraude / não fraude)
- **Features utilizadas:**
  - `amount` — valor do pagamento
  - `balance_diff` — inconsistência de saldo (padrão do dataset)
  - `hour_risk` — horário atípico
  - `velocity_proxy` — repetição de pagamentos no mesmo dia
  - `nao_cadastrado` — beneficiário fora da whitelist/RH
  - `valor_sobre_saldo` — percentual do saldo da conta consumido

### 2.2 Como o modelo atua em produção

> Documentação completa: [`docs/modelo-ia/08-vinculo-treinamento-e-runtime.md`](docs/modelo-ia/08-vinculo-treinamento-e-runtime.md)

1. Ao **enviar a remessa ao gerente** (ou na **reanálise** pelo gerente), a IA roda **em lote** para cada pagamento — não ao adicionar cada linha.
2. O backend monta o vetor de 6 features e o XGBoost retorna **probabilidade de fraude** (`ml_score`).
3. Se `ml_score ≥ 55%` → `ml_fraude_detectada = 1` e motivos explicativos são gravados.
4. O score ML compõe o **risco final** (50% ML + 30% heurística + penalidade documental).
5. A **GenAI** gera o parecer com prefixo de alerta ML quando aplicável.
6. O **gerente** revisa e pode liberar (com **justificativa obrigatória** se fraude ML, não cadastrado ou alto risco) ou devolver ao analista.

### 2.3 Retreinar o modelo

```powershell
cd c:\trabalho_final_digital_college_mba
.\backend\venv_mba\Scripts\activate
pip install kagglehub   # opcional, para dataset real
python ai_models/train_model.py
```

Arquivos gerados:
- `ai_models/detector_fraudes_v1.pkl`
- `ai_models/model_metadata.json` (F1, AUC, features, limiar)

### 2.4 API de validação (teste)

```http
GET  /api/ml/status
POST /api/ml/validar
Body: { "valor": 200000, "saldo_conta": 500000, "fornecedor_nao_cadastrado": true }
```

---

## 3. Guia por perfil

### 3.1 Analista Financeiro

#### Responsabilidades
- Manter saldos das contas (receitas)
- Cadastrar fornecedores e solicitar pagamentos
- Montar remessas vinculadas a uma conta bancária
- Anexar documentação fiscal/contábil

#### Passo a passo
1. Acesse **Entrar como Analista**.
2. Em **Contas bancárias**, confira saldos ou credite receita.
3. Clique **Usar na remessa** na conta desejada.
4. **Nova remessa** → preencha pagamentos:
   - **PJ:** fornecedor da whitelist (ou pendente, máx. R$ 10.000)
   - **PF:** colaborador RH ou CPF manual (não cadastrado, máx. R$ 10.000)
   - **Salário:** PF + tipo Salário + competência `MM/AAAA` + holerite
5. **Enviar à gerência** — dispara a análise IA em lote para todos os pagamentos da remessa.
6. Após o envio, o gerente verá scores ML, motivos e parecer GenAI (o analista não revisa IA antes do envio).

#### O que o ML valida para você
- Valor atípico vs. saldo da conta
- Múltiplos pagamentos no mesmo dia (velocity)
- Beneficiário não cadastrado
- Padrões aprendidos do dataset de fraudes

#### Cenários para demonstração na banca
| Ação | Resultado esperado |
|------|-------------------|
| Pagamento R$ 250.000 | ML tende a marcar fraude |
| CPF não cadastrado + R$ 15.000 | Bloqueio por limite ou alerta |
| Arquivo `nota_fake.pdf` | GenAI marca divergência documental |
| Remessa com fraude ML | Gerente vê alerta; liberação exige justificativa |

---

### 3.2 Gerente Financeiro

#### Responsabilidades
- Aprovar/rejeitar **fornecedores** e **colaboradores** (KYC/RH)
- Segunda assinatura em **remessas**
- Justificar exceções (fraude ML, não cadastrado, alto risco)

#### Passo a passo
1. Acesse **Entrar como Gerente**.
2. Revise **cadastros pendentes** e consulte **histórico** de aprovações.
3. Em **Remessas**, leia:
   - Tag **FRAUDE ML** e motivos listados
   - Parecer LLaMA
   - Saldo vs. total da remessa
4. Preencha **justificativa** se houver alerta ML ou beneficiário não cadastrado.
5. **Liberar no banco** → debita saldo e gera e-mail de auditoria.

#### Papel do ML neste perfil
O gerente não re-treina o modelo; **interpreta** o score e os motivos. A decisão humana fica registrada na trilha WORM junto com o parecer da IA.

---

### 3.3 Diretoria

#### Responsabilidades
- Monitorar KPIs e alertas consolidados
- Acompanhar pagamentos a PF não cadastrados e fraudes detectadas
- Auditoria pós-fato (compliance)

#### Passo a passo
1. Acesse **Entrar como Diretoria**.
2. Analise **saldo total**, **fraudes IA**, **PJ/PF não cadastrados**.
3. Revise tabelas de alertas e clique para ver **parecer LLaMA**.
4. Consulte **trilha de auditoria** (ações por perfil e timestamps).

#### Papel do ML neste perfil
Visão agregada: quantas fraudes o modelo impediu de seguir silenciosamente no fluxo, e quais exceções o gerente liberou com justificativa.

---

## 4. Regras de negócio complementares ao ML

| Regra | Descrição |
|-------|-----------|
| Saldo | Remessa não envia sem saldo suficiente na conta |
| PJ não cadastrado | Máx. R$ 10.000 por pagamento |
| PF não cadastrado | Máx. R$ 10.000; alerta diretoria |
| Salário | Competência obrigatória (MM/AAAA) |
| Zero-Trust | Gerente justifica alto risco / fraude ML / não cadastrado |
| MIME | Apenas PDF, PNG, JPG nos anexos |

---

## 5. Papel da GenAI (LLaMA) vs. ML

| | Machine Learning (XGBoost) | GenAI (LLaMA) |
|---|---------------------------|----------------|
| **Entrada** | Números (features) | Texto + contexto do pagamento |
| **Saída** | Score + fraude sim/não | Parecer em português |
| **Força** | Padrões estatísticos em massa | Explicação para humanos |
| **Quando** | Todo pagamento | Após análise ML + regras |

---

## 6. Execução do sistema

### Backend
```powershell
cd backend
.\venv_mba\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### Frontend
```powershell
cd frontend
npm run dev
```

### Ollama (opcional — pareceres GenAI)
```powershell
ollama run llama3:8b
```

### Acesso
- App: http://localhost:5173
- Guia integrado: http://localhost:5173/guia
- API docs: http://localhost:5173/api/docs (via proxy) ou http://127.0.0.1:8000/docs

---

## 7. Estrutura do repositório

```
trabalho_final_digital_college_mba/
├── ai_models/           # Treinamento e modelo .pkl
├── backend/             # FastAPI + SQLite
├── frontend/            # React + Vite
├── GUIA_UTILIZACAO.md   # Este documento
└── README.md
```

---

## 8. Checklist para apresentação do TCC/MBA

- [ ] Modelo treinado (`detector_fraudes_v1.pkl` presente)
- [ ] Demo: pagamento normal (verde/baixo risco)
- [ ] Demo: pagamento com fraude ML (vermelho + bloqueio envio)
- [ ] Demo: gerente justifica e libera
- [ ] Demo: diretoria vê KPIs e alertas
- [ ] Explicar diferença ML (score) vs. GenAI (parecer)

---

*Documento gerado para o projeto Guardião de Pagamentos — Digital College MBA.*
