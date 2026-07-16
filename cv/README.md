# Resume PDF & DOCX Builder

[![CI](https://github.com/menil/livne.org/actions/workflows/build.yml/badge.svg)](https://github.com/menil/livne.org/actions/workflows/build.yml)
[![Python](https://img.shields.io/badge/python-3.13-blue?logo=python)](https://www.python.org)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000)](https://docs.astral.sh/ruff)
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)](.coveragerc)
[![License](https://img.shields.io/github/license/menil/livne.org)](../LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/menil/livne.org)](https://github.com/menil/livne.org/commits/main)

Builds a polished PDF and DOCX resume from Markdown using WeasyPrint and Pandoc.

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
     * `RESUME_LOCATION`

## Usage

```sh
# Build all outputs (PDF, DOCX, HTML)
just build

# Or run scripts directly
./src/pdf/build_pdf.py resources/cv.md     # generates resources/cv.pdf
./src/docx/build_docx.py resources/cv.md   # generates resources/cv.docx
./src/html/build_html.py resources/cv.md   # generates resources/cv.html
```

## Development

All commands run inside `devenv shell`:

| Command | Action |
|---|---|
| `just lint` | Ruff lint + shellcheck |
| `just format` | Ruff format + shfmt |
| `just check-format` | Check formatting without changes |
| `just typecheck` | mypy strict mode on `src/` |
| `just test` | pytest + coverage (threshold: 90%) |
| `just build` | Generate PDF, DOCX, and HTML |
| `just validate` | Run lint + format-check + typecheck + test |

## Project structure

```
cv/
├── src/
│   ├── pdf/
│   │   ├── build_pdf.py     # WeasyPrint PDF builder
│   │   └── style.css        # PDF stylesheet
│   ├── docx/
│   │   └── build_docx.py    # python-docx DOCX builder
│   ├── html/
│   │   ├── build_html.py    # Static HTML resume builder
│   │   ├── style-web.css    # Web stylesheet
│   │   └── template.html    # Jinja2 HTML wrapper template
│   └── __init__.py
├── resources/
│   └── cv.md            # Resume source
├── tests/
│   ├── test_build.py    # Unit tests for build scripts
│   ├── test_html.py     # Unit tests for HTML transform
│   ├── test_integration.py  # End-to-end smoke tests
│   └── test_spacing.py  # Unit tests for markdown spacing
├── devenv.nix / .yaml / .lock
├── mypy.ini / ruff.toml / .coveragerc
├── Justfile / .envrc / README.md
```
