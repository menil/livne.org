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
  ];

  env.FONTCONFIG_FILE = pkgs.writeText "fonts.conf" ''
    <?xml version="1.0"?>
    <!DOCTYPE fontconfig SYSTEM "fonts.dtd">
    <fontconfig>
      <include ignore_missing="yes">${pkgs.fontconfig.out}/etc/fonts/fonts.conf</include>
      <dir>/System/Library/Fonts</dir>
      <dir>/Library/Fonts</dir>
      <dir>~/.fonts</dir>
      <dir>~/.local/share/fonts</dir>
    </fontconfig>
  '';

  languages.python = {
    enable = true;
    package = pkgs.python3.withPackages (ps: with ps; [
      weasyprint
      markdown
    ]);
  };
}
