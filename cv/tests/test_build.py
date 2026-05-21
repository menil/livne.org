import os
import subprocess
import sys

from docx import Document

from src import build_docx, build_pdf

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_name_header_title_style():
    doc = Document()
    p = doc.add_paragraph("[REDACTED] [REDACTED]")
    p.style = doc.styles["Title"]
    assert build_docx._format_name_header(p)


def test_name_header_heading1_style():
    doc = Document()
    p = doc.add_paragraph("[REDACTED] [REDACTED] - CEO")
    p.style = doc.styles["Heading 1"]
    assert build_docx._format_name_header(p)


def test_name_header_no_name():
    doc = Document()
    p = doc.add_paragraph("Not My Name")
    p.style = doc.styles["Title"]
    assert not build_docx._format_name_header(p)


def test_name_header_wrong_style_and_long():
    doc = Document()
    p = doc.add_paragraph("[REDACTED] [REDACTED] - Chief Executive Officer")
    p.style = doc.styles["Heading 2"]
    assert not build_docx._format_name_header(p)


def test_name_header_wrong_style_but_short():
    doc = Document()
    p = doc.add_paragraph("[REDACTED] [REDACTED]")
    p.style = doc.styles["Normal"]
    assert build_docx._format_name_header(p)


def test_build_flawless_pdf_missing_file(tmp_path, capsys):
    missing = tmp_path / "nonexistent.md"
    build_pdf.build_flawless_pdf(str(missing))
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_build_styled_docx_missing_file(tmp_path, capsys):
    missing = tmp_path / "nonexistent.md"
    build_docx.build_styled_docx(str(missing))
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_cli_no_args_pdf():
    result = subprocess.run(
        [sys.executable, "src/build_pdf.py"],
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR,
    )
    assert result.returncode == 1
    assert "Usage:" in result.stdout


def test_cli_no_args_docx():
    result = subprocess.run(
        [sys.executable, "src/build_docx.py"],
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR,
    )
    assert result.returncode == 1
    assert "Usage:" in result.stdout
