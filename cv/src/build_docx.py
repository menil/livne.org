#!/usr/bin/env python3
import os
import sys

import pypandoc
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.text.paragraph import Paragraph


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


def _style_name(paragraph: Paragraph) -> str:
    return paragraph.style.name if paragraph.style is not None else ""


def _format_name_header(paragraph: Paragraph) -> bool:
    if "[REDACTED] [REDACTED]" not in paragraph.text:
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


def build_styled_docx(input_file: str) -> None:
    base_output = input_file.replace(".md", "_base.docx")
    final_output = input_file.replace(".md", ".docx")

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print("1. Reading and auto-formatting Markdown...")
    with open(input_file, encoding="utf-8") as f:
        raw_md = f.read()

    clean_md = fix_markdown_spacing(raw_md)

    print("2. Converting to baseline DOCX via Pandoc...")
    pypandoc.convert_text(
        clean_md,
        "docx",
        format="markdown-auto_identifiers",
        outputfile=base_output,
        extra_args=["--standalone"],
    )

    print("3. Applying custom executive styling...")
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

    found_name = False
    for paragraph in doc.paragraphs:
        if _format_name_header(paragraph):
            found_name = True
            continue

        if found_name and "[REDACTED_EMAIL]" in paragraph.text:
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
        print("Usage: python build_docx.py <input.md>")
        sys.exit(1)
    build_styled_docx(sys.argv[1])
