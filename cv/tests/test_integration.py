import subprocess
import sys
import tempfile
from pathlib import Path

from tests.conftest import DEFAULT_CONFIG, SAMPLE_YAML_INTEGRATION

SCRIPT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = SCRIPT_DIR / "dist"

_ENV_KEYS = {
    "name": "RESUME_NAME",
    "email": "RESUME_EMAIL",
    "phone": "RESUME_PHONE",
    "linkedin": "RESUME_LINKEDIN",
    "location": "RESUME_LOCATION",
}


def _write_env(path, data):
    lines = [f"{_ENV_KEYS[k]}={v}" for k, v in data.items() if k in _ENV_KEYS]
    path.write_text("\n".join(lines) + "\n")


def _check_file(path: Path, magic: bytes, label: str) -> None:
    assert path.exists(), f"{label} output not found: {path}"
    size = path.stat().st_size
    assert size > 100, f"{label} output too small ({size} bytes): {path}"
    assert path.read_bytes()[: len(magic)] == magic, f"{label} wrong magic bytes"


def test_build_pdf():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        tmp = Path(tmp)
        _write_env(tmp / ".env.local", DEFAULT_CONFIG)
        (tmp / "test.yaml").write_text(SAMPLE_YAML_INTEGRATION)
        result = subprocess.run(
            [sys.executable, "src/pdf/build_pdf.py", str(tmp / "test.yaml")],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0, f"build_pdf.py failed: {result.stderr}"
        _check_file(DIST_DIR / "john_doe_resume.pdf", b"%PDF", "PDF")
        (DIST_DIR / "john_doe_resume.pdf").unlink()


def test_build_pdf_public():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        tmp = Path(tmp)
        _write_env(tmp / ".env.local", DEFAULT_CONFIG)
        (tmp / "test.yaml").write_text(SAMPLE_YAML_INTEGRATION)
        result = subprocess.run(
            [sys.executable, "src/pdf/build_pdf.py", "--public", str(tmp / "test.yaml")],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0, f"build_pdf.py --public failed: {result.stderr}"
        _check_file(DIST_DIR / "john_doe_resume_public.pdf", b"%PDF", "PDF-public")
        (DIST_DIR / "john_doe_resume_public.pdf").unlink()


def test_build_docx():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        tmp = Path(tmp)
        _write_env(tmp / ".env.local", DEFAULT_CONFIG)
        (tmp / "test.yaml").write_text(SAMPLE_YAML_INTEGRATION)
        result = subprocess.run(
            [sys.executable, "src/docx/build_docx.py", str(tmp / "test.yaml")],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0, f"build_docx.py failed: {result.stderr}"
        _check_file(DIST_DIR / "john_doe_resume.docx", b"PK", "DOCX")
        (DIST_DIR / "john_doe_resume.docx").unlink()


def test_build_html():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        tmp = Path(tmp)
        _write_env(tmp / ".env.local", DEFAULT_CONFIG)
        (tmp / "test.yaml").write_text(SAMPLE_YAML_INTEGRATION)
        result = subprocess.run(
            [sys.executable, "src/html/build_html.py", str(tmp / "test.yaml")],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0, f"build_html.py failed: {result.stderr}"
        html_path = DIST_DIR / "john_doe_resume.html"
        assert html_path.exists(), "HTML output not found"
        assert html_path.stat().st_size > 100, "HTML output too small"
        assert "<!DOCTYPE html>" in html_path.read_text()
        html_path.unlink()
