# Resume PDF, DOCX, HTML & MD Builder

[![CI](https://github.com/menil/livne.org/actions/workflows/build.yml/badge.svg)](https://github.com/menil/livne.org/actions/workflows/build.yml)
[![Python](https://img.shields.io/badge/python-3.13-blue?logo=python)](https://www.python.org)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000)](https://docs.astral.sh/ruff)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](.coveragerc)
[![License](https://img.shields.io/github/license/menil/livne.org)](../LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/menil/livne.org)](https://github.com/menil/livne.org/commits/main)

Builds a polished PDF, DOCX, HTML, and Markdown resume from a single structured YAML database using WeasyPrint, Pandoc, and Jinja2.

## Pipeline Flow

```
                      +-------------------+
                      |   .env.local /    |  <-- PII Configuration
                      |   Environment     |
                      +---------+---------+
                                |
                                v
+------------------+  +---------+---------+
|  resources/      |  |  src/common.py    |  <-- Loads config &
|  cv.yaml         +->|                   |      derives output filenames
|  (JSON Resume)   |  +---------+---------+
+------------------+            |
                                |
                                v
                     +--------------------+
                     | src/resume_model.py|  <-- Renders PII placeholders,
                     +---------+----------+      groups work by company,
                               |                 splits early career
                               v
                      +--------------------+
                      |src/validate_resume.|  <-- Official JSON Resume schema
                      |        py          |      check, gated by
                      +---------+----------+      `just build`/`just validate`
                     +---------+----------+
                               |
       +-----------------------+------------------------+
       |                        |                        |
       v                        v                        v
+--------------+         +--------------+         +--------------+
|  src/md/     |         |  src/pdf/    |         |  src/docx/   |  (Also html)
|  render_md.py|         |  build_pdf.py|         |  build_docx.py
+------+-------+         +------+-------+         +------+-------+
       |                        |                        |
       | (Jinja2 Template)      | (WeasyPrint / CSS)     | (Jinja2 + Pandoc)
       v                        v                        v
+--------------+         +--------------+         +--------------+
|  dist/cv.md  |         |  dist/*.pdf  |         |  dist/*.docx |  (Also html)
+--------------+         +--------------+         +--------------+
```

## Prerequisites

- [Nix](https://nixos.org/download) (with flakes enabled)
- [devenv](https://devenv.sh/getting-started/) (`nix profile install nixpkgs#devenv`)
- [direnv](https://direnv.net/) (optional, for auto-activation)

## Setup

1. **Enter the dev environment**:
   ```sh
   devenv shell

   # Or if you have direnv:
   direnv allow
   ```

2. **Configure Personal Details (PII)**:
   To keep your resume source files generic and safe for public repositories, personal details are injected via environment variables:
   * **Locally**: Copy the example configuration to `.env.local` and add your details:
     ```sh
     cp .env.example .env.local
     ```
   * **In CI / CD (GitHub Actions)**: Add the following variables to your repository's **GitHub Actions Secrets**:
     * `RESUME_NAME`
     * `RESUME_EMAIL`
     * `RESUME_PHONE`
     * `RESUME_LINKEDIN`

## Usage

All outputs are generated inside the `dist/` directory. Filenames dynamically incorporate the candidate's name configured via `RESUME_NAME` (e.g., `{slug}_resume.pdf`, `{slug}_resume.docx`, `{slug}_resume.html`), falling back to `cv.{ext}` if no name is configured.

```sh
# Build all outputs (Markdown, PDF, DOCX, HTML) under dist/
just build

# Or run individual scripts directly:
./src/md/render_md.py resources/cv.yaml dist/cv.md          # generates Markdown
./src/pdf/build_pdf.py resources/cv.yaml                    # generates recruiter PDF (includes phone)
./src/pdf/build_pdf.py resources/cv.yaml --public           # generates public PDF (hides phone)
./src/docx/build_docx.py resources/cv.yaml                  # generates DOCX (Word)
./src/html/build_html.py resources/cv.yaml                  # generates HTML (web)
```

## Resume data format

`resources/cv.yaml` follows the [JSON Resume](https://jsonresume.org/schema/) schema in YAML form, with one project-specific convention:

* **Multi-role companies** store one `work` entry per position. `src/resume_model.py` groups consecutive same-company entries into a single company block at render time, and moves positions that ended more than 10 years ago into an "Earlier Career History" section.

Validation (`just validate-resume`) renders PII placeholders with synthetic dummy values and validates `resources/cv.yaml` against the [official JSON Resume schema](https://jsonresume.org/schema/) (vendored at `resources/resume.schema.json`) using `jsonschema`.

The vendored `resources/resume.schema.json` is pinned from [jsonresume/resume-schema](https://github.com/jsonresume/resume-schema) tag `v1.2.1` (commit `50798e359292ad4448d95b3bb0de5f694d6bcc4b`). To update it, diff against the upstream tag and review the changes before committing:

```sh
curl -fsSL https://raw.githubusercontent.com/jsonresume/resume-schema/v1.2.1/schema.json | diff - resources/resume.schema.json
```

Then bump the pinned tag/commit here and in the `$comment` inside `resources/resume.schema.json`.

PII values (`name`, `email`, `phone`, `linkedin`) remain Jinja2 placeholders and are injected from `.env.local` or environment variables at render time. LinkedIn lives under `basics.profiles`.

## Development

All commands run inside `devenv shell`:

| Command | Action |
|---|---|
| `just lint` | Ruff lint + shellcheck |
| `just format` | Ruff format + shfmt |
| `just check-format` | Check formatting without changes |
| `just typecheck` | mypy strict mode on `src/` |
| `just test` | pytest + coverage (threshold: 90%) |
| `just validate-resume` | Schema-validate `resources/cv.yaml` |
| `just build` | Generate Markdown, PDF, DOCX, and HTML (validates first) |
| `just validate` | Run lint + format-check + schema + typecheck + test |

## Project structure

```
cv/
├── dist/                # Generated resume outputs
├── src/
│   ├── pdf/
│   │   ├── build_pdf.py     # WeasyPrint PDF builder (generates private and public PDFs)
│   │   └── style.css        # PDF stylesheet
│   ├── docx/
│   │   └── build_docx.py    # python-docx DOCX builder
│   ├── html/
│   │   ├── build_html.py    # Static HTML resume builder
│   │   ├── style-web.css    # Web stylesheet
│   │   └── template.html    # Jinja2 HTML wrapper template
│   ├── md/
│   │   ├── render_md.py     # Markdown resume builder
│   │   └── template.md      # Jinja2 Markdown template
│   ├── body.html        # Shared Jinja2 template for HTML & PDF layout
│   ├── common.py        # Shared configuration & utility functions
│   ├── resume_model.py  # JSON Resume model: placeholders, grouping, early career
│   ├── validate_resume.py  # Validates cv.yaml against the official JSON Resume schema
│   └── __init__.py
├── resources/
│   ├── cv.yaml             # Resume structured database source (JSON Resume)
│   └── resume.schema.json  # Official JSON Resume schema (vendored)
├── tests/
│   ├── conftest.py      # Shared test fixtures and setup
│   ├── test_build.py    # Unit tests for build scripts
│   ├── test_integration.py  # End-to-end smoke tests
│   ├── test_model.py    # Tests for the resume model
│   ├── test_validate.py # Tests for schema validation
│   ├── test_golden.py   # Byte-identical golden output regression tests
│   ├── test_spacing.py  # Unit tests for markdown spacing
│   └── golden/          # Captured golden outputs (dummy PII)
├── devenv.nix / .yaml / .lock
├── mypy.ini / ruff.toml / .coveragerc
├── Justfile / .envrc / README.md
```
