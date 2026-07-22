#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

if E11_US091_TARGET="$repo_root" E11_US091_FRESH_CLONE="$repo_root" \
    "$repo_root/scripts/verify-e11-us091.sh" >/dev/null 2>&1; then
  echo "US-091 verifier accepted repository-harness as the standalone Symphony product" >&2
  exit 1
fi

echo "US-091 verifier negative fixture passed"
