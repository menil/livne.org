# [REDACTED].org — Resume PDF Builder

Builds a polished PDF resume from Markdown using WeasyPrint.

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

Then build a resume PDF:

```sh
./cv/build_pdf.py cv/cv.md
```

The output will be `cv/cv.pdf`.

## Usage

```sh
./cv/build_pdf.py <input.md>
```

Generates `<input>.pdf` with a two-page polished layout.
