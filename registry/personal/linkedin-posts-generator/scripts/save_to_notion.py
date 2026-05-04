#!/usr/bin/env python3
"""
save_to_notion.py — Script determinístico para salvar posts no banco "Posts do LinkedIn" no Notion.

Este script define:
  1. Configuração do banco (IDs e schema)
  2. Mapeamento de estilos da skill → opções do banco
  3. Validações do post (determinísticas, executáveis via Python)
  4. Template do conteúdo da página
  5. Instruções passo a passo para o Claude criar a entrada via MCP

O Claude executa as validações via Python (determinístico) e depois usa as
instruções para chamar Notion:notion-create-pages via MCP (não-determinístico).
"""

import re
import json
from datetime import datetime

# =============================================================================
# CONFIGURAÇÃO DO BANCO NO NOTION
# =============================================================================

# Data source do banco "Posts do LinkedIn"
NOTION_DATA_SOURCE_ID = "6fc126c6-c0cb-421d-8de8-537408635273"

# =============================================================================
# SCHEMA DO BANCO — Campos e opções válidas
# =============================================================================

SCHEMA = {
    # --- Campos preenchidos automaticamente pela skill ---
    "Título": {
        "type": "title",
        "description": "Título do post (campo obrigatório). Resumo curto do tema.",
        "required": True,
    },
    "Status": {
        "type": "status",
        "options": ["Ideia", "Rascunho", "Revisão", "Agendado", "Postado"],
        "default": "Rascunho",
        "description": "Status do post no pipeline de publicação.",
    },
    "Estilo da escrita": {
        "type": "select",
        "options": [
            "Técnico / Especialista",
            "Estratégico / Liderança",
            "Storytelling / Pessoal",
            "Educacional / How-to",
            "Opinião / Provocativo",
        ],
        "description": "Estilo usado na escrita do post.",
    },
    "Tema": {
        "type": "select",
        "options": [
            "Agent Skills",
            "Implementação de IA",
            "Estratégia de IA",
            "Arquitetura / Integração",
            "Liderança / Gestão",
        ],
        "description": "Tema/categoria principal do post.",
    },
    "Objetivo": {
        "type": "text",
        "description": "Objetivo do post (ex: Educar + posicionar expertise).",
    },
    "Hook / 1ª linha": {
        "type": "text",
        "description": "A primeira linha/hook do post, que aparece antes do 'ver mais'.",
    },
    "Horário sugerido": {
        "type": "text",
        "description": "Horário ideal para publicação (ex: Terça, 7h-9h).",
    },
    "Hashtags": {
        "type": "multi_select",
        "options": [
            "AgenticAI",
            "AIArchitecture",
            "TransformacaoDigital",
            "ThoughtLeadership",
            "#Claude",
            "#AgentSkills",
        ],
        "description": "Hashtags do post. Enviar como JSON array.",
    },
    "Data do post": {
        "type": "date",
        "description": "Data planejada ou efetiva da publicação. Formato ISO-8601.",
    },
    "Notas": {
        "type": "text",
        "description": "Raciocínio estratégico e notas adicionais.",
    },

    # --- Campos de métricas (preenchidos depois da publicação) ---
    "Link do post": {
        "type": "url",
        "description": "URL do post publicado no LinkedIn.",
        "fill_on_create": False,
    },
    "Exibições": {"type": "number", "fill_on_create": False},
    "Reações": {"type": "number", "fill_on_create": False},
    "Comentários": {"type": "number", "fill_on_create": False},
    "Compartilhamentos": {"type": "number", "fill_on_create": False},
    "Cliques": {"type": "number", "fill_on_create": False},
    "Interações": {"type": "number", "fill_on_create": False},
    # "Taxa de engajamento (%)" é formula — preenchido automaticamente
    # "Criado em" é created_time — preenchido automaticamente
}


# =============================================================================
# MAPEAMENTO: Estilos da Skill → Opções do Banco
# =============================================================================

ESTILO_MAP = {
    # Estilos principais → select do banco
    "Professoral": "Educacional / How-to",
    "Técnico / Especialista": "Técnico / Especialista",
    "Simplista Conciso": "Educacional / How-to",
    "Cut Through Noise": "Opinião / Provocativo",
    "Storytelling": "Storytelling / Pessoal",
    "Visionário / Futurista": "Estratégico / Liderança",
    "Opinionado / Hot Take": "Opinião / Provocativo",
    "Analítico / Estruturado": "Estratégico / Liderança",
    "Mentor / Conselheiro": "Storytelling / Pessoal",
    "Confessional / Vulnerável": "Storytelling / Pessoal",
    "Inspiracional / Motivacional": "Storytelling / Pessoal",
    "Contrarian": "Opinião / Provocativo",
    "Data-driven": "Técnico / Especialista",
    "Mini-ensaio": "Estratégico / Liderança",
    # Híbridos
    "Cut Through + Analítico": "Opinião / Provocativo",
    "Simplista + Técnico": "Educacional / How-to",
    "Storytelling + Mentor": "Storytelling / Pessoal",
    "Contrarian + Data-driven": "Opinião / Provocativo",
}


