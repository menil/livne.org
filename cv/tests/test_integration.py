import json
import os
import subprocess
import sys
import tempfile

SAMPLE_MD = """\
# [REDACTED] Test

Summary line here.

## Experience

### Company Name
*Role description here.*

- Bullet one
- Bullet two
- Bullet three

## Education

- **B.Sc., Computer Science**, University
"""


def _check_file(path: str, magic: bytes, label: str) -> None:
    assert os.path.exists(path), f"{label} output not found: {path}"
    size = os.path.getsize(path)
    assert size > 100, f"{label} output too small ({size} bytes): {path}"
    with open(path, "rb") as f:
        header = f.read(len(magic))
    assert header == magic, f"{label} wrong magic bytes: {header!r}"


def _write_config(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(SCRIPT_DIR, "dist")

CONFIG = {"name": "[REDACTED] [REDACTED]", "email": "[REDACTED_EMAIL]"}


def test_build_pdf():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        md_path = os.path.join(tmp, "test.md")
        _write_config(os.path.join(tmp, "config.json"), CONFIG)
        with open(md_path, "w") as f:
            f.write(SAMPLE_MD)
        result = subprocess.run(
            [sys.executable, "src/pdf/build_pdf.py", md_path],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0, f"build_pdf.py failed: {result.stderr}"
        _check_file(os.path.join(DIST_DIR, "[REDACTED]_[REDACTED]_resume.pdf"), b"%PDF", "PDF")
        os.remove(os.path.join(DIST_DIR, "[REDACTED]_[REDACTED]_resume.pdf"))


def test_build_pdf_public():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        md_path = os.path.join(tmp, "test.md")
        _write_config(os.path.join(tmp, "config.json"), CONFIG)
        with open(md_path, "w") as f:
            f.write(SAMPLE_MD)
        result = subprocess.run(
            [sys.executable, "src/pdf/build_pdf.py", "--public", md_path],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0, f"build_pdf.py --public failed: {result.stderr}"
        _check_file(
            os.path.join(DIST_DIR, "[REDACTED]_[REDACTED]_resume_public.pdf"),
            b"%PDF",
            "PDF-public",
        )
        os.remove(os.path.join(DIST_DIR, "[REDACTED]_[REDACTED]_resume_public.pdf"))


def test_build_docx():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        md_path = os.path.join(tmp, "test.md")
        _write_config(os.path.join(tmp, "config.json"), CONFIG)
        with open(md_path, "w") as f:
            f.write(SAMPLE_MD)
        result = subprocess.run(
            [sys.executable, "src/docx/build_docx.py", md_path],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0, f"build_docx.py failed: {result.stderr}"
        _check_file(os.path.join(DIST_DIR, "[REDACTED]_[REDACTED]_resume.docx"), b"PK", "DOCX")
        os.remove(os.path.join(DIST_DIR, "[REDACTED]_[REDACTED]_resume.docx"))


def test_build_html():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        md_path = os.path.join(tmp, "test.md")
        _write_config(os.path.join(tmp, "config.json"), CONFIG)
        with open(md_path, "w") as f:
            f.write(SAMPLE_MD)
        result = subprocess.run(
            [sys.executable, "src/html/build_html.py", md_path],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0, f"build_html.py failed: {result.stderr}"
        html_path = os.path.join(DIST_DIR, "[REDACTED]_[REDACTED]_resume.html")
        assert os.path.exists(html_path), "HTML output not found"
        size = os.path.getsize(html_path)
        assert size > 100, f"HTML output too small ({size} bytes)"
        with open(html_path) as f:
            assert "<!DOCTYPE html>" in f.read()
        os.remove(html_path)
