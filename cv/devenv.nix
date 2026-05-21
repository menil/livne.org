{ pkgs, ... }:

{
  packages = with pkgs; [
    pango
    glib
    cairo
    gdk-pixbuf
    libffi
    fontconfig
    liberation_ttf
    pandoc
    ruff
    shellcheck
    shfmt
    just
  ];

  env.FONTCONFIG_FILE = "${pkgs.fontconfig.out}/etc/fonts/fonts.conf";

  enterShell = ''
    git config core.hooksPath .githooks 2>/dev/null || true
  '';

  languages.python = {
    enable = true;
    package = pkgs.python3.withPackages (ps: with ps; [
      weasyprint
      markdown
      pypandoc
      python-docx
      pytest
    ]);
  };
}
