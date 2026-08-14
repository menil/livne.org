#!/usr/bin/env python3
import os
import re
import sys

import jinja2

from src import resume_model
from src.common import config_output_path

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def transform_html(html: str) -> str:
    """Legacy regex transformer (retained for backward compatibility and unit tests)."""
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


def build_web_html(yaml_file: str, output_dir: str | None = None) -> None:
    if not os.path.exists(yaml_file):
        print(f"Error: {yaml_file} not found!")
        return

    # 1. Load YAML, render placeholders, and prepare the resume model
    data = resume_model.load_resume(yaml_file)
    basics = data["basics"]
    linkedin_url = basics.get("linkedin", "")
    email = basics.get("email", "")
    config_name = basics.get("name", "")

    # 2. Derive output path using name in config
    html_file = config_output_path(yaml_file, {"name": config_name}, "html", output_dir=output_dir)

    # 3. Prepare data for body rendering (web version hides phone and linkedin in header)
    body_data = dict(data)
    body_basics = dict(basics)
    body_basics.pop("phone", None)
    body_basics.pop("linkedin", None)
    body_data["basics"] = body_basics
    body_data["is_pdf"] = False

    # 4. Render html_body from body.html template
    project_root = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
    body_tpl_path = os.path.join(project_root, "src", "body.html")
    with open(body_tpl_path, encoding="utf-8") as f:
        body_tpl = f.read()
    html_body = jinja2.Template(body_tpl).render(**body_data)

    # 5. Read CSS and outer template
    css_path = os.path.join(_SCRIPT_DIR, "style-web.css")
    with open(css_path, encoding="utf-8") as f:
        css_content = f.read()

    tpl_path = os.path.join(_SCRIPT_DIR, "template.html")
    with open(tpl_path, encoding="utf-8") as f:
        tpl_content = f.read()

    slug = config_name.lower().replace(" ", "_")
    pdf_url = f"{slug}_resume.pdf"

    # 6. Render full HTML
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
        print("Usage: python build_html.py <input.yaml>")
        sys.exit(1)
    _project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _dist_dir = os.path.join(_project_root, "dist")
    os.makedirs(_dist_dir, exist_ok=True)
    build_web_html(sys.argv[1], output_dir=_dist_dir)
