{ nixpkgs ? <nixpkgs>
, poetry2nixSrc ? null }:
let
  pkgs = import nixpkgs {};
  poetry2nix = (
    if poetry2nixSrc != null
    then (pkgs.callPackage poetry2nixSrc {
      inherit pkgs;
    })
    else pkgs.poetry2nix
  );
  python = pkgs.python310;
  projectDir = ./.;
in
{
  app = poetry2nix.mkPoetryApplication {
    inherit python projectDir;
  };
  env = poetry2nix.mkPoetryEnv {
    editablePackageSources = { cferates = ./.; };
    inherit python projectDir ;
  };
}
