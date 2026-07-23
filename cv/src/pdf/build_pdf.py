#!/usr/bin/env python3
import os
import re
import sys

import jinja2
import weasyprint
import yaml

from src.common import apply_config, config_output_path, load_config

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def transform_html(html: str) -> str:
    """Legacy regex transformer (retained for backward compatibility and unit tests)."""
    html = re.sub(
        r"<h3>(.*?)</h3>\s*<p><em>(.*?)</em></p>",
        lambda m: (
            '<div class="company-header'
            + (" page-break" if "Contacts+" in m.group(1) else "")
            + '">'
            r'<span class="company-name">' + m.group(1) + "</span>"
            r'<span class="company-desc">' + m.group(2) + "</span></div>"
        ),
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
    html = re.sub(
        r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        r'<a href="mailto:\1">\1</a>',
        html,
    )
    html = re.sub(
        r"(https?://[^\s<]+)",
        lambda m: f'<a href="{m.group(1)}">{re.sub(r"https?://(?:www\.)?", "", m.group(1))}</a>',
        html,
    )
    return html


def build_flawless_pdf(yaml_file: str, public: bool = False, output_dir: str | None = None) -> None:
    if not os.path.exists(yaml_file):
        print(f"Error: {yaml_file} not found!")
        return

    # 1. Load PII config
    config = load_config(yaml_file)

    # 2. Read and parse YAML
    with open(yaml_file, encoding="utf-8") as f:
        yaml_content = f.read()
    rendered_yaml = apply_config(yaml_content, config)
    data = yaml.safe_load(rendered_yaml)

    # 3. Derive output path
    pdf_file = config_output_path(yaml_file, config, "pdf", output_dir=output_dir)
    if public:
        pdf_file = pdf_file.replace(".pdf", "_public.pdf")

    # 4. Prepare data for body rendering (public version hides phone)
    body_data = dict(data)
    body_basics = dict(data["basics"])
    if public:
        body_basics.pop("phone", None)
    body_data["basics"] = body_basics
    body_data["is_pdf"] = True

    # 5. Render html_body from body.html template
    project_root = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
    body_tpl_path = os.path.join(project_root, "src", "body.html")
    with open(body_tpl_path, encoding="utf-8") as f:
        body_tpl = f.read()
    html_body = jinja2.Template(body_tpl).render(**body_data)

    # 6. Read PDF stylesheet
    css_path = os.path.join(_SCRIPT_DIR, "style.css")
    with open(css_path, encoding="utf-8") as f:
        css_content = f.read()

    # 7. Render full HTML wrapper
    full_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
{css_content}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    print("Generating perfectly matched, two-page PDF...")
    weasyprint.HTML(string=full_html).write_pdf(pdf_file)
    print(f"Success! Created {pdf_file}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--public"]
    public = "--public" in sys.argv[1:]
    if len(args) < 1:
        print("Usage: python build_pdf.py [--public] <input.yaml>")
        sys.exit(1)
    _project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _dist_dir = os.path.join(_project_root, "dist")
    os.makedirs(_dist_dir, exist_ok=True)
    build_flawless_pdf(args[0], public=public, output_dir=_dist_dir)
