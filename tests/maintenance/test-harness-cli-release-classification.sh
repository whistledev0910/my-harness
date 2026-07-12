#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
classifier="$root/scripts/harness-cli-release-changed.sh"
workflow="$root/.github/workflows/post-merge-maintenance.yml"

printf '%s\n' \
  crates/harness-cli/src/main.rs \
  scripts/schema/013-changeset-content-sha.sql \
  scripts/build-harness-cli-release.sh \
  Cargo.toml \
  Cargo.lock |
  "$classifier"

for unrelated in \
  crates/harness-symphony/Cargo.toml \
  docs/HARNESS.md \
  .github/workflows/harness-cli-release.yml; do
  if printf '%s\n' "$unrelated" | "$classifier"; then
    echo "unrelated path triggered Harness CLI publication: $unrelated" >&2
    exit 1
  fi
done

grep -Fq 'scripts/harness-cli-release-changed.sh <<<"$changed_files"' "$workflow"

echo "Harness CLI post-merge release classification tests passed"
