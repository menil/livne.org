{ pkgs, ... }:

{
  packages = with pkgs; [
    fontconfig
    liberation_ttf
    pandoc
    bun
    ruff
    shellcheck
    shfmt
    just
  ];

  env.FONTCONFIG_FILE = "${pkgs.fontconfig.out}/etc/fonts/fonts.conf";

  enterShell = ''
    git config core.hooksPath .githooks 2>/dev/null || true
    if [ ! -d .venv ]; then
      python -m venv .venv
      .venv/bin/pip install -e . -q
    fi
    source .venv/bin/activate
    if [ ! -d node_modules ]; then
      bun install
      bun x puppeteer browsers install chrome
    fi
  '';

  languages.python = {
    enable = true;
    package = pkgs.python3.withPackages (ps: with ps; [
      markdown
      jinja2
      pypandoc
      python-docx
      python-dotenv
      pytest
      pytest-cov
      mypy
      pyyaml
      jsonschema
    ]);
  };
}
