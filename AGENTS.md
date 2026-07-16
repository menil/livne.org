# AGENTS.md — Project Conventions for opencode Agents

## Project structure

- `cv/` — Resume source files. See [`cv/README.md`](cv/README.md) for usage.
  - `src/pdf/build_pdf.py` — Main script: reads Markdown, generates a two-page PDF resume via WeasyPrint.
  - `src/docx/build_docx.py` — Script to generate a styled DOCX from Markdown.
  - `src/html/build_html.py` — Script to generate a styled HTML resume from Markdown.
  - `resources/cv.md` — Resume in Markdown.
  - `devenv.{nix,yaml,lock}` — Nix-based dev environment (system libs + Python deps).
  - `.envrc` — direnv auto-activation.
- Root `.gitignore` — standard ignores for generated/cache files.

## Environment

All development and execution happens inside the devenv shell under the `cv/` directory. Run `cd cv && devenv shell` (or `direnv allow` in the `cv/` directory) before using the scripts or running `just` tasks.

## Conventions

- Python 3.x, with static type annotations (checked via `mypy`).
- Shebang is `#!/usr/bin/env python3` — only works inside the devenv shell.
- Scripts accept input via command-line argument, not hard-coded paths.
- Commits must follow [Conventional Commits](https://www.conventionalcommits.org/):
  - Title: `type(scope): subject` (max 72 chars)
  - Body lines: max 72 chars
  - Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
  - Scope (optional): single scope only, chars `[a-z0-9._-]` (no commas)
  - Enforced locally via `.githooks/commit-msg` and in CI.
- Formatting/linting via `just` (run from the `cv/` directory):
  - `just lint` — ruff (Python), shellcheck (shell)
  - `just format` — ruff format + shfmt
  - `just typecheck` — mypy static type checking
  - `just test` — pytest unit and integration tests
  - `just validate` — lint + check-format + typecheck + test
  - Pre-commit hooks and CI all use the same tools/configs.
