#!/usr/bin/env python3
"""Shared utilities for CV resume builders (PDF, DOCX, HTML)."""

import json
import os

import jinja2


def load_config(md_file: str) -> dict[str, str]:
    """Load config.json from the same directory as the markdown file.

    Returns an empty dict if no config.json exists.
    """
    config_path = os.path.join(os.path.dirname(md_file), "config.json")
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
    return {}


def apply_config(md_content: str, config: dict[str, str]) -> str:
    """Render Jinja2 placeholders in markdown using values from config."""
    tpl = jinja2.Template(md_content)
    return tpl.render(**config)


def fix_markdown_spacing(md_content: str) -> str:
    """Insert blank lines before bullet lists for proper HTML conversion.

    Without these blank lines, Markdown parsers may not recognize
    bullet lists that immediately follow a paragraph.
    """
    lines = md_content.split("\n")
    out = []
    for i, line in enumerate(lines):
        if (
            line.strip().startswith("* ")
            and i > 0
            and lines[i - 1].strip() != ""
            and not lines[i - 1].strip().startswith("* ")
        ):
            out.append("")
        out.append(line)
    return "\n".join(out)


def config_output_path(md_file: str, config: dict[str, str], ext: str) -> str:
    """Derive output path from config name, falling back to the md filename.

    When config contains a name, the output is ``{slug}_resume.{ext}``
    where *slug* is the lowercased name with spaces replaced by underscores.
    Otherwise the output path mirrors the input path with the extension changed.
    """
    name = config.get("name", "")
    if name:
        slug = name.lower().replace(" ", "_")
        return os.path.join(os.path.dirname(md_file), f"{slug}_resume.{ext}")
    return md_file.replace(".md", f".{ext}")
