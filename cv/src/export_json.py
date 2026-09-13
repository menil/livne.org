#!/usr/bin/env python3
"""Export the resume JSON with PII placeholders resolved from .env.local."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import yaml

from src.common import apply_config, load_config


def export_json(yaml_file: str, output_file: str, public: bool = False) -> None:
    """Read a JSON Resume YAML file, resolve PII placeholders, and write formatted JSON."""
    config = load_config(yaml_file)
    if not config:
        raise ValueError(
            "Error: no PII config found. Create .env.local or set environment variables."
        )

    with open(yaml_file, encoding="utf-8") as f:
        yaml_content = f.read()

    rendered = apply_config(yaml_content, config)
    data: dict[str, Any] = yaml.safe_load(rendered) or {}

    if public and "basics" in data and isinstance(data["basics"], dict):
        data["basics"].pop("phone", None)

    out_dir = os.path.dirname(output_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Exported {output_file}")


def main() -> None:
    """CLI entry point for exporting JSON Resume data."""
    parser = argparse.ArgumentParser(description="Export resolved JSON Resume data to JSON file.")
    parser.add_argument("input_yaml", help="Path to input YAML file")
    parser.add_argument("output_json", help="Path to output JSON file")
    parser.add_argument(
        "--public",
        action="store_true",
        help="Omit private fields (e.g. phone) for public distribution",
    )

    args = parser.parse_args()
    try:
        export_json(args.input_yaml, args.output_json, public=args.public)
    except Exception as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
