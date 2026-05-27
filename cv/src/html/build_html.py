#!/usr/bin/env python3
import os
import re
import sys

import jinja2
import markdown

if __name__ == "__main__":
    _project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, _project_root)

from src.common import apply_config, config_output_path, fix_markdown_spacing, load_config

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


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
    html = re.sub(
        r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        r'<a href="mailto:\1">\1</a>',
        html,
    )
    return html


def build_web_html(md_file: str, output_dir: str | None = None) -> None:
    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found!")
        return

    with open(md_file, encoding="utf-8") as f:
        raw_md = f.read()

    config = load_config(md_file)
    linkedin_url = config.get("linkedin", "")
    config.pop("phone", None)
    config.pop("linkedin", None)
    raw_md = apply_config(raw_md, config)

    html_file = config_output_path(md_file, config, "html", output_dir=output_dir)

    clean_md = fix_markdown_spacing(raw_md)
    html_body = markdown.markdown(clean_md, extensions=["tables", "sane_lists"])
    html_body = transform_html(html_body)

    css_path = os.path.join(_SCRIPT_DIR, "style-web.css")
    with open(css_path, encoding="utf-8") as f:
        css_content = f.read()

    tpl_path = os.path.join(_SCRIPT_DIR, "template.html")
    with open(tpl_path, encoding="utf-8") as f:
        tpl_content = f.read()

    config_name = config["name"]
    slug = config_name.lower().replace(" ", "_")
    pdf_url = f"{slug}_resume.pdf"
    email = config.get("email", "")
    full_html = jinja2.Template(tpl_content).render(
        title=f"{config_name} - Principal Software Engineer",
        css_content=css_content,
        html_body=html_body,
        linkedin_url=linkedin_url,
        pdf_url=pdf_url,
        email=email,
    )

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Success! Created {html_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_html.py <input.md>")
        sys.exit(1)
    _project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _dist_dir = os.path.join(_project_root, "dist")
    os.makedirs(_dist_dir, exist_ok=True)
    build_web_html(sys.argv[1], output_dir=_dist_dir)
