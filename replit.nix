{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python39
    pkgs.python39Packages.aiohttp
    pkgs.python39Packages.flask
    pkgs.python39Packages.discord-py
  ];
}