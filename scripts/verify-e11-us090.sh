#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
vault=${E11_US090_VAULT:-/Users/themrb/Documents/personal/e11-migration-artifacts/US-090-20260712}
target=${E11_US090_TARGET:-/Users/themrb/Documents/personal/symphony}
filtered="$vault/filtered"
fresh="$vault/fresh-clone"
bundle=/Users/themrb/Documents/personal/e11-migration-artifacts/US-089-20260711-v8/repository-harness-all-refs.bundle
expected=5db694c8fd43a7d0e34bd9eaf9030d18b856f2b5
tag=symphony-raw-import-20260712

test -f "$vault/owner-go-no-go.txt"
test "$(shasum -a 256 "$vault/owner-go-no-go.txt" | awk '{print $1}')" = e7e9cef61a7d778b4d5ac6eef3cce76630ff5cea61e01067cb8472d48733dd5e
test "$(shasum -a 256 "$bundle" | awk '{print $1}')" = cc6b868567750e139d167e8b674d8016359e0e8c66307446ef15fe6ae4df712d
git bundle verify "$bundle" >/dev/null
cmp "$vault/source-refs-before.txt" "$vault/source-refs-after.txt"

test "$(git -C "$filtered" rev-parse HEAD)" = "$expected"
test "$(git -C "$filtered" rev-parse "$tag^{commit}")" = "$expected"
test "$(shasum -a 256 "$filtered/docs/provenance/e11-filter-paths.txt" | awk '{print $1}')" = e949ed330ace1e6ae80aa0bbe737dce831732d18bef62edf288eb00f8de876cf
"$filtered/tests/migration/assert-filter-scope.sh" --expected-head main --expected-tag "$tag"

remote_now=$(mktemp)
trap 'rm -f "$remote_now"' EXIT
git ls-remote --heads --tags git@github.com:hoangnb24/symphony.git >"$remote_now"
cmp "$vault/target-refs-post-push.txt" "$remote_now"
test "$(awk '$2=="refs/heads/main" {print $1}' "$remote_now")" = "$expected"
test "$(awk -v ref="refs/tags/$tag^{}" '$2==ref {print $1}' "$remote_now")" = "$expected"

for checkout in "$fresh" "$target"; do
  test "$(git -C "$checkout" rev-parse HEAD)" = "$expected"
  test "$(git -C "$checkout" rev-parse "$tag^{commit}")" = "$expected"
  git -C "$checkout" diff --quiet
  git -C "$checkout" diff --cached --quiet
  git -C "$checkout" fsck --full
done

git -C "$repo_root" diff --check
echo "US-090 provenance-preserving bootstrap verification passed"