# =============================================================================
# MAPEAMENTO: Hashtags do post → multi_select do banco
# =============================================================================

HASHTAG_MAP = {
    "#AgenticAI": "AgenticAI",
    "#AIArchitecture": "AIArchitecture",
    "#TransformacaoDigital": "TransformacaoDigital",
    "#ThoughtLeadership": "ThoughtLeadership",
    "#Claude": "#Claude",
    "#AgentSkills": "#AgentSkills",
}


def map_hashtags(post_text: str) -> list[str]:
    """
    Extrai hashtags do post e mapeia para as opções válidas do multi_select.
    Hashtags não mapeadas são ignoradas (o banco só aceita opções pré-definidas).
    """
    raw_hashtags = re.findall(r'#\w+', post_text)
    mapped = []
    for h in raw_hashtags:
        if h in HASHTAG_MAP:
            mapped.append(HASHTAG_MAP[h])
    return mapped


def extract_hook(post_text: str) -> str:
    """
    Extrai a primeira linha não-vazia do post (o hook).
    """
    lines = [l.strip() for l in post_text.strip().split('\n') if l.strip()]
    return lines[0] if lines else ""


# =============================================================================
# VALIDAÇÕES DETERMINÍSTICAS
# =============================================================================

def validate_post(post_text: str) -> dict:
    """
    Valida o post antes de salvar. Retorna dict com status e avisos.
    """
    warnings = []
    word_count = len(post_text.split())

    # Contagem de palavras
    if word_count < 100:
        warnings.append(f"⚠️ Post muito curto ({word_count} palavras). Mínimo recomendado: 150.")
    elif word_count > 500:
        warnings.append(f"⚠️ Post muito longo ({word_count} palavras). Máximo recomendado: 500.")

    # Links no corpo
    urls = re.findall(r'https?://\S+', post_text)
    if urls:
        warnings.append(f"⚠️ Link detectado no corpo: {urls[0]}. Mover para primeiro comentário.")

    # Hashtags
    hashtags = re.findall(r'#\w+', post_text)
    if len(hashtags) == 0:
        warnings.append("⚠️ Nenhuma hashtag encontrada. Adicionar 3-5.")
    elif len(hashtags) > 5:
        warnings.append(f"⚠️ Muitas hashtags ({len(hashtags)}). Máximo: 5.")

    # Hook truncado
    lines = [l for l in post_text.strip().split('\n') if l.strip()]
    if lines and len(lines[0].split()) > 20:
        warnings.append("⚠️ Primeira linha muito longa. Hook deve funcionar truncado.")

    return {
        "valid": len(warnings) == 0,
        "word_count": word_count,
        "hashtag_count": len(hashtags),
        "warnings": warnings,
    }


# =============================================================================
# TEMPLATE DE CONTEÚDO DA PÁGINA (corpo da entry no banco)
# =============================================================================

def build_page_content(post_text: str, raciocinio: str) -> str:
    """
    Gera o conteúdo Markdown que vai no corpo da página do banco.
    Os metadados (estilo, tema, status etc.) ficam nas properties do banco,
    NÃO no conteúdo da página — evita duplicação.
    """
    content = f"""## Post — Pronto para copiar

{post_text}

---

## Raciocínio Estratégico

{raciocinio}

---

## Checklist Pré-Publicação

- [ ] Hook captura atenção em ~2s e funciona truncado?
- [ ] Parágrafos curtos e escanáveis?
- [ ] Valor claro e tom B2B adequado?
- [ ] CTA com pergunta genuína?
- [ ] Sem link no corpo?
- [ ] 3–5 hashtags?
- [ ] Reforça expertise de Cristiano?
- [ ] Publicado no horário ideal?
- [ ] Primeiros 60 min: respondeu todos os comentários?

---

## Métricas Pós-Publicação

*Preencha as métricas nas properties do banco após 24-48h.*
"""
    return content


# =============================================================================
# MONTAGEM DO PAYLOAD COMPLETO
# =============================================================================

