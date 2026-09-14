"""Integration tests for the resumed CLI pipeline (HTML render and PDF export)."""

import json
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent

SAMPLE_RESUME = {
    "basics": {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "summary": "Principal Architect specializing in scalable backend systems.",
        "location": {
            "city": "Seattle",
            "region": "WA",
        },
        "profiles": [
            {"network": "LinkedIn", "url": "https://linkedin.com/in/janedoe"},
            {"network": "GitHub", "url": "https://github.com/janedoe"},
        ],
    },
    "work": [
        {
            "name": "Tech Corp",
            "position": "Principal Engineer",
            "startDate": "2020",
            "endDate": "2026",
            "description": "High volume data platform.",
            "highlights": [
                "Led distributed systems architecture",
                "Mentored engineering teams across org",
            ],
        },
    ],
    "skills": [{"name": "Languages", "keywords": ["TypeScript", "Python", "Rust"]}],
    "education": [{"studyType": "B.Sc.", "area": "Computer Science", "institution": "UW"}],
}


def _run_resumed(
    subcommand: str,
    input_json: Path,
    output_file: Path,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Execute resumed CLI with standard arguments."""
    cmd = [
        "bun",
        "run",
        "--bun",
        "resumed",
        subcommand,
        str(input_json),
        "-o",
        str(output_file),
        "-t",
        "jsonresume-theme-signal",
    ]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=SCRIPT_DIR,
    )


def test_resumed_render_html(tmp_path: Path):
    input_json = tmp_path / "resume.json"
    output_html = tmp_path / "resume.html"
    input_json.write_text(json.dumps(SAMPLE_RESUME))

    result = _run_resumed("render", input_json, output_html)
    assert result.returncode == 0
    assert output_html.exists()
    content = output_html.read_text(encoding="utf-8")
    assert "Jane Doe" in content
    assert "Principal Architect" in content
    assert "Tech Corp" in content


def test_resumed_export_pdf(tmp_path: Path):
    input_json = tmp_path / "resume.json"
    output_pdf = tmp_path / "resume.pdf"
    input_json.write_text(json.dumps(SAMPLE_RESUME))

    result = _run_resumed(
        "export",
        input_json,
        output_pdf,
        extra_args=[
            "--puppeteer-arg=--no-sandbox",
            "--puppeteer-arg=--disable-setuid-sandbox",
        ],
    )
    assert result.returncode == 0
    assert output_pdf.exists()
    data = output_pdf.read_bytes()
    assert len(data) > 1000
    assert data.startswith(b"%PDF-")
