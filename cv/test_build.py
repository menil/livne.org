#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile


def run(input_md: str) -> int:
    tmp = tempfile.mkdtemp(prefix="cv_test_")
    md_path = os.path.join(tmp, "test.md")
    with open(md_path, "w") as f:
        f.write(input_md)

    pdf_path = os.path.join(tmp, "test.pdf")
    docx_path = os.path.join(tmp, "test.docx")

    errors: list[str] = []
    script_dir = os.path.dirname(os.path.abspath(__file__))

    result = subprocess.run(  # noqa: S603
        [sys.executable, "build_pdf.py", md_path],
        capture_output=True,
        text=True,
        cwd=script_dir,
    )
    if result.returncode != 0:
        errors.append(f"build_pdf.py failed: {result.stderr}")
    else:
        _check_file(errors, pdf_path, b"%PDF", "PDF")

    result = subprocess.run(  # noqa: S603
        [sys.executable, "build_docx.py", md_path],
        capture_output=True,
        text=True,
        cwd=script_dir,
    )
    if result.returncode != 0:
        errors.append(f"build_docx.py failed: {result.stderr}")
    else:
        _check_file(errors, docx_path, b"PK", "DOCX")

    for err in errors:
        print(err, file=sys.stderr)

    _cleanup(tmp)
    return 1 if errors else 0


def _check_file(errors: list[str], path: str, magic: bytes, label: str) -> None:
    if not os.path.exists(path):
        errors.append(f"{label} output not found: {path}")
        return
    size = os.path.getsize(path)
    if size < 100:
        errors.append(f"{label} output too small ({size} bytes): {path}")
        return
    with open(path, "rb") as f:
        header = f.read(len(magic))
    if header != magic:
        errors.append(f"{label} output has wrong magic bytes: {header!r}")


def _cleanup(tmp: str) -> None:
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)


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


if __name__ == "__main__":
    sys.exit(run(SAMPLE_MD))
