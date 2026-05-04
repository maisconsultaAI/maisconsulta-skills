# Exportar Architecture Deliverable para Word (.docx) ou PDF

O **fonte da verdade** é o Markdown preenchido a partir de `templates/architecture-deliverable.md`. Os diagramas **Mermaid C4** precisam ser **renderizados** para imagens antes do Pandoc incluir figuras no Word/PDF (Pandoc puro não executa Mermaid).

---

## Pré-requisitos sugeridos

| Ferramenta | Uso |
|------------|-----|
| [Pandoc](https://pandoc.org/installing.html) | `md` → `.docx` / `.pdf` |
| [Quarto](https://quarto.org/docs/get-started/) | Alternativa com bom suporte a Mermaid em HTML/PDF |
| Node.js + `@mermaid-js/mermaid-cli` | `mmdc` renderiza cada `.mmd` → `.png` / `.svg` |

---

## Fluxo recomendado (Mermaid → imagens → Pandoc)

1. Gere o `.md` final a partir do template (C4 obrigatório já no arquivo).
2. **Extraia** cada bloco ```mermaid … ``` para arquivos `diagrama-01.mmd`, `diagrama-02.mmd`, etc. (ou use o script `scripts/export_architecture_doc.py --render-mermaid` se `mmdc` estiver no PATH).
3. Para cada arquivo:

   ```bash
   npx -y @mermaid-js/mermaid-cli -i diagrama-01.mmd -o build/c4-context.png -b transparent
   ```

4. No Markdown de entrega **final para export**, substitua os blocos mermaid por imagens:

   ```markdown
   ![C4 Context](build/c4-context.png)
   ```

   (mantenha os `.mmd` no repositório como fonte editável.)

5. **Word:**

   ```bash
   pandoc arquitetura-projeto.md -o arquitetura-projeto.docx --from markdown+yaml_metadata_block
   ```

6. **PDF** (exige engine LaTeX ou usar Quarto):

   ```bash
   pandoc arquitetura-projeto.md -o arquitetura-projeto.pdf --pdf-engine=xelatex
   ```

Se o PDF com Pandoc falhar por fontes/LaTeX no Windows, prefira **Quarto**: `quarto render arquivo.qmd` com o mesmo conteúdo e `format: pdf`.

---

## Quarto (atalho com Mermaid)

Crie um `arquitetura.qmd` com cabeçalho YAML e o corpo igual ao Markdown; o Quarto pode renderizar Mermaid em PDF/HTML sem passo manual de `mmdc` em muitos setups.

---

## Checklist de exportação

- [ ] `validate_architecture_brief.py` passou sem `[ERRO]`.
- [ ] Três diagramas C4 presentes no `.md` (ou equivalentes em PNG no export final).
- [ ] Figuras com legenda curta no documento Word/PDF.
- [ ] Metadados de capa (versão, data, confidencialidade) preenchidos.
