#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

# A process that exits successfully but violates the protocol must never allow
# the story verifier to pass. This proves the wrapper checks behavior rather
# than trusting an executable's exit code.
fake="$tmp/fake-harness-cli"
printf '%s\n' '#!/usr/bin/env bash' 'printf "{}\\n"' >"$fake"
chmod +x "$fake"

if E11_US092_ARTIFACT="$fake" "$repo_root/scripts/verify-e11-us092.sh" >/dev/null 2>&1; then
  echo "US-092 verifier accepted an invalid protocol artifact" >&2
  exit 1
fi

echo "US-092 verifier negative fixture passed"
