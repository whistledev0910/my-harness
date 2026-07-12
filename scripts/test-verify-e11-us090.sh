#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

git -C "$tmp" init -q
git -C "$tmp" config user.name fixture
git -C "$tmp" config user.email fixture@example.invalid
printf 'wrong history\n' >"$tmp/README.md"
git -C "$tmp" add README.md
git -C "$tmp" commit -qm fixture

if E11_US090_TARGET="$tmp" "$repo_root/scripts/verify-e11-us090.sh" >/dev/null 2>&1; then
  echo "US-090 verifier accepted a target with the wrong provenance" >&2
  exit 1
fi

echo "US-090 verifier negative fixture passed"
