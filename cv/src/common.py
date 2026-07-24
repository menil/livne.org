#!/usr/bin/env python3
"""Shared utilities for CV resume builders (PDF, DOCX, HTML)."""

import os

import jinja2
from dotenv import dotenv_values

ENV_KEYS = {
    "RESUME_NAME": "name",
    "RESUME_EMAIL": "email",
    "RESUME_PHONE": "phone",
    "RESUME_LINKEDIN": "linkedin",
}


def _find_env_file(md_dir: str) -> str | None:
    """Look for .env.local in *md_dir* or its immediate parent."""
    md_dir = os.path.abspath(md_dir)
    for candidate in (md_dir, os.path.dirname(md_dir)):
        path = os.path.join(candidate, ".env.local")
        if os.path.isfile(path):
            return path
    return None


def load_config(md_file: str) -> dict[str, str]:
    """Load PII config from .env.local or environment variables.

    Priority:
      1. .env.local in the markdown file's directory or its parent
      2. Process environment variables (for CI / GitHub Secrets)

    Returns a dict with keys: name, email, phone, linkedin, location.
    """
    env_file = _find_env_file(os.path.dirname(md_file))
    file_vars = dotenv_values(env_file) if env_file else {}

    config: dict[str, str] = {}
    for env_key, dict_key in ENV_KEYS.items():
        value = file_vars.get(env_key) or os.environ.get(env_key)
        if value:
            config[dict_key] = value
    return config


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


def config_output_path(
    md_file: str, config: dict[str, str], ext: str, output_dir: str | None = None
) -> str:
    """Derive output path from config name, falling back to the md filename.

    When config contains a name, the output is ``{slug}_resume.{ext}``
    where *slug* is the lowercased name with spaces replaced by underscores.
    Otherwise the output path mirrors the input path with the extension changed.
    """
    name = config.get("name", "")
    if name:
        slug = name.lower().replace(" ", "_")
        filename = f"{slug}_resume.{ext}"
    else:
        base, _ = os.path.splitext(os.path.basename(md_file))
        filename = f"{base}.{ext}"
    if output_dir is not None:
        return os.path.join(output_dir, filename)
    return os.path.join(os.path.dirname(md_file), filename)
