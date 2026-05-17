# Pitch Manus AI — Guardião de Pagamentos (10 slides)

Copie o bloco abaixo e cole no **Manus AI**. Anexe as imagens indicadas antes de gerar.

**Imagens para anexar** (pasta `docs/assets/` do repositório — screenshots reais da UI):

| Arquivo | Uso no pitch |
|---------|----------------|
| `01-home.png` | Slide 3 (Solução) — visão geral e perfis |
| `02-analista.png` | Slide 3 ou 4 — operação em remessas |
| `03-gerente-ia.png` | Slide 5 (Diferenciais) — revisão ML + GenAI |
| `04-diretoria.png` | Slide 4 ou 9 (Tração) — KPIs executivos |
| `05-paineis-ia.png` | Slide 9 — gráficos IA (perfil, evolução, detecção) |
| `06-fluxo-completo.png` | Slide 3 — fluxo ponta a ponta do processo |

**Paleta oficial (mesmo tom do app — `frontend/src/index.css`):**

| Token | Hex | Uso |
|--------|-----|-----|
| Fundo surface | `#0b0f1a` | Background dos slides |
| Surface elevado | `#121829` | Cards e painéis |
| Cards UI | `#1e293b` / slate-900 | Blocos internos |
| Accent / verde | `#10b981` | CTAs, logo GP, sucesso |
| Accent muted | `#064e3b` | Destaques verdes escuros |
| Analista | `#22d3ee` | Faixa analista, gráficos |
| Gerente | `#a78bfa` | Faixa gerente |
| Sistema / IA | `#fbbf24` | Pipeline automático |
| Fraude / alerta | `#f87171` | Badges de risco |
| Texto principal | `#f1f5f9` | Títulos e corpo |
| Texto secundário | `#94a3b8` / slate-300 | Subtítulos |
| Bordas | `#475569`–`#64748b` | Divisores |

Gradientes sutis no fundo (opcional): radial emerald `rgba(16,185,129,0.12)`, indigo `rgba(99,102,241,0.08)`, cyan `rgba(6,182,212,0.06)`.

**Configuração no Manus:** formato **16:9**, estilo **corporativo dark** usando **exatamente** a paleta acima (não usar azul claro genérico nem verde limão).

---

## PROMPT (copiar daqui para baixo)

