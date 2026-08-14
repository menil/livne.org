#!/usr/bin/env python3
"""Render a Markdown resume from a structured YAML file using PII config."""

import os
import re
import sys

import jinja2

from src import resume_model

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def render_markdown(yaml_file: str, output_file: str) -> None:
    """Read *yaml_file*, resolve PII variables, render MD from template, write to *output_file*."""
    # 1. Load YAML, render placeholders, and prepare the resume model
    data = resume_model.load_resume(yaml_file)

    # 2. Load Markdown template
    tpl_path = os.path.join(_SCRIPT_DIR, "template.md")
    with open(tpl_path, encoding="utf-8") as f:
        tpl_content = f.read()

    # 3. Render template
    rendered_md = jinja2.Template(tpl_content).render(**data)

    # 4. Normalize multiple blank lines (3 or more newlines -> 2 newlines)
    rendered_md = re.sub(r"\n{3,}", "\n\n", rendered_md)
    rendered_md = rendered_md.strip() + "\n"

    # 5. Write output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered_md)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: render_md.py <input.yaml> <output.md>")
        sys.exit(1)
    render_markdown(sys.argv[1], sys.argv[2])
