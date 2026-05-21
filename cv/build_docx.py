#!/usr/bin/env python3
import os
import sys

import pypandoc
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


def fix_markdown_spacing(md_content):
    """
    Automatically injects required blank lines before Markdown lists
    so the parser correctly identifies them as native bullet points.
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


def build_styled_docx(input_file):
    base_output = input_file.replace(".md", "_base.docx")
    final_output = input_file.replace(".md", ".docx")

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print("1. Reading and auto-formatting Markdown...")
    with open(input_file, "r", encoding="utf-8") as f:
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

    # Apply 0.7-inch Margins
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # Set Base Typography to Arial 10.5
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    normal.paragraph_format.line_spacing = 1.3

    # Direct Paragraph Manipulation
    found_name = False
    for paragraph in doc.paragraphs:
        # 1. Format the Main Header ([REDACTED] [REDACTED])
        if "[REDACTED] [REDACTED]" in paragraph.text and (
            paragraph.style.name in ["Title", "Heading 1"] or len(paragraph.text) < 20
        ):
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.font.name = "Arial"
                run.font.size = Pt(26)
                run.font.bold = True
                run.font.all_caps = True
                run.font.color.rgb = RGBColor(0x1A, 0x25, 0x2F)  # Dark Navy
            found_name = True
            continue

        # 2. Format the Contact Info Line directly underneath
        if found_name and "[REDACTED_EMAIL]" in paragraph.text:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.space_after = Pt(18)
            for run in paragraph.runs:
                run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            found_name = False
            continue

        # 3. Format H2 Section Headers (e.g., Professional Experience)
        if paragraph.style.name == "Heading 2":
            for run in paragraph.runs:
                run.font.name = "Arial"
                run.font.size = Pt(13.5)
                run.font.color.rgb = RGBColor(0x29, 0x80, 0xB9)  # Custom Blue
                run.font.all_caps = True
                run.font.bold = True
            paragraph.paragraph_format.space_before = Pt(20)
            paragraph.paragraph_format.space_after = Pt(6)

        # 4. Format H3 Company Headers (e.g., Whitepages)
        if paragraph.style.name == "Heading 3":
            for run in paragraph.runs:
                run.font.name = "Arial"
                run.font.size = Pt(12)
                run.font.color.rgb = RGBColor(0x1A, 0x25, 0x2F)
                run.font.bold = True
            paragraph.paragraph_format.space_before = Pt(12)
            paragraph.paragraph_format.space_after = Pt(2)

            # THE PAGE BREAK FIX: Push Contacts+ to the second page
            if "Contacts+" in paragraph.text:
                paragraph.paragraph_format.page_break_before = True

        # 5. Format Job Titles & Dates
        if "|" in paragraph.text and "20" in paragraph.text and paragraph.style.name == "Normal":
            paragraph.paragraph_format.space_before = Pt(8)
            paragraph.paragraph_format.space_after = Pt(2)

    # Save and clean up
    doc.save(final_output)
    os.remove(base_output)  # Delete the unstyled temp file

    print(f"Success! Final styled document saved as: {final_output}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_docx.py <input.md>")
        sys.exit(1)
    build_styled_docx(sys.argv[1])
