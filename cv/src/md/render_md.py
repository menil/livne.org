#!/usr/bin/env python3
"""Render a Markdown template with PII config values."""

import sys

from src.common import apply_config, load_config


def render_markdown(md_file: str, output_file: str) -> None:
    """Read *md_file*, apply config placeholders, write to *output_file*."""
    config = load_config(md_file)
    with open(md_file, encoding="utf-8") as f:
        template = f.read()
    rendered = apply_config(template, config)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: render_md.py <input.md> <output.md>")
        sys.exit(1)
    render_markdown(sys.argv[1], sys.argv[2])
