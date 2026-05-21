# AGENTS.md — Project Conventions for opencode Agents

## Project structure

- `cv/` — Resume source files. See [`cv/README.md`](cv/README.md) for usage.
  - `build_pdf.py` — Main script: reads Markdown, generates a two-page PDF resume via WeasyPrint.
  - `build_docx.py` — Script to generate a styled DOCX from Markdown.
  - `cv.md` — Resume in Markdown.
  - `devenv.{nix,yaml,lock}` — Nix-based dev environment (system libs + Python deps).
  - `.envrc` — direnv auto-activation.
- Root `.gitignore` — standard ignores for generated/cache files.

## Environment

All development and execution happens inside the devenv shell. Run `devenv shell` (or `direnv allow`) before using the scripts.

## Conventions

- Python 3.x, no type annotations currently.
- Shebang is `#!/usr/bin/env python3` — only works inside the devenv shell.
- Scripts accept input via command-line argument, not hard-coded paths.
- Formatting: keep existing style (no automatic formatter configured).
- Commits must follow [Conventional Commits](https://www.conventionalcommits.org/):
  - Title: `type(scope): subject` (max 72 chars)
  - Body lines: max 72 chars
  - Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
  - Enforced locally via `.githooks/commit-msg` and in CI.
