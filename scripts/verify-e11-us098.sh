#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"

[[ ${E11_US098_FORCE_FAILURE:-0} != 1 ]] || {
  echo "intentional US-098 negative verification fixture" >&2
  exit 1
}

metadata=$(cargo metadata --locked --no-deps --format-version 1)
jq -e '
  [.workspace_members[] as $id | .packages[] | select(.id == $id) | .name]
  == ["harness-cli"]
' <<<"$metadata" >/dev/null
tests/boundary/assert-harness-only-tree.sh
tests/boundary/assert-target-symphony-coverage.sh
tests/boundary/assert-symphony-history-allowlist.sh
tests/installer/assert-install-manifest-links.sh
tests/installer/assert-consumer-changeset-trackable.sh
bash -n scripts/install-harness.sh scripts/build-harness-cli-release.sh
test ! -e scripts/verify-e11-external-gate.sh
git diff --check

echo "US-098 Harness-only repository cleanup verification passed"
