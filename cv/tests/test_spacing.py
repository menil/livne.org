from src.docx import build_docx
from src.pdf import build_pdf


def _both(md: str) -> tuple[str, str]:
    return (build_pdf.fix_markdown_spacing(md), build_docx.fix_markdown_spacing(md))


def test_implementations_match():
    pdf, docx = _both("a\n* b")
    assert pdf == docx


def test_no_change_when_already_spaced():
    md = "text\n\n* bullet"
    pdf, docx = _both(md)
    assert pdf == md
    assert docx == md


def test_inserts_blank_line_before_bullet():
    md = "text\n* bullet"
    pdf, docx = _both(md)
    assert pdf == "text\n\n* bullet"
    assert docx == "text\n\n* bullet"


def test_no_insert_for_first_line():
    md = "* bullet\ntext"
    pdf, docx = _both(md)
    assert pdf == md
    assert docx == md


def test_no_insert_for_consecutive_bullets():
    md = "* one\n* two\n* three"
    pdf, docx = _both(md)
    assert pdf == md
    assert docx == md


def test_inserts_for_multiple_groups():
    md = "text\n* one\ntext2\n* two"
    pdf, docx = _both(md)
    assert pdf == "text\n\n* one\ntext2\n\n* two"
    assert docx == "text\n\n* one\ntext2\n\n* two"


def test_empty_input():
    pdf, docx = _both("")
    assert pdf == ""
    assert docx == ""


def test_single_line():
    pdf, docx = _both("hello")
    assert pdf == "hello"
    assert docx == "hello"


def test_blank_line_before_bullet_preserved():
    md = "text\n\n\n* bullet"
    pdf, docx = _both(md)
    assert pdf == md
    assert docx == md
