import os
import subprocess
import sys

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

from docx import Document
from src.docx import build_docx
from src.html import build_html
from src.pdf import build_pdf

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SAMPLE_MD = """\
# [REDACTED] [REDACTED]

[REDACTED_EMAIL]

Summary line here.

## Experience

### Company Name
*Role description here.*

**Engineer | 2020-2025**

- Bullet one
"""


def _add_run(paragraph, text):
    run = paragraph.add_run(text)
    return run


# ─── _format_name_header ──────────────────────────────────────


_NAME = "[REDACTED] [REDACTED]"


def test_name_header_title_style():
    doc = Document()
    p = doc.add_paragraph("[REDACTED] [REDACTED]")
    p.style = doc.styles["Title"]
    _add_run(p, "[REDACTED] [REDACTED]")
    assert build_docx._format_name_header(p, _NAME)


def test_name_header_heading1_style():
    doc = Document()
    p = doc.add_paragraph("[REDACTED] [REDACTED] - CEO")
    p.style = doc.styles["Heading 1"]
    _add_run(p, "[REDACTED] [REDACTED] - CEO")
    assert build_docx._format_name_header(p, _NAME)


def test_name_header_no_name():
    doc = Document()
    p = doc.add_paragraph("Not My Name")
    p.style = doc.styles["Title"]
    _add_run(p, "Not My Name")
    assert not build_docx._format_name_header(p, _NAME)


def test_name_header_wrong_style_and_long():
    doc = Document()
    p = doc.add_paragraph("[REDACTED] [REDACTED] - Chief Executive Officer")
    p.style = doc.styles["Heading 2"]
    _add_run(p, "[REDACTED] [REDACTED] - Chief Executive Officer")
    assert not build_docx._format_name_header(p, _NAME)


def test_name_header_wrong_style_but_short():
    doc = Document()
    p = doc.add_paragraph("[REDACTED] [REDACTED]")
    p.style = doc.styles["Normal"]
    assert build_docx._format_name_header(p, _NAME)


def test_name_header_formats_correctly():
    doc = Document()
    p = doc.add_paragraph("[REDACTED] [REDACTED]")
    p.style = doc.styles["Title"]
    _add_run(p, "[REDACTED] [REDACTED]")
    assert build_docx._format_name_header(p, _NAME)
    assert p.alignment == WD_ALIGN_PARAGRAPH.CENTER
    assert p.runs[0].font.size == Pt(26)
    assert p.runs[0].font.bold
    assert p.runs[0].font.all_caps


# ─── _format_contact_info ─────────────────────────────────────


def test_contact_info_styling():
    doc = Document()
    p = doc.add_paragraph("test@example.com")
    _add_run(p, "test@example.com")
    build_docx._format_contact_info(p)
    assert p.alignment == WD_ALIGN_PARAGRAPH.CENTER
    assert p.paragraph_format.space_after == Pt(14)
    assert p.runs[0].font.color.rgb == RGBColor(0x55, 0x55, 0x55)


# ─── _format_heading2 ─────────────────────────────────────────


def test_heading2_styling():
    doc = Document()
    p = doc.add_paragraph("Experience")
    _add_run(p, "Experience")
    build_docx._format_heading2(p)
    assert p.runs[0].font.size == Pt(13)
    assert p.runs[0].font.color.rgb == RGBColor(0x29, 0x80, 0xB9)
    assert p.runs[0].font.all_caps
    assert p.runs[0].font.bold
    assert p.paragraph_format.space_before == Pt(16)
    assert p.paragraph_format.space_after == Pt(5)


# ─── _format_heading3 ─────────────────────────────────────────


def test_heading3_styling():
    doc = Document()
    p = doc.add_paragraph("Company Name")
    _add_run(p, "Company Name")
    build_docx._format_heading3(p)
    assert p.runs[0].font.size == Pt(11)
    assert p.runs[0].font.color.rgb == RGBColor(0x1A, 0x25, 0x2F)
    assert p.runs[0].font.bold
    assert p.paragraph_format.space_before == Pt(10)
    assert p.paragraph_format.space_after == Pt(2)


def test_heading3_contacts_page_break():
    doc = Document()
    p = doc.add_paragraph("Contacts+")
    _add_run(p, "Contacts+")
    build_docx._format_heading3(p)
    assert p.paragraph_format.page_break_before


def test_heading3_no_page_break():
    doc = Document()
    p = doc.add_paragraph("Other Company")
    _add_run(p, "Other Company")
    build_docx._format_heading3(p)
    assert not p.paragraph_format.page_break_before


# ─── _format_job_title ────────────────────────────────────────


def test_job_title_styling():
    doc = Document()
    p = doc.add_paragraph("Engineer | 2020-2025")
    _add_run(p, "Engineer | 2020-2025")
    build_docx._format_job_title(p)
    assert p.paragraph_format.space_before == Pt(6)
    assert p.paragraph_format.space_after == Pt(1)


# ─── helpers ────────────────────────────────────────────────


def _write_json(path, data):
    import json

    with open(path, "w") as f:
        json.dump(data, f)


# ─── build_flawless_pdf happy path ────────────────────────────


