#!/usr/bin/env python3
"""Assemble the public site from documentation owned by each component."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SITE = ROOT / "site-docs"


def copy_markdown(source: Path, destination: Path, replacements: dict[str, str] | None = None) -> None:
    text = source.read_text(encoding="utf-8")
    text = text.replace("](docs/", "](")
    for original, replacement in (replacements or {}).items():
        text = text.replace(original, replacement)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def copy_component(source_root: Path, destination_name: str, root_replacements: dict[str, str]) -> None:
    destination = SITE / destination_name
    docs = source_root / "docs"
    if not docs.is_dir():
        raise ValueError(f"Documentation directory missing: {docs}")
    shutil.copytree(docs, destination)
    for document in destination.rglob("*.md"):
        copy_markdown(document, document)
    copy_markdown(source_root / "README.md", destination / "index.md", root_replacements)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--operator", type=Path, required=True)
    parser.add_argument("--helm", type=Path, required=True)
    arguments = parser.parse_args()

    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(CONTENT, SITE)

    copy_component(arguments.runtime, "runtime", {})
    copy_component(
        arguments.operator,
        "operator",
        {
            "charts/trussium-operator/README.md": "chart.md",
            "DEVELOPMENT.md": "https://github.com/trussiumhq/trussium-operator/blob/main/DEVELOPMENT.md",
            "ROADMAP.md": "https://github.com/trussiumhq/trussium-operator/blob/main/ROADMAP.md",
            "CONTRIBUTING.md": "https://github.com/trussiumhq/trussium-operator/blob/main/CONTRIBUTING.md",
            "SECURITY.md": "https://github.com/trussiumhq/trussium-operator/blob/main/SECURITY.md",
        },
    )
    copy_markdown(arguments.operator / "charts" / "trussium-operator" / "README.md", SITE / "operator" / "chart.md")
    copy_component(
        arguments.helm,
        "helm",
        {
            "charts/trussium/README.md": "chart.md",
            "CONTRIBUTING.md": "https://github.com/trussiumhq/trussium-helm/blob/main/CONTRIBUTING.md",
        },
    )
    copy_markdown(arguments.helm / "charts" / "trussium" / "README.md", SITE / "helm" / "chart.md")


if __name__ == "__main__":
    main()