```
Crie uma apresentação de vendas (pitch deck) profissional, elegante e persuasiva em português do Brasil, com EXATAMENTE 10 slides no formato 16:9.

PALETA OBRIGATÓRIA (idêntica ao produto Guardião de Pagamentos):
- Fundo: #0b0f1a
- Cards: #121829 e #1e293b
- Verde accent: #10b981
- Ciano (analista): #22d3ee
- Violeta (gerente): #a78bfa
- Âmbar (sistema/IA): #fbbf24
- Vermelho alerta: #f87171
- Texto: #f1f5f9 e #94a3b8
- Tipografia: Segoe UI, Inter ou sans-serif moderna

Use as imagens anexadas como referência visual dos mockups reais da plataforma (home, analista, gerente com IA, diretoria com KPIs, painéis de gráficos IA, fluxo completo do processo). Incorpore-as nos slides adequados com layout premium — não distorça os textos; mantenha acentuação correta em português (Guardião, Governança, inteligência, etc.).

O objetivo do pitch NÃO é fechar a venda na hora, mas despertar interesse e levar o prospect ao próximo passo: reunião de demonstração ao vivo ou piloto de 30 dias.

---

## PRODUTO

**Guardião de Pagamentos** — plataforma web de governança financeira com Inteligência Artificial para aprovação de pagamentos corporativos.

**Frase de marca:** Pagamentos seguros. Decisões rápidas. Auditoria que não se perde.

**Stack:** React 19 + FastAPI + XGBoost (anti-fraude) + GenAI (pareceres) + trilha de auditoria WORM.

**Perfis:** Analista (monta remessas) → Gerente (2ª assinatura + revisão IA) → Diretoria (KPIs e compliance).

**Projeto:** MBA Digital College — Ciência de Dados & GenAI (produto demonstrável e evoluível para enterprise).

**Repositório:** github.com/mairtonandrade/trabalho_final_digital_college_mba

---

## ESTRUTURA OBRIGATÓRIA — 10 SLIDES

Siga esta ordem e estes títulos. Cada slide: título forte + no máximo 4 bullets curtos OU 1 número de impacto + visual (ícone, diagrama ou imagem anexa). Muito espaço em branco. Tom executivo B2B.

---

### SLIDE 1 — INTRODUÇÃO
**Título sugerido:** Guardião de Pagamentos

**Conteúdo:**
- Uma única frase de impacto que resume a essência do negócio, por exemplo:
  *"Governança financeira com IA que protege cada pagamento — da remessa à liberação, com dupla aprovação e auditoria em tempo real."*
- Subtítulo discreto: Plataforma de contas a pagar inteligente
- Logo/conceito visual GP (verde #10b981 / teal)
- Sem bullets neste slide — apenas impacto visual

---

### SLIDE 2 — O PROBLEMA
**Título:** O mercado paga caro pela falta de governança

**Dores a destacar:**
- Fraude e pagamentos a beneficiários não cadastrados (PJ/PF)
- Remessas revisadas em planilhas e e-mail — sem trilha única
- Gerente sobrecarregado; diretoria sem visão consolidada
- Auditoria reativa, cara e lenta
- IA usada sem controle humano gera desconfiança em CFOs

Use ícones de alerta vermelho (#f87171) e âmbar (#fbbf24). Tom de urgência, não catastrófico.

---

### SLIDE 3 — A SOLUÇÃO
**Título:** Uma plataforma, três perfis, IA no momento certo

**Conteúdo:**
- **Inserir imagem anexa principal:** `06-fluxo-completo` (cadastro → remessa → IA → gerente → diretoria/WORM)
- **Inserir imagem secundária:** `01-home` (três perfis)
- Pipeline: Heurísticas + XGBoost + GenAI + decisão humana
- Destaque: IA não roda a cada clique — roda no envio da remessa (eficiência + consistência)

---

### SLIDE 4 — PROPOSTA DE VALOR
**Título:** O que o cliente ganha na prática

**Benefícios diretos (use ícones nas cores por perfil):**
| Stakeholder | Benefício |
|-------------|-----------|
| Analista | Remessas em lote, menos retrabalho, anexos guiados |
| Gerente | Score ML + parecer GenAI + histórico PAY por pagamento |
| Diretoria | KPIs, gráficos e alertas de fraude em um painel |
| Compliance | Trilha WORM imutável, justificativas obrigatórias |
| Empresa | Menos risco operacional antes do dinheiro sair |

**Inserir imagens anexas:** `04-diretoria` e opcionalmente `02-analista`.

---

### SLIDE 5 — DIFERENCIAIS
**Título:** Por que o Guardião e não planilha, ERP genérico ou IA isolada

**Diferenciais competitivos:**
1. **Dupla aprovação nativa** — segregação analista ≠ gerente
2. **IA híbrida explicável** — ML + regras + GenAI (não caixa-preta)
3. **Copiloto, não autômato** — humano decide; IA evidencia
4. **Histórico versionado** — cada reanálise registrada (`envio_gerente`, `reanalise_gerente`)
5. **Métricas coerentes** — KPIs, gráficos e histórico com mesma base de dados
6. **Catálogo amplo de detecções** — fraude ML, não cadastrado, valor atípico, velocity, documento divergente

**Inserir imagem anexa:** tela gerente com alertas ML (`03-gerente-ia`).

---

### SLIDE 6 — MODELO DE NEGÓCIOS
**Título:** Como o Guardião gera receita

**Sugestão de modelo SaaS B2B (apresentar como proposta comercial):**

| Plano | Público | Preço sugerido (referência) | Inclui |
|-------|---------|----------------------------|--------|
| **Starter** | PME, até 50 pagamentos/mês | R$ 1.990/mês | 2 perfis, IA básica, auditoria 90 dias |
| **Professional** | Médio porte, até 500 pag/mês | R$ 4.990/mês | 3 perfis, GenAI, API, suporte |
| **Enterprise** | Grande volume / multi-CNPJ | Sob consulta | SSO, ERP, modelo customizado, SLA |

**Receitas adicionais:** implantação (setup), treinamento, retreino do modelo XGBoost por segmento, horas de consultoria em compliance.

**Nota no rodapé:** Valores ilustrativos para pitch — ajustar na proposta comercial.

---

### SLIDE 7 — MERCADO
**Título:** Mercado endereçável

**Dados e narrativa (use fontes genéricas se necessário, tom conservador):**
- **TAM:** Empresas médias e grandes no Brasil com contas a pagar estruturadas (dezenas de milhares)
- **SAM:** Setores com alto volume e risco — indústria, varejo, serviços, construção, saúde
- **SOM (inicial):** PME/ médias que processam 20–500 pagamentos/mês e sofrem com fraude ou auditoria
- Tendência: PIX/TED em alta, pressão por IA responsável pós-regulamentação, CFOs exigindo trilha de auditoria
- Concorrência indireta: ERPs, ferramentas de AP automation, consultorias manuais — gap: IA + governança integrada

Visual: funil TAM → SAM → SOM ou mapa do Brasil com setores-alvo.

---

### SLIDE 8 — EQUIPE
**Título:** Quem está por trás do Guardião

**Apresentar como slide de credibilidade (ajuste nomes/fotos se o usuário fornecer depois):**

- **Mairton Andrade** — Idealizador e desenvolvimento do produto | MBA Digital College (Ciência de Dados & GenAI)
  - Responsável por arquitetura full-stack, modelo XGBoost, integração GenAI e produto demo
- **Digital College / programa MBA** — Validação acadêmica e metodologia em dados e IA
- **Espaço para co-founders / advisors:** Compliance financeiro, especialista em tesouraria, DevOps cloud

Tom: profissional, humano, confiável. Use avatares ou iniciais se não houver foto.

---

### SLIDE 9 — TRAÇÃO E VALIDAÇÃO
**Título:** Resultados já alcançados

**Prova social e métricas da demo (6 meses simulados):**
- Plataforma funcional: frontend (Netlify-ready) + API FastAPI + modelo treinável
- ~96 pagamentos analisados pela IA, ~110 execuções IA, 24 fraudes ML detectadas
- Gráficos coerentes: Analista 74%, Sistema 20%, Gerente 14% das execuções IA
- Catálogo de 12+ tipos de detecção (fraude ML, PJ/PF não cadastrado, valor atípico, GenAI documento, velocity)
- Trilha de auditoria WORM com centenas de eventos
- Documentação completa, repositório público no GitHub
- Demo ao vivo em 20 minutos: analista → gerente → diretoria

**Depoimento sugerido (placeholder):**
*"A visão da diretoria finalmente conversa com o que o gerente aprova — os números batem."* — Perfil CFO (piloto simulado)

**Inserir imagens anexas:** `04-diretoria` e `05-paineis-ia`.

---

### SLIDE 10 — CONCLUSÃO E CHAMADA PARA AÇÃO
**Título:** Vamos dar o próximo passo?

**Mensagem de fechamento:**
- Recapitule em 1 linha: menos fraude, mais controle, auditoria pronta
- **Oferta para o prospect:**
  - Demonstração ao vivo gratuita (20 min) — todos os perfis
  - **Piloto de 30 dias** com até 100 pagamentos/mês (plano Starter) — implantação assistida
- **Contato:**
  - E-mail: **mairton_andrade@hotmail.com**
  - GitHub / demo: github.com/mairtonandrade/trabalho_final_digital_college_mba
  - LinkedIn: [incluir espaço para @mairtonandrade ou link se o apresentador adicionar]
- **CTA visual grande:** "Agende sua demonstração" (botão verde #10b981)

Frase final na tela:
*"O Guardião de Pagamentos transforma aprovação de pagamentos em vantagem competitiva — com IA que respeita quem decide."*

---

## DIRETRIZES VISUAIS (OBRIGATÓRIAS)

- Proporção: 16:9
- Estilo: corporativo dark premium (fintech + consultoria) — MESMAS cores do app
- Paleta: ver tabela no início deste documento (não inventar cores novas)
- Tipografia: sans-serif (Inter, Segoe UI ou similar)
- Máximo 40 palavras de corpo por slide (exceto slide 6 tabela de planos)
- Ícones lineares minimalistas
- Não usar caracteres quebrados (ç, ã, ê sempre corretos)
- Incluir notas do apresentador (2 frases por slide) em documento separado ou modo apresentador

---

## TOM

- B2B, CFO/Controller/Tesouraria/Compliance
- Honesto: "IA assistiva, decisão humana"
- Não prometer 100% anti-fraude — "camada adicional de detecção e governança"
- Foco: dor → solução → prova → piloto/demo

---

## ENTREGÁVEIS DO MANUS

1. Apresentação PowerPoint ou Google Slides — 10 slides exatos
2. Notas do apresentador em português (2–3 frases por slide)
3. Opcional: 1 slide-resumo executivo (one-pager) para envio pós-reunião por e-mail

Gere todo o conteúdo em português brasileiro, pronto para apresentar a diretores financeiros e gestores de tesouraria de empresas médias.
```

---

## Checklist antes de enviar ao Manus

- [ ] Anexar `01-home.png`, `02-analista.png`, `03-gerente-ia.png`, `04-diretoria.png`, `05-paineis-ia.png`, `06-fluxo-completo.png`
- [ ] Colar o prompt completo acima
- [ ] Escolher **16:9** e tema **dark** com paleta `#0b0f1a` + `#10b981`
- [ ] Após gerar: revisar slide 8 (equipe) e adicionar sua foto/LinkedIn se desejar
- [ ] Ajustar preços do slide 6 conforme sua estratégia comercial real

**Contato no pitch:** mairton_andrade@hotmail.com

**Regenerar imagens no repositório:**
```powershell
# Screenshots reais (com app rodando em :5173 e API em :8000)
cd frontend
npm install playwright --save-dev
node ../scripts/capture_doc_screenshots.mjs

# Diagrama do fluxo completo
cd ..
.\scripts\regenerate_doc_assets.ps1
```
