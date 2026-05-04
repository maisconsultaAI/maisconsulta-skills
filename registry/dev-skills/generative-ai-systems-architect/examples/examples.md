# Exemplos de uso — Generative AI Systems Architect

Guia rápido de pedidos. Para um **brief de exemplo** com C4 Mermaid, abra `sample_architecture_brief.md`.  
Para **entrega formal**, copie sempre `../templates/architecture-deliverable.md` e preencha.

---

## Pedido simples (greenfield)

```
"Preciso da arquitetura de um sistema novo: plataforma B2B que usa um copiloto com RAG
sobre documentação interna do cliente. Multi-cloud não é obrigatório mas quero evitar
lock-in de modelo. Carga inicial ~50k req/dia."
```

A skill deve: fazer perguntas de PASSO 1 se faltar domínio/regulação; instanciar o **template** obrigatório; entregar o Brief com **C4Context, C4Container, C4Component** em Mermaid; rodar o validador e, se pedido Word/PDF, seguir `../references/export_word_pdf.md`.

---

## Pedido intermediário (brownfield)

```
"Temos um monólito em Java com Postgres. Queremos expor um agente que chama três APIs internas
e grava auditoria. Quais fronteiras e ADRs você propõe antes de quebrar o monólito?"
```

---

## Pedido avançado (enterprise + GenAI)

```
"Setor financeiro, dados na UE, precisamos de explicabilidade resumida para o operador,
SLA 99.9% no caminho de aprovação, e custo de LLM controlado por caso de uso.
Proponha arquitetura e ADRs incluindo fallback sem modelo."
```

---

## Combinações úteis

| Situação | O que pedir explicitamente |
|----------|---------------------------|
| Só diagrama | "Use o template; C4 Context + Container + Component são obrigatórios." |
| Foco segurança | "Amplie threat model e dados sensíveis no prompt." |
| Custo | "Inclua estratégia de model routing e cache com estimativa qualitativa." |
| Portabilidade | "Liste interfaces mínimas para trocar cloud e provedor de LLM." |

---

## Após gerar o brief

1. Salvar o Markdown em arquivo (recomendado: `docs/architecture/<projeto>.md`).
2. `python scripts/validate_architecture_brief.py arquivo.md` **ou** `python scripts/export_architecture_doc.py arquivo.md --check`
3. Corrigir até `ok: True` ou aceitar avisos conscientemente.

## Word ou PDF

1. Ler `../references/export_word_pdf.md`.
2. `python scripts/export_architecture_doc.py arquivo.md --write-mmd ./build/mmd`
3. Renderizar com `npx -y @mermaid-js/mermaid-cli` e substituir por imagens **ou** usar Quarto; depois Pandoc para `.docx` / `.pdf`.
