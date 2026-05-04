# Fluxo de trabalho — Arquitetura de sistemas com GenAI

Documento complementar ao `SKILL.md`. Carregar quando o caso exigir profundidade em fase, governança ou entregáveis.

---

## 1. Descoberta e alinhamento

- **Problema de negócio** vs solução desejada (evitar “IA por IA”).
- **Restrições externas**: regulatório, contratos, fornecedores já escolhidos.
- **Métricas de sucesso**: qualidade (humano/LLM-judge), latência p95/p99, custo por requisição, taxa de escalação para humano.

## 2. Modelagem de domínio

- Eventos de negócio vs eventos técnicos.
- **Bounded contexts** com linguagem ubíqua resumida.
- Mapa de contexto (integração: parceria, cliente-fornecedor, anticorrupção).

## 3. Arquitetura lógica

- **Estilo arquitetural** principal (modular monolith vs serviços; event-driven onde couber).
- **APIs** (síncrono vs assíncrono); contratos versionados.
- **Consistência**: sagas/outbox para efeitos colaterais críticos.

## 4. Camada GenAI (estado da arte pragmático)

| Tópico | Perguntas guia |
|--------|----------------|
| Orquestração | Um agente, grafo de etapas, ou pipeline RAG fixo? |
| Contexto | O que entra no prompt? TTL e sanitização? |
| RAG | Chunking, re-ranking, freshness, permissões por documento? |
| Ferramentas | Quais tools o agente pode invocar? Idempotência e timeouts? |
| Guardrails | Políticas de conteúdo, PII, injeção indireta, allowlist de domínios? |
| Avaliação | Golden sets, regressão por release, shadow mode? |
| Custo | Cache de embeddings/respostas, model routing, batch offline? |

## 5. Dados e MLOps leve

- Fontes da verdade e **PII minimization**.
- **Lineage** quando respostas dependem de dados dinâmicos.
- Versionamento de **índices** / artefatos RAG junto ao deploy da aplicação.

## 6. Segurança e conformidade

- Modelo de ameaças STRIDE resumido (spoofing, tampering, repudiation, information disclosure, DoS, elevation).
- **Secrets** e rotação; least privilege IAM.
- **Logs**: o que não pode ir para log (prompts com PII).

## 7. Operação e SRE

- SLIs/SLOs para caminho crítico **incluindo** dependências de modelo/API.
- **Runbooks**: degradação (modo sem LLM, resposta cacheada, fila).
- **DR**: RPO/RTO alinhados a custo; backups de estado e de configuração de GenAI.

## 8. Cloud-agnostic e portabilidade

- **Abstrações**: interfaces para storage, fila, secrets, observabilidade — implementações trocáveis.
- **Infra as code** pensando em múltiplos provedores ou ao menos em **camadas** que não vazem APIs proprietárias no domínio.
- **Kubernetes** como denominador comum opcional — avaliar se o time sustenta a complexidade.

## 9. Encerramento

- ADRs priorizados (o que decide primeiro desbloqueia implementação).
- Roadmap em ondas: fundação → dados/GenAI → hardening → escala.
