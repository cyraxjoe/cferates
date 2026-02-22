{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  pname = "cferates";
  version = "0.1.0";

  src = ./.;

  nativeBuildInputs = [ pkgs.uv pkgs.python3 ];

  # Note: This is a placeholder for uv2nix integration.
  # Without uv2nix or network access, uv sync will fail in restricted build environments.
  buildPhase = ''
    export HOME=$(mktemp -d)
    uv sync --frozen --no-install-project || echo "Warning: uv sync failed (expected without network)"
  '';

  installPhase = ''
    mkdir -p $out
    if [ -d .venv ]; then
      cp -r .venv $out/venv
      mkdir -p $out/bin
      ln -s $out/venv/bin/cferates $out/bin/cferates
    else
      echo "Warning: .venv not found, skipping installation"
    fi
  '';
}
