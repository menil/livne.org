# Resume PDF, DOCX, HTML & MD Builder

[![CI](https://github.com/menil/livne.org/actions/workflows/build.yml/badge.svg)](https://github.com/menil/livne.org/actions/workflows/build.yml)
[![Python](https://img.shields.io/badge/python-3.13-blue?logo=python)](https://www.python.org)
[![Bun](https://img.shields.io/badge/bun-1.3-black?logo=bun)](https://bun.sh)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000)](https://docs.astral.sh/ruff)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)](.coveragerc)
[![License](https://img.shields.io/github/license/menil/livne.org)](../LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/menil/livne.org)](https://github.com/menil/livne.org/commits/main)

Builds a polished PDF, DOCX, HTML, and Markdown resume from a single structured YAML database using JSON Resume schemas, Signal theme, Puppeteer, Pandoc, and Jinja2.

## Pipeline Flow

```
                      +-------------------+
                      |   .env.local /    |  <-- PII Configuration
                      |   Environment     |
                      +---------+---------+
                                |
                                v
+------------------+  +---------+---------+
|  resources/      |  |  export_json.py   |  <-- Resolves PII & generates
|  cv.yaml         +->|  export_yaml.py   |      dist/resume.json (JSON Resume)
+------------------+  +---------+---------+
                                |
        +-----------------------+-----------------------+
        |                       |                       |
        v                       v                       v
+---------------+       +---------------+       +---------------+
| resumed       |       | resumed       |       | src/docx/ &   |
| render        |       | export        |       | src/md/       |
| (-t signal)   |       | (-t signal)   |       | (DOCX & MD)   |
+-------+-------+       +-------+-------+       +-------+-------+
        |                       |                       |
        v                       v                       v
+---------------+       +---------------+       +---------------+
| dist/*.html   |       | dist/*.pdf    |       | dist/*.docx   |
|               |       |               |       | dist/cv.md    |
+---------------+       +---------------+       +---------------+
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
     * `RESUME_GITHUB`

## Usage

All outputs are generated inside the `dist/` directory. Filenames dynamically incorporate the candidate's name configured via `RESUME_NAME` (e.g., `{slug}_resume.pdf`, `{slug}_resume.docx`, `{slug}_resume.html`), falling back to `resume.{ext}` if no name is configured.

```sh
# Build all outputs (JSON, YAML, HTML, PDF, DOCX, Markdown) under dist/
just build

# Or run individual build targets:
just export-json                                           # exports dist/resume.json & dist/resume_public.json
just build-html                                            # renders HTML via Handlebars theme
just build-pdf                                             # generates PDF via Puppeteer
just build-docx                                            # generates DOCX (Word)
just build-md                                              # generates Markdown
```

## Development

All commands run inside `devenv shell`:

| Command | Action |
|---|---|
| `just lint` | Ruff lint + shellcheck + Biome lint |
| `just format` | Ruff format + shfmt + Biome format |
| `just check-format` | Check formatting without changes |
| `just typecheck` | mypy strict mode on `src/` |
| `just test` | pytest + coverage (threshold: 90%) |
| `just build` | Generate all JSON Resume artifacts under `dist/` |
| `just validate` | Run lint + format-check + schema + typecheck + test |

## Project structure

```
cv/
├── dist/                # Generated resume outputs
├── src/
│   ├── docx/
│   │   └── build_docx.py    # python-docx DOCX builder
│   ├── md/
│   │   ├── render_md.py     # Markdown resume builder
│   │   └── template.md      # Jinja2 Markdown template
│   ├── export_json.py   # JSON Resume exporter
│   ├── export_yaml.py   # PII-resolved YAML exporter
│   ├── resume_model.py  # Resume data loading & processing
│   └── validate_resume.py # Schema validator
├── resources/
│   └── cv.yaml          # Resume structured database source
├── tests/
│   ├── test_build.py    # Python build unit tests
│   ├── test_model.py    # Resume model tests
│   ├── test_resumed.py  # Resumed CLI integration tests (HTML & PDF)
│   └── test_validate.py # Schema validation tests
├── devenv.nix / .yaml / .lock
├── package.json / biome.json
├── mypy.ini / ruff.toml / .coveragerc
├── Justfile / .envrc / README.md
```
