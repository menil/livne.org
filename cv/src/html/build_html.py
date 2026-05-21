#!/usr/bin/env python3
import json
import os
import re
import sys

import jinja2
import markdown

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config(md_file: str) -> dict[str, str]:
    config_path = os.path.join(os.path.dirname(md_file), "config.json")
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
    return {}


def apply_config(md_content: str, config: dict[str, str]) -> str:
    tpl = jinja2.Template(md_content)
    return tpl.render(**config)


def fix_markdown_spacing(md_content: str) -> str:
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


def transform_html(html: str) -> str:
    html = re.sub(
        r"<h3>(.*?)</h3>\s*<p><em>(.*?)</em></p>",
        r'<div class="company-header">'
        r'<span class="company-name">\1</span>'
        r'<span class="company-desc">\2</span></div>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<p><strong>(.*?)</strong>\s*\|\s*(.*?)</p>",
        '<div class="role-header">'
        r'<span class="role-title">\1</span>'
        r'<span class="role-date">\2</span></div>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(
        r"<li><strong>(.*?)</strong>:\s*(.*?)</li>",
        r'<tr><td class="skill-cat">\1</td><td class="skill-list">\2</td></tr>',
        html,
        flags=re.DOTALL,
    )
    html = re.sub(r"<ul>(\s*<tr>)", r'<table class="skills-table">\1', html)
    html = re.sub(r"(</tr>\s*)</ul>", r"\1</table>", html)
    html = re.sub(
        r'(<h2>Early Career History</h2>\s*)<table class="skills-table">',
        r'\1<table class="skills-table early-career">',
        html,
    )
    html = re.sub(
        r"<h2>Education</h2>\s*<ul>\s*<li>(.*?)</li>\s*</ul>",
        r'<h2>Education</h2>\n<div class="education">\1</div>',
        html,
        flags=re.DOTALL,
    )
    return html


def build_web_html(md_file: str) -> None:
    html_file = md_file.replace(".md", ".html")

    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found!")
        return

    with open(md_file, encoding="utf-8") as f:
        raw_md = f.read()

    config = load_config(md_file)
    raw_md = apply_config(raw_md, config)

    clean_md = fix_markdown_spacing(raw_md)
    html_body = markdown.markdown(clean_md, extensions=["tables", "sane_lists"])
    html_body = transform_html(html_body)

    css_path = os.path.join(_SCRIPT_DIR, "style-web.css")
    with open(css_path, encoding="utf-8") as f:
        css_content = f.read()

    tpl_path = os.path.join(_SCRIPT_DIR, "template.html")
    with open(tpl_path, encoding="utf-8") as f:
        tpl_content = f.read()

    config_name = config.get("name", "[REDACTED] [REDACTED]")
    full_html = jinja2.Template(tpl_content).render(
        title=f"{config_name} - Principal Software Engineer",
        css_content=css_content,
        html_body=html_body,
    )

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Success! Created {html_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_html.py <input.md>")
        sys.exit(1)
    build_web_html(sys.argv[1])
