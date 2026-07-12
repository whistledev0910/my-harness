#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"

[[ ${E11_US097_FORCE_FAILURE:-0} != 1 ]] || {
  echo "intentional US-097 negative verification fixture" >&2
  exit 1
}

scripts/validate-changeset-rebuild.sh
scripts/test-validate-changeset-rebuild.sh
scripts/verify-e11-inventory.sh \
  --require-zero-unknown \
  --require-fk-closure \
  --compare-uid-sets
tests/history/test-e11-epoch-transition.sh
tests/history/assert-no-live-root-changesets.sh
tests/installer/assert-consumer-changeset-trackable.sh
cargo test -p harness-cli --locked
scripts/bin/harness-cli audit
scripts/bin/harness-cli query matrix >/dev/null
scripts/bin/harness-cli query backlog >/dev/null
scripts/bin/harness-cli query tools --summary >/dev/null
git diff --check

echo "US-097 durable history and local state partition verification passed"
