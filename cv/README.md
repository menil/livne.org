# Resume PDF & DOCX Builder
[![CI](https://github.com/[REDACTED]l/[REDACTED].org/actions/workflows/build.yml/badge.svg)](https://github.com/[REDACTED]l/[REDACTED].org/actions/workflows/build.yml)

Builds a polished PDF and DOCX resume from Markdown using WeasyPrint and Pandoc.

## Prerequisites

- [Nix](https://nixos.org/download) (with flakes enabled)
- [devenv](https://devenv.sh/getting-started/) (`nix profile install nixpkgs#devenv`)
- [direnv](https://direnv.net/) (optional, for auto-activation)

## Setup

```sh
# Enter the dev environment
devenv shell

# Or if you have direnv:
direnv allow
```

## Usage

```sh
# Build PDF and DOCX
just build

# Or run scripts directly
./src/build_pdf.py resources/cv.md    # generates resources/cv.pdf
./src/build_docx.py resources/cv.md   # generates resources/cv.docx
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
| `just build` | Generate PDF and DOCX |
| `just validate` | Run lint + format-check + typecheck + test |

## Project structure

```
cv/
├── src/
│   ├── build_pdf.py     # WeasyPrint PDF builder
│   ├── build_docx.py    # python-docx DOCX builder
│   └── style.css        # PDF stylesheet
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
