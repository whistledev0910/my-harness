#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_evidence="$repo_root/docs/stories/epics/E11-symphony-repository-separation/US-089-separation-boundary-and-frozen-baselines/evidence"
artifact_dir="${E11_US089_ARTIFACT_DIR:?set E11_US089_ARTIFACT_DIR to the external owner-only US-089 vault}"

expect_fail() {
  local name="$1"
  local fixture="$2"
  if E11_US089_EVIDENCE_DIR="$fixture" E11_US089_ARTIFACT_DIR="$artifact_dir" \
      "$repo_root/scripts/verify-e11-us089.sh" >/dev/null 2>&1; then
    echo "negative fixture unexpectedly passed: $name" >&2
    exit 1
  fi
}

E11_US089_EVIDENCE_DIR="$source_evidence" E11_US089_ARTIFACT_DIR="$artifact_dir" \
  "$repo_root/scripts/verify-e11-us089.sh" >/dev/null

temp="$(mktemp -d)"
trap 'rm -rf "$temp"' EXIT

cp -R "$source_evidence" "$temp/empty-checksums"
: >"$temp/empty-checksums/changesets.sha256"
expect_fail empty-checksums "$temp/empty-checksums"

cp -R "$source_evidence" "$temp/missing-operations"
printf '[]\n' >"$temp/missing-operations/changeset-operations.json"
expect_fail missing-operations "$temp/missing-operations"

cp -R "$source_evidence" "$temp/unknown-durable-row"
jq '.unknown_row_count = 1' "$temp/unknown-durable-row/durable-records.json" >"$temp/unknown-durable-row/new.json"
mv "$temp/unknown-durable-row/new.json" "$temp/unknown-durable-row/durable-records.json"
expect_fail unknown-durable-row "$temp/unknown-durable-row"

cp -R "$source_evidence" "$temp/stale-baseline"
jq '.frozen_sha = "0000000000000000000000000000000000000000"' "$temp/stale-baseline/baseline.json" >"$temp/stale-baseline/new.json"
mv "$temp/stale-baseline/new.json" "$temp/stale-baseline/baseline.json"
expect_fail stale-baseline "$temp/stale-baseline"

cp -R "$source_evidence" "$temp/tampered-log-hash"
jq '.commands[0].log_sha256 = "0000000000000000000000000000000000000000000000000000000000000000"' \
  "$temp/tampered-log-hash/baseline.json" >"$temp/tampered-log-hash/new.json"
mv "$temp/tampered-log-hash/new.json" "$temp/tampered-log-hash/baseline.json"
expect_fail tampered-log-hash "$temp/tampered-log-hash"

cp -R "$source_evidence" "$temp/tampered-operation-owner"
jq 'first(to_entries[] | select(.value.owner=="symphony") | .key) as $index | .[$index].owner = "repository-harness"' \
  "$temp/tampered-operation-owner/changeset-operations.json" >"$temp/tampered-operation-owner/new.json"
mv "$temp/tampered-operation-owner/new.json" "$temp/tampered-operation-owner/changeset-operations.json"
expect_fail tampered-operation-owner "$temp/tampered-operation-owner"

cp -R "$source_evidence" "$temp/tampered-reviewed-owner"
jq '(.records[] | select(.table=="intake" and .identity=="128")) |= (.owner="repository-harness" | .disposition="retain")' \
  "$temp/tampered-reviewed-owner/durable-ownership-map.json" >"$temp/tampered-reviewed-owner/new.json"
mv "$temp/tampered-reviewed-owner/new.json" "$temp/tampered-reviewed-owner/durable-ownership-map.json"
expect_fail tampered-reviewed-owner "$temp/tampered-reviewed-owner"

cp -R "$source_evidence" "$temp/empty-replay-comparison"
printf '{}\n' >"$temp/empty-replay-comparison/replay-comparison.json"
expect_fail empty-replay-comparison "$temp/empty-replay-comparison"

cp -R "$source_evidence" "$temp/truncated-paths"
head -1 "$temp/truncated-paths/paths.tsv" >"$temp/truncated-paths/new.tsv"
mv "$temp/truncated-paths/new.tsv" "$temp/truncated-paths/paths.tsv"
expect_fail truncated-paths "$temp/truncated-paths"

cp -R "$source_evidence" "$temp/truncated-ledger"
head -1 "$temp/truncated-ledger/applied-ledger.tsv" >"$temp/truncated-ledger/new.tsv"
mv "$temp/truncated-ledger/new.tsv" "$temp/truncated-ledger/applied-ledger.tsv"
expect_fail truncated-ledger "$temp/truncated-ledger"

cp -R "$source_evidence" "$temp/missing-reviewed-map"
rm "$temp/missing-reviewed-map/durable-ownership-map.json"
expect_fail missing-reviewed-map "$temp/missing-reviewed-map"

echo "US-089 verifier negative fixtures passed"