def build_notion_payload(
    titulo: str,
    post_text: str,
    estilo_skill: str,
    tema: str,
    objetivo: str,
    raciocinio: str,
    horario: str,
    data_post: str | None = None,
) -> dict:
    """
    Monta o payload completo para Notion:notion-create-pages.

    Args:
        titulo: Título curto do post (ex: "Agent Skills e a nova arquitetura de agentes")
        post_text: Texto completo do post
        estilo_skill: Nome do estilo usado na skill (ex: "Técnico / Especialista")
        tema: Tema do post — deve ser uma das opções do banco
        objetivo: Objetivo do post (texto livre)
        raciocinio: Raciocínio estratégico
        horario: Horário sugerido (texto livre)
        data_post: Data do post em ISO-8601 (default: hoje)

    Returns:
        dict pronto para ser usado como argumento do Notion:notion-create-pages
    """
    if data_post is None:
        data_post = datetime.now().strftime("%Y-%m-%d")

    # Mapear estilo da skill para opção do banco
    estilo_banco = ESTILO_MAP.get(estilo_skill, "Técnico / Especialista")

    # Mapear hashtags
    hashtags_mapped = map_hashtags(post_text)

    # Extrair hook
    hook = extract_hook(post_text)

    # Montar properties
    properties = {
        "Título": titulo,
        "Status": "Rascunho",
        "Estilo da escrita": estilo_banco,
        "Tema": tema,
        "Objetivo": objetivo,
        "Hook / 1ª linha": hook,
        "Horário sugerido": horario,
        "Hashtags": json.dumps(hashtags_mapped),
        "date:Data do post:start": data_post,
        "date:Data do post:is_datetime": 0,
        "Notas": raciocinio,
    }

    # Montar conteúdo da página
    content = build_page_content(post_text, raciocinio)

    return {
        "parent": {
            "type": "data_source_id",
            "data_source_id": NOTION_DATA_SOURCE_ID,
        },
        "pages": [
            {
                "properties": properties,
                "content": content,
                "icon": "📝",
            }
        ],
    }


# =============================================================================
# INSTRUÇÕES PARA O CLAUDE (passo a passo determinístico)
# =============================================================================

INSTRUCTIONS = """
## Como salvar o post no banco "Posts do LinkedIn" no Notion

Após gerar o post e o Cristiano aprovar, siga EXATAMENTE estes passos:

### Passo 1 — Executar validações
Rode este script com o texto do post:

```python
from scripts.save_to_notion import validate_post
result = validate_post(post_text)
```

Se houver warnings, corrija antes de prosseguir.

### Passo 2 — Montar o payload
Rode:

```python
from scripts.save_to_notion import build_notion_payload
payload = build_notion_payload(
    titulo="<título curto do post>",
    post_text="<texto completo do post>",
    estilo_skill="<estilo usado na skill>",
    tema="<tema do banco>",
    objetivo="<objetivo do post>",
    raciocinio="<raciocínio estratégico>",
    horario="<horário sugerido>",
)
```

O payload retornado contém parent, pages, properties e content prontos.

### Passo 3 — Criar a página no Notion
Use `Notion:notion-create-pages` passando:
- `parent`: payload["parent"]
- `pages`: payload["pages"]

### Passo 4 — Confirmar
Informe ao Cristiano:
- ✅ Post salvo no banco "Posts do LinkedIn"
- 📋 Título e status (Rascunho)
- 💡 Campos de métricas ficam vazios — preencher após publicação

### Mapeamento de estilos (Skill → Banco)
A skill tem 14 estilos + 4 híbridos, mas o banco tem 5 categorias.
O script mapeia automaticamente via ESTILO_MAP:
- Professoral, Simplista Conciso, Simplista + Técnico → "Educacional / How-to"
- Técnico / Especialista, Data-driven → "Técnico / Especialista"
- Storytelling, Mentor, Confessional, Inspiracional, Storytelling + Mentor → "Storytelling / Pessoal"
- Visionário, Analítico, Mini-ensaio → "Estratégico / Liderança"
- Cut Through, Opinionado, Contrarian, Cut Through + Analítico, Contrarian + Data-driven → "Opinião / Provocativo"

### Mapeamento de hashtags (Post → Banco)
O banco aceita apenas estas hashtags no multi_select:
AgenticAI, AIArchitecture, TransformacaoDigital, ThoughtLeadership, #Claude, #AgentSkills

O script extrai do post e mapeia automaticamente via HASHTAG_MAP.
Hashtags que não estão no banco são ignoradas.

### Campos de métricas (pós-publicação)
Estes campos NÃO são preenchidos na criação:
- Link do post, Exibições, Reações, Comentários, Compartilhamentos, Cliques, Interações
- Taxa de engajamento (%) é fórmula automática

O Cristiano preenche manualmente após 24-48h da publicação.
"""


# =============================================================================
# TESTE LOCAL
# =============================================================================

if __name__ == "__main__":
    sample_post = """Deep dive: por que Agent Skills estão redefinindo a arquitetura de agentes de IA

Imagina dar um playbook para um agente de IA.

Não um prompt solto. Um playbook completo: com instruções, contexto, exemplos e scripts executáveis.

#AgenticAI #AIArchitecture #TransformacaoDigital #ThoughtLeadership"""

    print("=== VALIDAÇÃO ===")
    v = validate_post(sample_post)
    print(json.dumps(v, indent=2, ensure_ascii=False))

    print("\n=== HASHTAGS MAPEADAS ===")
    print(map_hashtags(sample_post))

    print("\n=== HOOK EXTRAÍDO ===")
    print(extract_hook(sample_post))

    print("\n=== PAYLOAD COMPLETO ===")
    payload = build_notion_payload(
        titulo="Agent Skills e a nova arquitetura de agentes",
        post_text=sample_post,
        estilo_skill="Técnico / Especialista",
        tema="Agent Skills",
        objetivo="Educar + posicionar expertise",
        raciocinio="Hook com metáfora do playbook...",
        horario="Terça ou Quarta, 7h-9h",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
