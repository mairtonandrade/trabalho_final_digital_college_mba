# Planejamento Estratégico: Sistema de Aprovação de Pagamentos e Detecção de Fraudes com IA
**Autor:** Especialista Sênior em Ciência de Dados e Arquitetura Full Stack (> 30 anos de experiência)
**Objetivo:** Trabalho Final MBA - Digital College (Módulo 4 - GenAI)

---

## 1. Visão Executiva e Arquitetural

Com base na minha vasta experiência desenvolvendo sistemas críticos e conduzindo auditorias financeiras (SOX, ISO 27001), afirmo que um sistema financeiro de excelência exige **processo rigoroso, controles compensatórios e velocidade**. A complexidade não deve estar na burocracia, mas na inteligência profunda contida na validação e proteção contra anomalias.

### Arquitetura Tecnológica Proposta (Foco em Performance e MVP)
Para garantir uma entrega de padrão *enterprise*, extrema velocidade e de fácil demonstração (deploy via Netlify):
- **Frontend (Web App & Dashboard):** React.js (Next.js ou Vite) + Tailwind CSS. Interface executiva, limpa e responsiva.
- **Armazenamento de Dados (Estratégia para o Hackathon/MVP):** 
  - Como o objetivo principal é a *apresentação* e a *validação do modelo de IA*, **não vamos subir um banco de dados relacional complexo (como PostgreSQL)** agora. Isso deixaria o projeto lento para rodar na hora da banca e adicionaria complexidade desnecessária de infraestrutura.
  - **Estratégia adotada: `JSON Server` ou `SQLite` + `LocalStorage` (Frontend).**
    - Para os *cadastros estáticos e fluxo de telas (Mock)*, usaremos o `LocalStorage` do navegador ou arquivos JSON locais lidos pelo backend. Isso garante que o frontend responda em **milissegundos**, sem latência de rede para buscar dados em nuvem.
    - O banco de dados só será simulado para o que for estritamente necessário para o cruzamento da IA. 
    - *Vantagem:* Você clica e a tela carrega instantaneamente na apresentação. Não há risco do banco "cair" ou demorar a responder.
- **Backend (API):** Python com **FastAPI**. Ideal para integrar ML e GenAI nativamente de forma assíncrona. Ele lerá os arquivos locais (JSON/SQLite) de forma instantânea.
- **Camada de IA (Híbrida):**
  - *Detecção de Anomalias (Transacional):* Machine Learning (XGBoost/Random Forest) validando "Velocity Rules" e detecção de padrões anômalos.
  - *Auditoria e Inteligência Generativa:* GenAI (LLaMA) para ler relatórios via OCR, cruzar dados fiscais e redigir o parecer executivo para a Diretoria.

---

## 2. Modelagem do Processo (Workflow Financeiro Anti-Fraude)

O coração do aplicativo é a **Governança de Acessos (Segregação de Funções - Maker/Checker)** aliada a verificações heurísticas antes mesmo da IA atuar.

### *Ajuste para a Apresentação (UX Flow):*
Para que a sua apresentação seja dinâmica e fluida, não exigiremos digitação de senhas complexas ao vivo. A tela inicial será um **"Fast-Switch Persona"** (Seleção de Perfil), contendo 3 grandes botões:
1. `[ Entrar como Analista ]`
2. `[ Entrar como Gerente Financeiro ]`
3. `[ Entrar como Diretoria (Dashboard) ]`
Isso demonstra o controle de acesso Baseado em Papéis (RBAC - Role-Based Access Control) sem gastar tempo da banca com digitação de credenciais.

### A. Cadastro de Fornecedores (KYC - Know Your Supplier)
1. **Analista:** Tenta inserir um fornecedor na remessa. Se for novo, inicia o cadastro (CNPJ, Razão Social, Banco, Agência, Conta).
2. **Sistema (Regras Duras):** Valida a máscara do CNPJ e cruza a formatação. (Em um cenário real, bateria com a Receita Federal).
3. **Gerente Financeiro:** Aprova o cadastro para garantir a lisura da conta destino. Só após o "De Acordo", o fornecedor vai para a *Whitelist*.

### B. Remessa de Pagamentos (Aprovação Dupla + IA)
1. **Analista (Maker):** Monta a remessa com fornecedor da *Whitelist*, insere o valor e anexa a Nota Fiscal/Fatura (`.pdf` ou `.png`).
2. **Motor Híbrido Anti-Fraude (Background):**
   - **Regras Heurísticas:** O sistema avalia se o valor foge da Lei de Benford (distribuição natural de dígitos) e checa as *Velocity Rules* (ex: o mesmo fornecedor recebendo 3 pagamentos fracionados no mesmo dia para burlar limites de alçada).
   - **Machine Learning:** Calcula o *Risk Score* (ex: 88% de suspeita de fraude) com base no histórico.
   - **GenAI (LLaMA):** Faz OCR do anexo e cruza se a "Razão Social" e "Valor" do PDF batem com os dados digitados pelo Analista.
3. **Gerente (Checker):** Recebe a remessa no painel com uma **Tag de Risco** colorida. Avalia o alerta da IA e libera no banco (ou bloqueia).
4. **Finalização:** Sistema dispara e-mail com a Trilha de Auditoria (Audit Trail).

---

## 3. Guia de Treinamento do Modelo Preditivo (Setup e Execução)

Para detectar fraudes com precisão usando o dataset `online-payments-fraud-detection-dataset`, precisamos configurar sua máquina e treinar o modelo clássico antes de plugar a GenAI.

