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


def test_build_pdf():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        cfg_path = os.path.join(tmp, "config.json")
        _write_config(cfg_path, {"name": "[REDACTED] [REDACTED]", "email": "[REDACTED_EMAIL]"})
        md_path = os.path.join(tmp, "test.md")
        with open(md_path, "w") as f:
            f.write(SAMPLE_MD)

        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            [sys.executable, "src/pdf/build_pdf.py", md_path],
            capture_output=True,
            text=True,
            cwd=script_dir,
        )
        assert result.returncode == 0, f"build_pdf.py failed: {result.stderr}"
        _check_file(os.path.join(tmp, "[REDACTED]_[REDACTED]_resume.pdf"), b"%PDF", "PDF")


def test_build_pdf_public():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        cfg_path = os.path.join(tmp, "config.json")
        _write_config(cfg_path, {"name": "[REDACTED] [REDACTED]", "email": "[REDACTED_EMAIL]"})
        md_path = os.path.join(tmp, "test.md")
        with open(md_path, "w") as f:
            f.write(SAMPLE_MD)

        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            [sys.executable, "src/pdf/build_pdf.py", "--public", md_path],
            capture_output=True,
            text=True,
            cwd=script_dir,
        )
        assert result.returncode == 0, f"build_pdf.py --public failed: {result.stderr}"
        _check_file(os.path.join(tmp, "[REDACTED]_[REDACTED]_resume_public.pdf"), b"%PDF", "PDF-public")


def test_build_docx():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        cfg_path = os.path.join(tmp, "config.json")
        _write_config(cfg_path, {"name": "[REDACTED] [REDACTED]", "email": "[REDACTED_EMAIL]"})
        md_path = os.path.join(tmp, "test.md")
        with open(md_path, "w") as f:
            f.write(SAMPLE_MD)

        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            [sys.executable, "src/docx/build_docx.py", md_path],
            capture_output=True,
            text=True,
            cwd=script_dir,
        )
        assert result.returncode == 0, f"build_docx.py failed: {result.stderr}"
        _check_file(os.path.join(tmp, "[REDACTED]_[REDACTED]_resume.docx"), b"PK", "DOCX")


def test_build_html():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        cfg_path = os.path.join(tmp, "config.json")
        _write_config(cfg_path, {"name": "[REDACTED] [REDACTED]", "email": "[REDACTED_EMAIL]"})
        md_path = os.path.join(tmp, "test.md")
        with open(md_path, "w") as f:
            f.write(SAMPLE_MD)

        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            [sys.executable, "src/html/build_html.py", md_path],
            capture_output=True,
            text=True,
            cwd=script_dir,
        )
        assert result.returncode == 0, f"build_html.py failed: {result.stderr}"
        html_path = os.path.join(tmp, "[REDACTED]_[REDACTED]_resume.html")
        assert os.path.exists(html_path), "HTML output not found"
        size = os.path.getsize(html_path)
        assert size > 100, f"HTML output too small ({size} bytes)"
        with open(html_path) as f:
            assert "<!DOCTYPE html>" in f.read()
