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
  ];

  env.FONTCONFIG_FILE = "${pkgs.fontconfig.out}/etc/fonts/fonts.conf";

  languages.python = {
    enable = true;
    package = pkgs.python3.withPackages (ps: with ps; [
      weasyprint
      markdown
      pypandoc
      python-docx
    ]);
  };
}
