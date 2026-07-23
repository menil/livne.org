#!/usr/bin/env python3
import os
import sys

import jinja2
import pypandoc
import yaml
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.text.paragraph import Paragraph

from docx import Document
from src.common import apply_config, config_output_path, fix_markdown_spacing, load_config

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _style_name(paragraph: Paragraph) -> str:
    return paragraph.style.name if paragraph.style is not None else ""


def _format_name_header(paragraph: Paragraph, name: str) -> bool:
    if name not in paragraph.text:
        return False
    if _style_name(paragraph) not in ["Title", "Heading 1"] and len(paragraph.text) >= 20:
        return False
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in paragraph.runs:
        run.font.name = "Arial"
        run.font.size = Pt(26)
        run.font.bold = True
        run.font.all_caps = True
        run.font.color.rgb = RGBColor(0x1A, 0x25, 0x2F)
    return True


def _format_contact_info(paragraph: Paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(14)
    for run in paragraph.runs:
        run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)


def _format_heading2(paragraph: Paragraph) -> None:
    for run in paragraph.runs:
        run.font.name = "Arial"
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x29, 0x80, 0xB9)
        run.font.all_caps = True
        run.font.bold = True
    paragraph.paragraph_format.space_before = Pt(16)
    paragraph.paragraph_format.space_after = Pt(5)


def _format_heading3(paragraph: Paragraph) -> None:
    for run in paragraph.runs:
        run.font.name = "Arial"
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x1A, 0x25, 0x2F)
        run.font.bold = True
    paragraph.paragraph_format.space_before = Pt(10)
    paragraph.paragraph_format.space_after = Pt(2)
    if "Contacts+" in paragraph.text:
        paragraph.paragraph_format.page_break_before = True


def _format_job_title(paragraph: Paragraph) -> None:
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(1)


def build_styled_docx(yaml_file: str, output_dir: str | None = None) -> None:
    if not os.path.exists(yaml_file):
        print(f"Error: {yaml_file} not found.")
        return

    # 1. Load PII config
    config = load_config(yaml_file)

    # 2. Read and parse YAML
    with open(yaml_file, encoding="utf-8") as f:
        yaml_content = f.read()
    rendered_yaml = apply_config(yaml_content, config)
    data = yaml.safe_load(rendered_yaml)

    # 3. Derive output paths
    final_output = config_output_path(yaml_file, config, "docx", output_dir=output_dir)
    base_output = final_output.replace(".docx", "_base.docx")

    # 4. Render clean Markdown string in memory
    project_root = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
    tpl_path = os.path.join(project_root, "src", "md", "template.md")
    with open(tpl_path, encoding="utf-8") as f:
        tpl_content = f.read()
    clean_md = jinja2.Template(tpl_content).render(**data)

    # Clean up blank lines in markdown
    import re

    clean_md = re.sub(r"\n{3,}", "\n\n", clean_md).strip() + "\n"
    clean_md = fix_markdown_spacing(clean_md)

    # 5. Convert to baseline DOCX via Pandoc
    pypandoc.convert_text(
        clean_md,
        "docx",
        format="markdown-auto_identifiers",
        outputfile=base_output,
        extra_args=["--standalone"],
    )

    # 6. Apply custom styling
    doc = Document(base_output)

    for section in doc.sections:
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    normal.paragraph_format.line_spacing = 1.25

    cfg_name = config.get("name", data["basics"].get("name", ""))
    cfg_email = config.get("email", data["basics"].get("email", ""))

    found_name = False
    for paragraph in doc.paragraphs:
        if _format_name_header(paragraph, cfg_name):
            found_name = True
            continue

        if found_name and cfg_email in paragraph.text:
            _format_contact_info(paragraph)
            found_name = False
            continue

        if _style_name(paragraph) == "Heading 2":
            _format_heading2(paragraph)

        if _style_name(paragraph) == "Heading 3":
            _format_heading3(paragraph)

        if "|" in paragraph.text and "20" in paragraph.text and _style_name(paragraph) == "Normal":
            _format_job_title(paragraph)

    doc.save(final_output)
    os.remove(base_output)

    print(f"Success! Final styled document saved as: {final_output}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_docx.py <input.yaml>")
        sys.exit(1)
    _project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _dist_dir = os.path.join(_project_root, "dist")
    os.makedirs(_dist_dir, exist_ok=True)
    build_styled_docx(sys.argv[1], output_dir=_dist_dir)
