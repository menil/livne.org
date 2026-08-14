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

import json
import sys
from pathlib import Path
from typing import Any, cast

import jsonschema
import yaml

from src.common import apply_config

_SCHEMA_PATH = Path(__file__).resolve().parent.parent / "resources" / "resume.schema.json"

# Placeholder values used only for validation; chosen to satisfy the schema's
# format checks without introducing real personal data.
DUMMY_CONFIG = {
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "555-000-0000",
    "linkedin": "https://linkedin.com/in/janedoe",
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.validate_resume <input.yaml>")
        sys.exit(1)
    violations = validate_resume(sys.argv[1])
    if violations:
        print("Validation failed:")
        for violation in violations:
            print(f"  - {violation}")
        sys.exit(1)
    print("Resume source is valid JSON Resume.")
