#!/usr/bin/env python3
import os
import re
import sys

import markdown
import weasyprint

if __name__ == "__main__":
    _project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, _project_root)

from src.common import apply_config, config_output_path, fix_markdown_spacing, load_config

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def transform_html(html: str) -> str:
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
    return html


def build_flawless_pdf(md_file: str, public: bool = False) -> None:
    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found!")
        return

    with open(md_file, encoding="utf-8") as f:
        raw_md = f.read()

    config = load_config(md_file)
    if public:
        config.pop("phone", None)
    raw_md = apply_config(raw_md, config)

    pdf_file = config_output_path(md_file, config, "pdf")
    if public:
        pdf_file = pdf_file.replace(".pdf", "_public.pdf")
    clean_md = fix_markdown_spacing(raw_md)

    html_body = markdown.markdown(clean_md, extensions=["tables", "sane_lists"])
    html_body = transform_html(html_body)

    css_path = os.path.join(_SCRIPT_DIR, "style.css")
    with open(css_path, encoding="utf-8") as f:
        css_content = f.read()

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
        print("Usage: python build_pdf.py [--public] <input.md>")
        sys.exit(1)
    build_flawless_pdf(args[0], public=public)
