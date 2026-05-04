#!/usr/bin/env python3
"""
export_architecture_doc.py — Apoio ao export Markdown → Word/PDF com C4 Mermaid.

  --check          Valida C4 Mermaid obrigatório + regras do brief.
  --list-mermaid   Lista blocos ```mermaid encontrados (primeiras linhas).
  --write-mmd DIR  Extrai cada bloco mermaid para DIR/diagram-NN.mmd (para mmdc / CI).

Uso típico pelo agente:
  python export_architecture_doc.py entrega.md --check
  python export_architecture_doc.py entrega.md --write-mmd ./build/mmd
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from validate_architecture_brief import extract_mermaid_blocks, validate_brief  # noqa: E402


def write_mmd_files(md: str, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i, body in enumerate(extract_mermaid_blocks(md), start=1):
        p = out_dir / f"diagram-{i:02d}.mmd"
        p.write_text(body.strip() + "\n", encoding="utf-8")
        paths.append(p)
    return paths


def main() -> int:
    ap = argparse.ArgumentParser(description="Export helper para Architecture Deliverable (C4 Mermaid).")
    ap.add_argument("markdown", type=Path, help="Arquivo .md preenchido")
    ap.add_argument("--check", action="store_true", help="Valida brief + C4 Mermaid")
    ap.add_argument("--list-mermaid", action="store_true", help="Lista resumo dos blocos mermaid")
    ap.add_argument("--write-mmd", type=Path, metavar="DIR", help="Extrai blocos mermaid para .mmd")
    args = ap.parse_args()

    if not args.markdown.is_file():
        print(f"Arquivo não encontrado: {args.markdown}", file=sys.stderr)
        return 2

    text = args.markdown.read_text(encoding="utf-8")

    if args.list_mermaid:
        blocks = extract_mermaid_blocks(text)
        print(f"Blocos mermaid: {len(blocks)}")
        for i, b in enumerate(blocks, 1):
            head = " ".join(b.splitlines()[:2])
            print(f"  [{i}] {head[:120]}...")
        return 0

    if args.write_mmd:
        paths = write_mmd_files(text, args.write_mmd)
        for p in paths:
            print(str(p))
        return 0

    if args.check:
        ok, issues = validate_brief(text)
        errors = [x for x in issues if x.startswith("[ERRO]")]
        for line in issues:
            print(line)
        print(f"\nok: {ok}")
        return 0 if ok else 1

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
