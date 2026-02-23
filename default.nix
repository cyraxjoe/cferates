{ pkgs ? import <nixpkgs> {} }:

let
  inherit (pkgs) lib;

  # Fetch uv2nix and its dependencies
  # We use fetchGit to pin specific commits for reproducibility

  # pyproject.nix:
  # https://github.com/pyproject-nix/pyproject.nix/commits/master
  # 2026-02-19: eb204c6b3335698dec6c7fc1da0ebc3c6df05937
  pyproject-nix-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/pyproject.nix.git";
    rev = "eb204c6b3335698dec6c7fc1da0ebc3c6df05937";
  };

  # uv2nix:
  # https://github.com/pyproject-nix/uv2nix/commits/master
  # 2026-02-19: 51b184e6985f00091dc65d2a6ca36a08a69cafcb
  uv2nix-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/uv2nix.git";
    rev = "51b184e6985f00091dc65d2a6ca36a08a69cafcb";
  };

  # build-system-pkgs:
  # https://github.com/pyproject-nix/build-system-pkgs/commits/master
  # 2026-02-18: 04e9c186e01f0830dad3739088070e4c551191a4
  pyproject-build-systems-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/build-system-pkgs.git";
    rev = "04e9c186e01f0830dad3739088070e4c551191a4";
  };

  # Import the libraries
  pyproject-nix = import pyproject-nix-src { inherit lib; };
  uv2nix = import uv2nix-src { inherit pyproject-nix lib; };
  pyproject-build-systems = import pyproject-build-systems-src { inherit pyproject-nix uv2nix lib; };

  # Load the workspace
  workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

  # Create an overlay from uv.lock
  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  # Construct the python set
  python = pkgs.python3;
  pythonBase = pkgs.callPackage pyproject-nix.build.packages {
    inherit python;
  };

  # Compose the final python set with build systems and the lockfile overlay
  pythonSet = pythonBase.overrideScope (
    lib.composeManyExtensions [
      pyproject-build-systems.overlays.default
      overlay
    ]
  );

  # Create a virtual environment containing the default dependencies
  virtualenv = pythonSet.mkVirtualEnv "cferates-env" workspace.deps.default;

in
pkgs.stdenv.mkDerivation {
  pname = "cferates";
  version = "0.1.0";
  src = ./.;

  nativeBuildInputs = [ pkgs.uv ];
  buildInputs = [ virtualenv ];

  installPhase = ''
    mkdir -p $out
    cp -r ${virtualenv}/* $out/
  '';
}
