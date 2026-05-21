# Resume PDF & DOCX Builder

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
./cv/build_pdf.py cv/cv.md   # generates cv/cv.pdf
./cv/build_docx.py cv/cv.md  # generates cv/cv.docx
```
