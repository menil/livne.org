#!/usr/bin/env python3
import os
import re
import sys

import markdown
import weasyprint

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


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


def build_flawless_pdf(md_file: str) -> None:
    pdf_file = md_file.replace(".md", ".pdf")

    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found!")
        return

    # 1. Read and Auto-Format the Markdown
    with open(md_file, encoding="utf-8") as f:
        raw_md = f.read()

    clean_md = fix_markdown_spacing(raw_md)

    # 2. Convert to pristine HTML
    html_body = markdown.markdown(clean_md, extensions=["tables", "sane_lists"])

    # 3. TRANSLATION LAYER: Convert standard HTML to our Custom Layout
    html_body = transform_html(html_body)

    # 4. Wrap in CSS engine from external file
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

    # 5. Generate the final file
    print("Generating perfectly matched, two-page PDF...")
    weasyprint.HTML(string=full_html).write_pdf(pdf_file)
    print(f"Success! Created {pdf_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_pdf.py <input.md>")
        sys.exit(1)
    build_flawless_pdf(sys.argv[1])
