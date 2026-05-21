from src.docx import build_docx
from src.html import build_html
from src.pdf import build_pdf


def _all(md: str) -> tuple[str, str, str]:
    return (
        build_pdf.fix_markdown_spacing(md),
        build_docx.fix_markdown_spacing(md),
        build_html.fix_markdown_spacing(md),
    )


def test_implementations_match():
    pdf, docx, html = _all("a\n* b")
    assert pdf == docx == html


def test_no_change_when_already_spaced():
    md = "text\n\n* bullet"
    pdf, docx, html = _all(md)
    assert pdf == md
    assert docx == md
    assert html == md


def test_inserts_blank_line_before_bullet():
    md = "text\n* bullet"
    pdf, docx, html = _all(md)
    assert pdf == "text\n\n* bullet"
    assert docx == "text\n\n* bullet"
    assert html == "text\n\n* bullet"


def test_no_insert_for_first_line():
    md = "* bullet\ntext"
    pdf, docx, html = _all(md)
    assert pdf == md
    assert docx == md
    assert html == md


def test_no_insert_for_consecutive_bullets():
    md = "* one\n* two\n* three"
    pdf, docx, html = _all(md)
    assert pdf == md
    assert docx == md
    assert html == md


def test_inserts_for_multiple_groups():
    md = "text\n* one\ntext2\n* two"
    pdf, docx, html = _all(md)
    assert pdf == "text\n\n* one\ntext2\n\n* two"
    assert docx == "text\n\n* one\ntext2\n\n* two"
    assert html == "text\n\n* one\ntext2\n\n* two"


def test_empty_input():
    pdf, docx, html = _all("")
    assert pdf == ""
    assert docx == ""
    assert html == ""


def test_single_line():
    pdf, docx, html = _all("hello")
    assert pdf == "hello"
    assert docx == "hello"
    assert html == "hello"


def test_blank_line_before_bullet_preserved():
    md = "text\n\n\n* bullet"
    pdf, docx, html = _all(md)
    assert pdf == md
    assert docx == md
    assert html == md
