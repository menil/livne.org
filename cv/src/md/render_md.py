#!/usr/bin/env python3
"""Render a Markdown resume from a structured YAML file using PII config."""

import os
import sys

import jinja2
import yaml

from src.common import apply_config, load_config

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_markdown(yaml_file: str, output_file: str) -> None:
    """Read *yaml_file*, resolve PII variables, render MD from template, write to *output_file*."""
    # 1. Load PII config
    config = load_config(yaml_file)

    # 2. Read YAML and render Jinja placeholders inside it
    with open(yaml_file, encoding="utf-8") as f:
        yaml_content = f.read()
    rendered_yaml = apply_config(yaml_content, config)

    # 3. Parse YAML to dictionary
    data = yaml.safe_load(rendered_yaml)

    # 4. Load Markdown template
    tpl_path = os.path.join(_SCRIPT_DIR, "template.md")
    with open(tpl_path, encoding="utf-8") as f:
        tpl_content = f.read()

    # 5. Render template
    rendered_md = jinja2.Template(tpl_content).render(**data)

    # 6. Normalize multiple blank lines (3 or more newlines -> 2 newlines)
    import re

    rendered_md = re.sub(r"\n{3,}", "\n\n", rendered_md)
    rendered_md = rendered_md.strip() + "\n"

    # 7. Write output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered_md)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: render_md.py <input.yaml> <output.md>")
        sys.exit(1)
    render_markdown(sys.argv[1], sys.argv[2])
