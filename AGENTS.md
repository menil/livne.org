# AGENTS.md — Project Conventions for opencode Agents

## Project structure

- `build_pdf.py` — Main script: reads Markdown, generates a two-page PDF resume via WeasyPrint.
- `cv.md` — Sample resume in Markdown.
- `devenv.{nix,yaml}` — Nix-based dev environment declaring system libs (pango, glib, cairo) and Python deps.
- `.envrc` — direnv auto-activation for devenv.

## Environment

All development and execution happens inside the devenv shell. Run `devenv shell` (or `direnv allow`) before using the scripts.

## Conventions

- Python 3.x, no type annotations currently.
- Shebang is `#!/usr/bin/env python3` — only works inside the devenv shell.
- Scripts accept input via command-line argument, not hard-coded paths.
- Formatting: keep existing style (no automatic formatter configured).
