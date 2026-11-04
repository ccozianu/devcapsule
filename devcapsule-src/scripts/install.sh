#!/bin/sh
# Install DevCapsule from one GitHub release:
#
#   curl -fsSL <release URL>/install.sh | sh
#
# It picks the executable for this computer and, on a Mac, also the Linux
# runtimes its capsules run, which the launcher finds in ~/.local/lib/devcapsule.
# Every file is checked against the release's SHA256SUMS before anything is
# installed. The release workflow writes its own URL over @RELEASE_URL@;
# DEVCAPSULE_RELEASE_URL overrides it, for a mirror or a test. Everything runs
# in main, called on the last line, so a download cut short runs nothing.
set -eu

RELEASE_URL="@RELEASE_URL@"

main() {
  release_url="${DEVCAPSULE_RELEASE_URL:-$RELEASE_URL}"
  case "$release_url" in
    https://* | http://* | file://*) ;;
    *) die "this install.sh names no release; download it from a DevCapsule release" ;;
  esac
  bin_dir="$HOME/.local/bin"
  runtime_dir="$HOME/.local/lib/devcapsule"

  os="$(uname -s)"
  machine="$(uname -m)"
  # A shell under Rosetta reports x86_64 on an Apple Silicon Mac.
  if [ "$os" = Darwin ] && [ "$(sysctl -n hw.optional.arm64 2>/dev/null || true)" = 1 ]; then
    machine=arm64
  fi
  case "$os-$machine" in
    Linux-x86_64 | Linux-amd64) launcher=devcapsule.pex ;;
    Linux-aarch64 | Linux-arm64) launcher=devcapsule-linux-arm64 ;;
    Darwin-arm64) launcher=devcapsule-macos-arm64 ;;
    Darwin-*) die "DevCapsule runs on Apple Silicon Macs only" ;;
    *) die "DevCapsule has no executable for $os $machine" ;;
  esac
  files="$launcher"
  if [ "$os" = Darwin ]; then
    files="$files devcapsule.pex devcapsule-linux-arm64"
  fi

  command -v curl >/dev/null 2>&1 || die "curl is required"
  if command -v sha256sum >/dev/null 2>&1; then
    sha256="sha256sum"
  elif command -v shasum >/dev/null 2>&1; then
    sha256="shasum -a 256"
  else
    die "sha256sum or shasum is required to verify the download"
  fi

  work="$(mktemp -d)"
  trap 'rm -rf "$work"' EXIT
  trap 'exit 1' INT TERM
  cd "$work"

  fetch SHA256SUMS
  for file in $files; do
    echo "Downloading $file"
    fetch "$file"
    verify "$file"
  done

  if [ "$os" = Darwin ]; then
    mkdir -p "$runtime_dir"
    install -m 0755 devcapsule.pex "$runtime_dir/devcapsule-linux-amd64"
    install -m 0755 devcapsule-linux-arm64 "$runtime_dir/devcapsule-linux-arm64"
    echo "Installed the Linux runtimes in $runtime_dir"
  fi
  mkdir -p "$bin_dir"
  install -m 0755 "$launcher" "$bin_dir/devcapsule"
  echo "Installed $bin_dir/devcapsule"
  "$bin_dir/devcapsule" version

  if [ "$os" = Darwin ] && [ -n "${DEVCAPSULE_RUNTIME_PEX:-}" ]; then
    echo "DEVCAPSULE_RUNTIME_PEX is set to $DEVCAPSULE_RUNTIME_PEX, so the launcher uses that instead of"
    echo "$runtime_dir. Remove it from your shell profile to use the runtimes just installed."
  fi
  case ":$PATH:" in
    *":$bin_dir:"*) ;;
    *) echo "Add $bin_dir to PATH in your shell profile to run devcapsule by name." ;;
  esac
}

die() {
  echo "devcapsule install: $*" >&2
  exit 1
}

fetch() {
  curl --fail --silent --show-error --location --output "$1" "$release_url/$1" \
    || die "could not download $release_url/$1"
}

verify() {
  expected="$(awk -v name="$1" '$2 == name || $2 == "*" name { print $1; exit }' SHA256SUMS)"
  [ -n "$expected" ] || die "the release's SHA256SUMS lists no $1"
  actual="$($sha256 "$1" | awk '{ print $1 }')"
  [ "$actual" = "$expected" ] || die "$1 does not match its SHA-256 checksum; nothing was installed"
}

main "$@"
