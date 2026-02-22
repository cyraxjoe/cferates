{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = [ pkgs.python3 pkgs.uv ];
  shellHook = ''
    echo "Welcome to the cferates development shell with uv!"
    echo "Run 'uv sync' to install dependencies."
  '';
}
