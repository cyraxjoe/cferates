{ pkgs ? import <nixpkgs> {} }:

let
  inherit (pkgs) lib;

  # Fetch uv2nix and its dependencies
  # We use fetchGit to pin specific commits for reproducibility
  pyproject-nix-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/pyproject.nix.git";
    rev = "8b7e28328198f2b7036c044005b630e6d628864d"; # 2024-07-06
  };

  uv2nix-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/uv2nix.git";
    rev = "31945f3c09192c733360b09633e7f411894d01b1"; # 2024-07-06
  };

  pyproject-build-systems-src = builtins.fetchGit {
    url = "https://github.com/pyproject-nix/build-system-pkgs.git";
    rev = "a55a687355152a832320b784a3c26b911855a0f6"; # 2024-07-06
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
