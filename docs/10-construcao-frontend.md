# 10 — Construção do frontend (React)

Como a interface foi organizada, como consome a API e como cada perfil enxerga os resultados do modelo.

---

## Stack e estrutura

| Tecnologia | Uso |
|------------|-----|
| React 19 | UI componentizada |
| Vite 8 | Build e dev server |
| Tailwind CSS 4 | Estilo dark corporativo (`index.css`) |
| React Router 7 | Rotas `/`, `/analista`, `/gerente`, `/diretoria` |
| Axios | Cliente HTTP (`api/client.ts`) |
| Recharts | Gráficos da Diretoria |

```
frontend/src/
├── main.tsx              # Bootstrap React
├── App.tsx               # Rotas + ProtectedRoute
├── index.css             # Tema (--color-surface, module-card)
├── context/
│   └── RoleContext.tsx   # Perfil demo (localStorage mba_role)
├── api/
│   ├── client.ts         # apiClient.* métodos REST
│   ├── apiConfig.ts      # isDemoMode() para Netlify
│   └── demoResolver.ts   # Dados estáticos sem backend
├── pages/
│   ├── Home.tsx          # Escolha de perfil
│   ├── Analista.tsx      # Remessas, cadastros, contas
│   ├── Gerente.tsx       # Aprovações, KYC
│   ├── Diretoria.tsx     # KPIs, gráficos, histórico
│   └── Guia.tsx          # Ajuda in-app
├── components/           # Painéis reutilizáveis
└── utils/
    └── filtrosMovimentacao.ts  # Lógica período/KPIs no FE
```

---

## Rotas e proteção

| Rota | Página | Quem acessa |
|------|--------|-------------|
| `/` | Home | Todos |
| `/analista` | Analista | `role === analista` |
| `/gerente` | Gerente | `role === gerente` |
| `/diretoria` | Diretoria | `role === diretoria` |
| `/guia` | Guia | Todos |

`ProtectedRoute` em `App.tsx`: alinha perfil à URL (permite link direto `/analista` após deploy).

---

## Cliente API

`api/client.ts` centraliza chamadas:

| Grupo | Exemplos |
|-------|----------|
| Remessas | `criarRemessa`, `enviarRemessa`, `listarRemessas` |
| Pagamentos | upload anexos |
| Dashboard | `kpis`, `metricasIA`, `historicoControleIA` |
| Cadastros | fornecedores, colaboradores |

**Modo demo (Netlify):** se `isDemoMode()` → adapter mock em `demoResolver.ts` (sem backend).

**Produção local:** proxy Vite `/api` → `localhost:8000` ou `VITE_API_URL`.

---

## Páginas por perfil

### Home (`Home.tsx`)

- Cards Analista / Gerente / Diretoria
- `setRole` + `navigate` com `flushSync` (evita race no deploy)

### Analista (`Analista.tsx`)

| Módulo | Componente | API |
|--------|------------|-----|
| Remessas | formulário inline | `remessas`, `pagamentos` |
| Novos cadastros | `CadastrosPanel` | `fornecedores`, `colaboradores` |
| Consultar cadastros | `CadastrosPanel` | listagens |
| Contas | `ContasPanel` | `contas` |

**IA:** botão enviar → `POST .../enviar` (não roda ao adicionar pagamento).

### Gerente (`Gerente.tsx`)

| Módulo | O que mostra do modelo |
|--------|------------------------|
| Remessas | `RiskBadge`, `ml_motivos`, `genai_parecer` via `PagamentoRevisaoPanel` |
| Fornecedores | Aprovação KYC |
| Cadastros | Solicitações analista |

Justificativa obrigatória: validada no backend ao liberar com alertas.

### Diretoria (`Diretoria.tsx`)

| Módulo | Componente | Dados ML |
|--------|------------|----------|
| Visão executiva | `IndicadoresExecutivos` + `PainelGraficosIA` | fraudes ML, execuções IA |
| Histórico IA | `HistoricoControleIA` | versões, `triggered_by` |
| Alertas | listas | não cadastrados |
| Auditoria | logs WORM | — |

Filtros: `FiltrosMovimentacao` (De/Até, somente fraudes ML).

---

## Componentes-chave

| Componente | Função |
|------------|--------|
| `Layout.tsx` | Header, nav por perfil, footer |
| `ModuloSelector.tsx` | Cards “O que deseja fazer?” |
| `RiskBadge.tsx` | ALTO/MÉDIO/BAIXO + % |
| `MlFraudAlert.tsx` | Destaque fraude ML |
| `PainelGraficosIA.tsx` | 3 gráficos + badges |
| `IndicadoresExecutivos.tsx` | KPIs alinhados aos gráficos |
| `PagamentoDetalheModal.tsx` | Drill-down PAY |
| `ErrorBoundary.tsx` | Erros de render |

---

## Onde o usuário vê o treinamento XGBoost

| UI | Campo API | Significado |
|----|-----------|-------------|
| Badge risco | `risk_score`, `risk_level` | Composto (ML + heurística + doc) |
| Tag fraude | `ml_fraude_detectada` | ≥ 55% no XGBoost |
| Lista motivos | `ml_motivos` | Saída explicável |
| Parecer | `genai_parecer` | Texto com prefixo ML se fraude |
| Card Diretoria | contagem fraudes | Agregação `ml_fraude_detectada` |

Rastreio: [modelo-ia/08](modelo-ia/08-vinculo-treinamento-e-runtime.md) §6.

---

## Tema visual

Definido em `index.css`:

- Fundo `#0b0f1a`, accent `#10b981`
- Classes: `glass-panel`, `module-card`, `btn-primary`

Screenshots: [docs/assets](README.md#telas-do-sistema).

---

## Build e deploy

| Comando | Resultado |
|---------|-----------|
| `npm run dev` | :5173 |
| `npm run build` | `dist/` → Netlify |

Ver [04-deploy-netlify](04-deploy-netlify.md).

---

## Como estender o frontend

| Necessidade | Onde |
|-------------|------|
| Nova tela | `pages/` + rota em `App.tsx` |
| Novo KPI | `Diretoria.tsx` + método em `client.ts` |
| Novo gráfico | `PainelGraficosIA.tsx` |
| Autenticação real | Substituir `RoleContext` por JWT (roadmap SaaS) |

---

## Relacionados

- [09-construcao-backend](09-construcao-backend.md)
- [GUIA_UTILIZACAO.md](../GUIA_UTILIZACAO.md)
- [05-apresentacao](05-apresentacao.md)
