# 04 — Segurança, compliance e LGPD

## Princípios para dados financeiros

1. **Confidencialidade** — acesso mínimo necessário (RBAC).
2. **Integridade** — trilha WORM; análises IA versionadas.
3. **Disponibilidade** — backup, monitoramento, SLA.
4. **Não repúdio** — quem aprovou, quando, com qual justificativa.
5. **Transparência IA** — motivos ML/heurística visíveis ao gerente.

## Controles técnicos obrigatórios (produção)

| Controle | Implementação |
|----------|----------------|
| Transporte | HTTPS TLS 1.2+ em todo tráfego |
| Autenticação | E-mail + senha forte ou SSO; MFA (Enterprise) |
| Autorização | Papéis: analista, gerente, diretoria, admin_tenant |
| Sessão | JWT curto + refresh; logout invalida token |
| Senhas | bcrypt/argon2; política de complexidade |
| API | Rate limit por IP e por tenant |
| Banco | Credenciais em secrets; sem SQLite em produção |
| Anexos | Storage privado; URL assinada temporária para download |
| Logs | Sem CPF/CNPJ completo em log de aplicação (mascarar) |
| Auditoria | `audit_logs` append-only; sem UPDATE/DELETE na app |

## LGPD — papéis e documentos

| Papel | Quem |
|-------|------|
| Controlador | **Cliente** (empresa contratante) |
| Operador | **Você** (provedor do Guardião) |

### Documentos a publicar/fornecer

| Documento | Conteúdo |
|-----------|----------|
| **Política de Privacidade** | Dados coletados, finalidade, bases legais |
| **DPA (Acordo de Tratamento)** | Anexo ao contrato B2B |
| **Termos de Uso** | Licença SaaS, limitações, IA assistiva |
| **Registro de operações** | ROPA simplificado por tenant (sob demanda) |

### Bases legais típicas

- Execução de contrato (prestação do SaaS)
- Legítimo interesse (prevenção a fraude) — com LIA documentada
- Obrigação legal (retenção para auditoria, quando aplicável)

### Direitos do titular

Processo para atender: acesso, correção, eliminação (após fim contrato), portabilidade (export JSON/CSV).

**Prazo sugerido:** 15 dias úteis via canal `privacidade@seudominio.com.br`.

## Retenção e exclusão

| Dado | Retenção padrão | Pós-cancelamento |
|------|-----------------|------------------|
| Pagamentos e IA | Vigência do contrato | Export 30 dias; delete 90 dias |
| Audit logs | 5 anos (configurável) | Mantido se lei exigir; senão anonimizar |
| Anexos | Idem pagamentos | Delete com pagamentos |
| Backups | 30–90 dias rolling | Expurgo automático |

## Segurança da IA

| Risco | Mitigação |
|-------|-----------|
| Falso positivo bloqueia operação | Gerente decide; IA não executa pagamento |
| Vazamento em prompt GenAI | Não enviar dados desnecessários; DPA com provedor LLM |
| Modelo enviesado | Retreino periódico; métricas F1/AUC por tenant |
| Dependência Ollama local | Fallback template; SLA com API cloud |

## Compliance financeiro (orientação, não aconselhamento jurídico)

- Alinhar processo à **política de alçadas** interna do cliente.
- Manter evidência para auditoria externa (Big4, interna).
- Se integrar com banco: exigências adicionais (PCI não se aplica se não armazena cartão).
- Setores regulados (saúde, financeiro): revisão jurídica do DPA.

## Testes de segurança antes do 1º cliente pagante

- [ ] Scan dependências (`pip audit`, `npm audit`)
- [ ] Teste IDOR entre tenants (dois JWT diferentes)
- [ ] Teste upload (tipo MIME, tamanho, path traversal)
- [ ] Revisão CORS e headers (CSP, HSTS)
- [ ] Pentest leve ou bug bounty após 5+ clientes

## Certificações (roadmap longo prazo)

| Certificação | Quando considerar |
|--------------|-------------------|
| ISO 27001 | > 20 clientes Enterprise |
| SOC 2 Type II | Clientes internacionais |
| Selo LGPD | Marketing B2B Brasil |
