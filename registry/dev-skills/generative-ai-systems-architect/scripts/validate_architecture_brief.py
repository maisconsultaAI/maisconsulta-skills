#!/usr/bin/env python3
"""
validate_architecture_brief.py — Validação determinística de Architecture Brief (Markdown).

Uso pelo agente:
  1. from validate_architecture_brief import validate_brief
  2. ok, issues = validate_brief(markdown_string)

CLI:
  python validate_architecture_brief.py caminho/para/brief.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Seções de primeiro nível obrigatórias (## Título) — alinhadas ao SKILL.md
REQUIRED_H2 = [
    "Visão e contexto",
    "Stakeholders e personas",
    "Requisitos funcionais (resumo)",
    "Requisitos não funcionais",
    "Domínio e fronteiras (bounded contexts)",
    "Arquitetura lógica e componentes",
    "GenAI: fluxos, dados e avaliação",
    "Segurança, privacidade e conformidade",
    "Operação, observabilidade e SRE",
    "Estratégia cloud-agnostic e portabilidade",
    "Riscos, trade-offs e ADRs propostos",
    "Roadmap e próximos passos",
]

# Palavras-chave mínimas (avisos, não erro fatal)
KEYWORD_HINTS = {
    "GenAI: fluxos, dados e avaliação": [
        "rag",
        "prompt",
        "guardrail",
        "avalia",
        "model",
        "contexto",
        "fallback",
        "agent",
        "golden",
        "métric",
        "rerank",
        "retrieve",
    ],
    "Segurança, privacidade e conformidade": ["threat", "stride", "iam", "encrypt", "pii", "secret", "auditor"],
    "Operação, observabilidade e SRE": ["slo", "sli", "trace", "metric", "log", "runbook", "degrad"],
    "Estratégia cloud-agnostic e portabilidade": ["vendor", "cloud", "adapter", "port", "provider", "agnostic", "interface"],
}

MERMAID_BLOCK = re.compile(r"```mermaid\s*\n(.*?)```", re.IGNORECASE | re.DOTALL)


def extract_mermaid_blocks(md: str) -> List[str]:
    return [b.strip() for b in MERMAID_BLOCK.findall(md)]


def validate_c4_mermaid(md: str) -> List[str]:
    """Exige três blocos ```mermaid distintos com C4Context, C4Container e C4Component."""
    blocks = extract_mermaid_blocks(md)
    if len(blocks) < 3:
        return [
            "[ERRO] Esperados pelo menos 3 blocos ```mermaid (um por diagrama C4: Context, Container, Component)."
        ]
    joined = "\n".join(blocks)
    errs: List[str] = []
    if "C4Context" not in joined:
        errs.append("[ERRO] Obrigatório: diagrama Mermaid **C4Context** (nível 1).")
    if "C4Container" not in joined:
        errs.append("[ERRO] Obrigatório: diagrama Mermaid **C4Container** (nível 2).")
    if "C4Component" not in joined:
        errs.append("[ERRO] Obrigatório: diagrama Mermaid **C4Component** (nível 3).")
    return errs


def _extract_h2_titles(md: str) -> List[str]:
    titles: List[str] = []
    for line in md.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line.strip())
        if m:
            titles.append(m.group(1).strip())
    return titles


def _section_body(md: str, h2_title: str) -> str:
    """Retorna texto da seção até o próximo ## ou fim."""
    pattern = rf"(?ms)^##\s+{re.escape(h2_title)}\s*$(.*?)(?=^##\s+|\Z)"
    m = re.search(pattern, md)
    return m.group(1) if m else ""


def _count_adrs(md: str) -> int:
    return len(re.findall(r"(?mi)^###\s+ADR-\d+", md))


def validate_brief(md: str) -> Tuple[bool, List[str]]:
    """
    Retorna (ok, issues) onde ok é True se não houver erros (somente avisos ok).
    issues: strings prefixadas com [ERRO] ou [AVISO].
    """
    issues: List[str] = []
    h2s = _extract_h2_titles(md)

    for req in REQUIRED_H2:
        if req not in h2s:
            issues.append(f"[ERRO] Seção obrigatória ausente ou título divergente: '## {req}'")

    # Duplicatas
    dup = {t for t in h2s if h2s.count(t) > 1}
    for t in sorted(dup):
        issues.append(f"[ERRO] Seção duplicada: ## {t}")

    # ADRs
    if _count_adrs(md) < 3:
        issues.append("[ERRO] Esperado pelo menos 3 ADRs no formato '### ADR-XXX — título'.")

    issues.extend(validate_c4_mermaid(md))

    # Avisos por seção
    for title, hints in KEYWORD_HINTS.items():
        if title not in h2s:
            continue
        body = _section_body(md, title).lower()
        if not body.strip():
            issues.append(f"[AVISO] Seção '{title}' está vazia ou muito curta.")
            continue
        if not any(h in body for h in hints):
            issues.append(
                f"[AVISO] Seção '{title}' não parece abordar tópicos esperados "
                f"(nenhuma de: {', '.join(hints)})."
            )

    errors = [i for i in issues if i.startswith("[ERRO]")]
    return (len(errors) == 0, issues)


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python validate_architecture_brief.py <arquivo.md>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"Arquivo não encontrado: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    ok, issues = validate_brief(text)
    print(f"ok: {ok}")
    for line in issues:
        print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
