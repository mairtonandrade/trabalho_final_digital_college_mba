# 02 — Arquitetura

```mermaid
flowchart TB
  subgraph frontend [Frontend - Netlify]
    Home[Home / Perfis]
    Ana[Analista]
    Ger[Gerente]
    Dir[Diretoria]
  end
  subgraph backend [Backend - FastAPI]
    API[Routers REST]
    IA[ia_analise.py]
    ML[fraud_engine XGBoost]
    Gen[genai_audit]
    DB[(SQLite)]
  end
  Home --> Ana
  Home --> Ger
  Home --> Dir
  Ana --> API
  Ger --> API
  Dir --> API
  API --> IA
  IA --> ML
  IA --> Gen
  API --> DB
```

## Repositório

```
trabalho_final_digital_college_mba/
├── frontend/          # React + Vite + Tailwind
├── backend/           # FastAPI + SQLite
├── ai_models/         # Treino e .pkl do XGBoost
├── docs/              # Esta documentação + assets
└── netlify.toml       # Build do frontend
```

## Modelos principais

- `Remessa` — lote de pagamentos com status do fluxo
- `Pagamento` — beneficiário, valor, scores IA atuais
- `PagamentoAnaliseIA` — histórico versionado por reanálise
- `AuditLog` — trilha WORM por perfil

## Perfis e responsabilidades

| Perfil | Ações |
|--------|--------|
| Analista | Cadastros, remessas, anexos, envio IA |
| Gerente | Revisão documental, devolução, liberação |
| Diretoria | KPIs, detecções, pontos de atenção |
