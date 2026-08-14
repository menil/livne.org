"""Golden output regression tests.

The golden files were captured from the pre-migration build pipeline using
dummy PII, so the current renderers must reproduce them byte-for-byte. The
early-career classification is time-dependent (10-year cutoff), so these
tests assume the current calendar year and may need regenerated goldens when
the data or the early-career boundary changes.
"""

import shutil
from pathlib import Path

from src.html.build_html import build_web_html
from src.md.render_md import render_markdown

SCRIPT_DIR = Path(__file__).resolve().parent.parent
GOLDEN_DIR = SCRIPT_DIR / "tests" / "golden"

DUMMY_ENV = {
    "RESUME_NAME": "Jane Doe",
    "RESUME_EMAIL": "jane.doe@example.com",
    "RESUME_PHONE": "+1-555-000-0000",
    "RESUME_LINKEDIN": "https://www.linkedin.com/in/janedoe",
}


def _copy_source(tmp_path: Path) -> Path:
    yaml_file = tmp_path / "cv.yaml"
    shutil.copy(SCRIPT_DIR / "resources" / "cv.yaml", yaml_file)
    return yaml_file


def test_golden_markdown(tmp_path, monkeypatch):
    for key, value in DUMMY_ENV.items():
        monkeypatch.setenv(key, value)
    yaml_file = _copy_source(tmp_path)
    output = tmp_path / "cv.md"
    render_markdown(str(yaml_file), str(output))
    golden = (GOLDEN_DIR / "cv.md").read_text(encoding="utf-8")
    assert output.read_text(encoding="utf-8") == golden


def test_golden_html(tmp_path, monkeypatch):
    for key, value in DUMMY_ENV.items():
        monkeypatch.setenv(key, value)
    yaml_file = _copy_source(tmp_path)
    build_web_html(str(yaml_file), output_dir=str(tmp_path))
    output = tmp_path / "jane_doe_resume.html"
    golden = (GOLDEN_DIR / "cv.html").read_text(encoding="utf-8")
    assert output.read_text(encoding="utf-8") == golden