### 3.1. Pré-Requisitos na Sua Máquina (O que instalar)
Abra seu terminal e garanta que possui o seguinte ambiente Python:
```bash
# 1. Crie um ambiente virtual para o projeto
python -m venv venv_mba
# Ative o ambiente (No Windows)
venv_mba\Scripts\activate

# 2. Instale as bibliotecas essenciais para Ciência de Dados
pip install pandas numpy scikit-learn xgboost imbalanced-learn jupyter kagglehub
```

**Para rodar a GenAI (LLaMA) Localmente:**
Se for rodar o LLM na sua máquina (precisa de +8GB RAM), acesse **[ollama.com](https://ollama.com)**, baixe o executável e rode no terminal:
```bash
ollama run llama3:8b
```
*(Se sua máquina for lenta, usaremos a API gratuita da Groq no código do backend para o LLaMA rodar na nuvem instantaneamente).*

### 3.2. Passo a Passo do Treinamento do Modelo (Machine Learning)
Você criará um arquivo `treinar_modelo.ipynb` na pasta do projeto e executará:

1. **Coleta:** Usar o `kagglehub` para baixar o `.csv`.
2. **Feature Engineering (Engenharia de Dados):** O dataset tem colunas como `amount`, `oldbalanceOrg`, `newbalanceOrig`. O modelo fica muito mais inteligente se criarmos colunas derivadas. Exemplo: `diferenca_saldo = oldbalanceOrg - newbalanceOrig`. Se a diferença de saldo não bater com o `amount`, a chance de fraude é gigantesca!
3. **Balanceamento:** Fraudes (`isFraud=1`) representam menos de 1% dos dados. Usaremos `SMOTE` (da biblioteca `imbalanced-learn`) para criar fraudes sintéticas e ensinar o modelo corretamente.
4. **Treinamento e Exportação:** Treinaremos um algoritmo `XGBoost`.
```python
# Exemplo do final do seu script Jupyter
import joblib
from xgboost import XGBClassifier

modelo = XGBClassifier()
modelo.fit(X_train_balanceado, y_train_balanceado)

# Salva o "cérebro" treinado num arquivo que o FastAPI vai ler depois
joblib.dump(modelo, 'detector_fraudes_v1.pkl')
```

---

## 4. O Dashboard Executivo da Diretoria e Auditoria

A Diretoria exige transparência total sem ler código.
- **Painel Resumo (KPls):** Volume de transações, montante salvo (bloqueado pela IA) e tempo médio de aprovação.
- **Trilha de Imutabilidade (WORM - Write Once, Read Many):** Uma tabela no frontend exibindo o **Log de Auditoria**. Cada ação de aprovação mostrará a *Data, Hora, IP do aprovador, Score da IA e Parecer do LLaMA*. Ninguém (nem o DBA) deve conseguir alterar esse registro no sistema.
- Ao clicar em uma transação suspeita, o Diretor vê o **Resumo Gerado pelo LLaMA**, ex: *"Transação bloqueada. Motivo: O modelo ML detectou risco de 92% devido a anomalia de saldo, e a leitura do anexo não localizou o CNPJ correspondente ao fornecedor cadastrado."*

---

## 5. Plano de Execução Detalhado (Roadmap)

### Fase 1: Kickoff e Infraestrutura (Dia 1)
- [ ] Clonar repositório `trabalho_final_digital_college_mba` localmente.
- [ ] Criar pastas: `frontend`, `backend`, `ai_models`.
- [ ] Baixar Ollama (se for usar local) ou criar conta na Groq.

### Fase 2: IA Preditiva - O Motor XGBoost (Dias 2-3)
- [ ] Baixar dataset via `kagglehub`.
- [ ] Criar *features* de anomalia financeira (comparativo de saldos).
- [ ] Treinar o modelo, avaliar precisão (F1-Score) e exportar o `.pkl`.

### Fase 3: API Backend e Processo (Dias 4-6)
- [ ] Criar endpoints FastAPI (fornecedores, remessas, logs).
- [ ] Configurar um banco de dados local super rápido (`SQLite` ou leitura de arquivos `JSON`) para simular as tabelas do sistema sem gargalos de rede.
- [ ] Criar a função que carrega o `.pkl` e devolve o risco.
- [ ] Criar a rota que recebe a foto da nota, passa pro LLaMA (Ollama/Groq) fazer OCR e comparar com o JSON do pagamento.

### Fase 4: Frontend e UX de Apresentação (Dias 7-9)
- [ ] Criar a tela de "Seleção de Perfil" (Analista / Gerente / Diretor).
- [ ] Telas do Analista: Formulário limpo para envio da nota e digitação de dados.
- [ ] Tela do Gerente: Lista de remessas pendentes com Alerta Visual (Verde, Amarelo, Vermelho baseado na IA).
- [ ] Tela da Diretoria (Dashboard).

### Fase 5: Validação e Pitch (Dia 10)
- [ ] Testar cenários: Subir uma nota falsa e ver a IA travar o pagamento.
- [ ] Fazer o deploy do Frontend no Netlify e Backend no Render.
- [ ] Preparar o discurso de defesa focando na **redução de risco financeiro e compliance corporativo**.

---

## 6. Segurança e Profissionalismo Extras Adicionados
- **Zero-Trust Interno:** Mesmo na tela do gerente (Checker), ele deve justificar textualmente caso libere um pagamento que a IA marcou como "Alto Risco". Isso garante responsabilidade (*accountability*).
- **Validação de Anexos (MIME Type):** No backend Python, checaremos o cabeçalho binário do arquivo, não apenas a extensão `.pdf`. Evita que enviem arquivos maliciosos (vírus/ransomware) disfarçados de notas fiscais para o servidor da empresa.