def test_build_flawless_pdf_happy_path(tmp_path):
    _write_json(tmp_path / "config.json", {"name": "[REDACTED] [REDACTED]", "email": "[REDACTED_EMAIL]"})
    md_file = tmp_path / "test.md"
    md_file.write_text(SAMPLE_MD)
    build_pdf.build_flawless_pdf(str(md_file))
    pdf_file = tmp_path / "[REDACTED]_[REDACTED]_resume.pdf"
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 100
    with open(pdf_file, "rb") as f:
        assert f.read(4) == b"%PDF"


def test_build_flawless_pdf_missing_file(tmp_path, capsys):
    missing = tmp_path / "nonexistent.md"
    build_pdf.build_flawless_pdf(str(missing))
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_build_flawless_pdf_with_config(tmp_path):
    _write_json(tmp_path / "config.json", {"name": "Jane Doe", "email": "j@e.co"})
    (tmp_path / "cv.md").write_text("# {{ name }}\n\n{{ email }}\n\nSummary.")
    build_pdf.build_flawless_pdf(str(tmp_path / "cv.md"))
    assert (tmp_path / "jane_doe_resume.pdf").exists()


def test_build_flawless_pdf_public(tmp_path):
    cfg = {"name": "Jane Doe", "email": "j@e.co", "phone": "555-0000"}
    _write_json(tmp_path / "config.json", cfg)
    (tmp_path / "cv.md").write_text("# {{ name }}\n\n{{ email }} | {{ phone }}\n\nSummary.")
    build_pdf.build_flawless_pdf(str(tmp_path / "cv.md"), public=True)
    assert (tmp_path / "jane_doe_resume_public.pdf").exists()
    # Phone should be stripped from public version
    size_public = (tmp_path / "jane_doe_resume_public.pdf").stat().st_size
    assert size_public > 100


# ─── build_styled_docx happy path ─────────────────────────────


def test_build_styled_docx_happy_path(tmp_path):
    _write_json(tmp_path / "config.json", {"name": "[REDACTED] [REDACTED]", "email": "[REDACTED_EMAIL]"})
    md_file = tmp_path / "test.md"
    md_file.write_text(SAMPLE_MD)
    build_docx.build_styled_docx(str(md_file))
    docx_file = tmp_path / "[REDACTED]_[REDACTED]_resume.docx"
    assert docx_file.exists()
    assert docx_file.stat().st_size > 100
    with open(docx_file, "rb") as f:
        assert f.read(2) == b"PK"


def test_build_styled_docx_missing_file(tmp_path, capsys):
    missing = tmp_path / "nonexistent.md"
    build_docx.build_styled_docx(str(missing))
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_build_styled_docx_with_config(tmp_path):
    _write_json(tmp_path / "config.json", {"name": "Jane Doe", "email": "j@e.co"})
    (tmp_path / "cv.md").write_text("# {{ name }}\n\n{{ email }}\n\nSummary.")
    build_docx.build_styled_docx(str(tmp_path / "cv.md"))
    assert (tmp_path / "jane_doe_resume.docx").exists()


# ─── build_web_html happy path ────────────────────────────────


def test_build_html_happy_path(tmp_path):
    _write_json(tmp_path / "config.json", {"name": "[REDACTED] [REDACTED]", "email": "[REDACTED_EMAIL]"})
    md_file = tmp_path / "test.md"
    md_file.write_text(SAMPLE_MD)
    build_html.build_web_html(str(md_file))
    html_file = tmp_path / "[REDACTED]_[REDACTED]_resume.html"
    assert html_file.exists()
    assert html_file.stat().st_size > 100
    with open(html_file) as f:
        content = f.read()
    assert "<!DOCTYPE html>" in content
    assert "[REDACTED] [REDACTED]" in content
    assert 'href="mailto:[REDACTED_EMAIL]"' in content
    assert "[REDACTED]_[REDACTED]_resume_public.pdf" in content


def test_build_html_missing_file(tmp_path, capsys):
    missing = tmp_path / "nonexistent.md"
    build_html.build_web_html(str(missing))
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_build_html_with_config(tmp_path):
    _write_json(tmp_path / "config.json", {"name": "Jane Doe", "email": "j@e.co"})
    (tmp_path / "cv.md").write_text("# {{ name }}\n\n{{ email }}\n\nSummary.")
    build_html.build_web_html(str(tmp_path / "cv.md"))
    html_file = tmp_path / "jane_doe_resume.html"
    assert html_file.exists()
    with open(html_file) as f:
        content = f.read()
    assert "Jane Doe" in content


# ─── CLI entry points ─────────────────────────────────────────


def test_cli_no_args_pdf():
    result = subprocess.run(
        [sys.executable, "src/pdf/build_pdf.py"],
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR,
    )
    assert result.returncode == 1
    assert "Usage:" in result.stdout


def test_cli_no_args_docx():
    result = subprocess.run(
        [sys.executable, "src/docx/build_docx.py"],
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR,
    )
    assert result.returncode == 1
    assert "Usage:" in result.stdout


def test_cli_no_args_html():
    result = subprocess.run(
        [sys.executable, "src/html/build_html.py"],
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR,
    )
    assert result.returncode == 1
    assert "Usage:" in result.stdout
