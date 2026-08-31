#!/usr/bin/env python3
"""Assemble the public site from documentation owned by each component."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SITE = ROOT / "site-docs"


def copy_markdown(
    source: Path,
    destination: Path,
    replacements: dict[str, str] | None = None,
    source_url: str | None = None,
) -> None:
    text = source.read_text(encoding="utf-8")
    text = text.replace("](docs/", "](")
    if source_url:
        for prefix in (
            "../../docs/",
            "../src/",
            "../examples/",
            "examples/",
            "../templates/",
        ):
            text = re.sub(
                rf"\]\({re.escape(prefix)}([^)#]+)(#[^)]+)?\)",
                lambda match: f"]({source_url}/blob/main/{prefix.lstrip('./')}{match.group(1)}{match.group(2) or ''})",
                text,
            )
    for original, replacement in (replacements or {}).items():
        text = text.replace(original, replacement)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def copy_component(
    source_root: Path,
    destination_name: str,
    root_replacements: dict[str, str],
    source_url: str,
) -> None:
    destination = SITE / destination_name
    docs = source_root / "docs"
    if not docs.is_dir():
        raise ValueError(f"Documentation directory missing: {docs}")
    shutil.copytree(docs, destination)
    # The runtime repository historically uses an uppercase `.MD` extension
    # for its architecture document.  Keep that source filename intact, but
    # publish a lowercase, stable URL in the Pages site.  MkDocs treats the
    # filename as part of the page path, so leaving it uppercase produces a
    # case-sensitive URL that is easy to break when linked from navigation.
    architecture_source = next(
        (path for path in docs.iterdir() if path.name.upper() == "ARCHITECTURE.MD"),
        None,
    )
    architecture_copy = next(
        (path for path in destination.iterdir() if path.name.upper() == "ARCHITECTURE.MD"),
        None,
    )
    if architecture_source is not None and architecture_copy is not None:
        architecture_copy.unlink()
        copy_markdown(architecture_source, destination / "architecture.md")
    for document in destination.rglob("*.md"):
        copy_markdown(document, document, source_url=source_url)
    copy_markdown(source_root / "README.md", destination / "index.md", root_replacements, source_url)


def add_runtime_architecture_overview() -> None:
    """Place the approved conceptual diagram below the runtime page title."""
    document = SITE / "runtime" / "architecture.md"
    text = document.read_text(encoding="utf-8")
    marker = "# Trussium Architecture\n"
    overview = (
        "# Trussium Architecture\n\n"
        "![Trussium architecture overview](../assets/trussium-architecture-overview.png)\n"
    )
    if marker in text and "trussium-architecture-overview.png" not in text:
        document.write_text(text.replace(marker, overview, 1), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--operator", type=Path, required=True)
    parser.add_argument("--helm", type=Path, required=True)
    arguments = parser.parse_args()

    if SITE.exists():
        shutil.rmtree(SITE)
    shutil.copytree(CONTENT, SITE)

    copy_component(
        arguments.runtime,
        "runtime",
        {"ARCHITECTURE.MD": "architecture.md"},
        "https://github.com/trussiumhq/trussium",
    )
    add_runtime_architecture_overview()
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
        "https://github.com/trussiumhq/trussium-operator",
    )
    copy_markdown(
        arguments.operator / "charts" / "trussium-operator" / "README.md",
        SITE / "operator" / "chart.md",
        source_url="https://github.com/trussiumhq/trussium-operator",
    )
    copy_component(
        arguments.helm,
        "helm",
        {
            "charts/trussium/README.md": "chart.md",
            "CONTRIBUTING.md": "https://github.com/trussiumhq/trussium-helm/blob/main/CONTRIBUTING.md",
        },
        "https://github.com/trussiumhq/trussium-helm",
    )
    copy_markdown(
        arguments.helm / "charts" / "trussium" / "README.md",
        SITE / "helm" / "chart.md",
        source_url="https://github.com/trussiumhq/trussium-helm",
    )


if __name__ == "__main__":
    main()
