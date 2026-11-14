#!/usr/bin/env python3
"""Validate a JSON Resume YAML source against the official JSON Resume schema.

Personal data is kept out of the repository by storing PII values as Jinja2
placeholders (e.g. "{{ name }}"). The official schema has no concept of
placeholders, so before validation they are rendered with the synthetic
values in ``DUMMY_CONFIG`` and the rendered document is validated with
jsonschema (``format: email`` and friends are enforced via a FormatChecker).

The official schema accepts year-only, year-month, and full dates as strings
(its ``iso8601`` definition), so ``startDate: "2020"`` is valid while the
unquoted ``2020`` (a YAML integer) is rejected.

Note that the schema is shape-only: jsonschema's default FormatChecker does
not register ``uri``, so URL formats are not checked.

The schema is vendored at ``resources/resume.schema.json`` from
https://github.com/jsonresume/resume-schema (MIT license).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

import jsonschema
import yaml

from src.common import apply_config
from src.format_resume import resume_yaml_is_canonical

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "resources" / "resume.schema.json"

# Placeholder values used only for validation; chosen to satisfy the schema's
# format checks without introducing real personal data.
DUMMY_CONFIG = {
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "555-000-0000",
    "linkedin": "https://linkedin.com/in/janedoe",
    "github": "https://github.com/janedoe",
}

_FORMAT_CHECKER = jsonschema.FormatChecker()


def _render_placeholders(yaml_text: str) -> str:
    """Render Jinja2 PII placeholders with synthetic validation values."""
    return apply_config(yaml_text, DUMMY_CONFIG)


def _load_schema() -> dict[str, Any]:
    """Load the vendored official JSON Resume schema."""
    with _SCHEMA_PATH.open(encoding="utf-8") as f:
        return cast("dict[str, Any]", json.load(f))


def validate_resume(yaml_file: str) -> list[str]:
    """Validate the JSON Resume source and return a list of violations."""
    with open(yaml_file, encoding="utf-8") as f:
        source = f.read()
    data = yaml.safe_load(_render_placeholders(source))
    if data is None:
        return ["resume source is empty"]
    if not isinstance(data, dict):
        return [f"resume must be a YAML mapping, got {type(data).__name__}"]
    schema = _load_schema()
    errors = list(
        jsonschema.Draft7Validator(schema, format_checker=_FORMAT_CHECKER).iter_errors(data)
    )
    return [f"{'.'.join(map(str, error.absolute_path))}: {error.message}" for error in errors]


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for validating and checking the resume format."""
    parser = argparse.ArgumentParser(description="Validate a resume YAML file.")
    parser.add_argument(
        "path",
        type=Path,
        help="Path to the resume YAML file.",
    )
    parser.add_argument(
        "--check-canonical",
        action="store_true",
        help=("Verify the file is canonically formatted. Exits with 2 if valid but not canonical."),
    )
    args = parser.parse_args(argv)

    violations = validate_resume(str(args.path))
    if violations:
        print("Validation failed:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    if args.check_canonical:
        if not resume_yaml_is_canonical(args.path):
            print(
                f"Resume {args.path} is valid but not canonically formatted.",
                file=sys.stderr,
            )
            return 2
        print("Resume source is valid and canonically formatted.")
    else:
        print("Resume source is valid JSON Resume.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
