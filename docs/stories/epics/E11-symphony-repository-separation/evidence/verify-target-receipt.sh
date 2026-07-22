#!/usr/bin/env bash
set -euo pipefail
[[ $# -eq 1 ]] || { echo "usage: $0 <US-093|US-094|US-095|US-096>" >&2; exit 2; }
story_id=$1
case "$story_id" in US-093|US-094|US-095|US-096) ;; *) echo "unsupported receipt story: $story_id" >&2; exit 2;; esac
evidence_root=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repo_root=$(git -C "$evidence_root" rev-parse --show-toplevel)
receipt="$evidence_root/receipts/$story_id.json"
checksum="$receipt.sha256"
fail() { echo "historical receipt verification failed for $story_id: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq is required"
test -f "$receipt" || fail "receipt is missing"
test -f "$checksum" || fail "checksum sidecar is missing"
receipt_rel=${receipt#"$repo_root"/}
checksum_rel=${checksum#"$repo_root"/}
git -C "$repo_root" ls-files --error-unmatch -- "$receipt_rel" >/dev/null 2>&1 || fail "receipt is not tracked"
git -C "$repo_root" ls-files --error-unmatch -- "$checksum_rel" >/dev/null 2>&1 || fail "checksum is not tracked"
(cd "$(dirname "$receipt")" && shasum -a 256 -c "$(basename "$checksum")" >/dev/null) || fail "checksum mismatch"
jq -e --arg story "$story_id" '
  .version == 1 and .story_id == $story and
  .target_repository == "git@github.com:hoangnb24/symphony.git" and
  (.target_commit | test("^[0-9a-f]{40}$")) and .protocol_tag == "harness-cli-v0.1.14" and
  (.validation_run | type == "string" and length > 0) and
  (.completed_at | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")) and
  .owner_attestation.type == "reviewed-git-commit" and
  .owner_attestation.repository == .target_repository and .owner_attestation.commit == .target_commit and
  (.owner_attestation.reviewed_by | type == "string" and length > 0) and
  (.owner_attestation.reviewed_at | test("^[0-9]{4}-[0-9]{2}-[0-9]{2}T")) and
  (.release == null or ((.release.tag | length > 0) and (.release.manifest_sha256 | test("^[0-9a-f]{64}$"))))
' "$receipt" >/dev/null || fail "receipt schema or attestation is invalid"
echo "historical target receipt verified: $story_id"
