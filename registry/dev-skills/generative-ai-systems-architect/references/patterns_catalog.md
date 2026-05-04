# Catálogo de padrões e práticas (referência)

Uso: escolher padrões **com justificativa** no Architecture Brief; evitar “catálogo completo” sem decisão.

---

## Integração e comunicação

- **API Gateway / BFF**: agregação para clients; rate limit e auth no edge.
- **Outbox / Transactional messaging**: consistência entre DB e eventos.
- **Idempotency keys**: APIs públicas e callbacks de agentes/ferramentas.
- **Webhook ingress**: validação de assinatura, replay protection.

## Dados

- **CQRS** (separar leitura pesada de escrita) — com cautela à complexidade.
- **Event sourcing** — só quando auditoria temporal for requisito central.
- **Data mesh light**: ownership explícito de datasets consumidos por RAG.

## Resiliência

- **Circuit breaker / bulkhead** em chamadas a LLM e a integrações terceiras.
- **Timeouts + orçamento de retries** por cadeia de agente.
- **Graceful degradation**: resposta determinística quando modelo indisponível.

## GenAI / LLM

- **RAG com re-ranking** quando recall precisa ser alto.
- **Prompt caching / prefix caching** quando prompts são estáveis.
- **Small model routing** para tarefas baratas; modelo grande só no nó crítico.
- **Human-in-the-loop** para ações irreversíveis ou de alto risco.

## Segurança

- **Zero trust** entre serviços (mTLS ou identidade workload).
- **Vault** ou equivalente para secrets; sem secrets em imagem ou repo.
- **OPA / policy-as-code** opcional para políticas de deploy e dados.

## Observabilidade

- **Distributed tracing** atravessando chamadas a modelo (span por etapa do grafo).
- **Métricas de custo** por tenant/rota (tokens, chamadas externas).
- **Structured logging** com correlação; redação de PII.

## Multi-cloud / vendor-agnostic

- **Ports & adapters** no núcleo do domínio.
- **Evitar SDKs proprietários** nas regras de negócio; isolar em `infra/`.
- **Containers + CNCF** onde possível; abstrair blob, queue, cache.

## Enterprise

- **Feature flags** para ligar/desligar fluxos GenAI por segmento.
- **Change management**: ADR + revisão de segurança para mudanças de dados em RAG.
