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
}


def _write_env(path, data):
    lines = [f"{_ENV_KEYS[k]}={v}" for k, v in data.items() if k in _ENV_KEYS]
    path.write_text("\n".join(lines) + "\n")


def _check_file(path: Path, magic: bytes, label: str) -> None:
    assert path.exists(), f"{label} output not found: {path}"
    size = path.stat().st_size
    assert size > 100, f"{label} output too small ({size} bytes): {path}"
    assert path.read_bytes()[: len(magic)] == magic, f"{label} wrong magic bytes"


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


def test_render_md():
    with tempfile.TemporaryDirectory(prefix="cv_test_") as tmp:
        tmp = Path(tmp)
        _write_env(tmp / ".env.local", DEFAULT_CONFIG)
        (tmp / "test.yaml").write_text(SAMPLE_YAML_INTEGRATION)
        md_path = DIST_DIR / "cv.md"
        result = subprocess.run(
            [sys.executable, "src/md/render_md.py", str(tmp / "test.yaml"), str(md_path)],
            capture_output=True,
            text=True,
            cwd=SCRIPT_DIR,
        )
        assert result.returncode == 0, f"render_md.py failed: {result.stderr}"
        assert md_path.exists()
        assert md_path.stat().st_size > 100
        md_path.unlink()
