#!/usr/bin/env python3
"""Export the resume YAML with PII placeholders resolved from .env.local."""

import os
import sys

from src.common import apply_config, load_config

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: export_yaml.py <input.yaml> <output.yaml>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    output_file = sys.argv[2]

    config = load_config(yaml_file)
    if not config:
        sys.exit("Error: no PII config found. Create .env.local or set environment variables.")

    with open(yaml_file, encoding="utf-8") as f:
        yaml_content = f.read()

    rendered = apply_config(yaml_content, config)

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"Exported {output_file}")
