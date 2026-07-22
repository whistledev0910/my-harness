#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TARGET_ROOT="${SYMPHONY_ROOT:-$ROOT_DIR/../symphony}"
RECEIPT_DIR="${E11_RECEIPT_DIR:-$ROOT_DIR/docs/stories/epics/E11-symphony-repository-separation/evidence/receipts}"
RECEIPT="${E11_US096_RECEIPT:-$RECEIPT_DIR/US-096.json}"
OWNERSHIP_MAP="$ROOT_DIR/docs/stories/epics/E11-symphony-repository-separation/US-089-separation-boundary-and-frozen-baselines/evidence/path-ownership-map.tsv"

for command in git jq awk; do
  command -v "$command" >/dev/null || { echo "required command is missing: $command" >&2; exit 1; }
done
test -d "$TARGET_ROOT/.git" || { echo "Symphony checkout is missing: $TARGET_ROOT" >&2; exit 1; }
test -f "$RECEIPT" || { echo "US-096 receipt is missing: $RECEIPT" >&2; exit 1; }
test -f "$OWNERSHIP_MAP" || { echo "frozen ownership map is missing: $OWNERSHIP_MAP" >&2; exit 1; }

target_commit="$(jq -er '.target_commit | select(test("^[0-9a-f]{40}$"))' "$RECEIPT")"
test "$(git -C "$TARGET_ROOT" cat-file -t "$target_commit")" = commit

count=0
while IFS= read -r item; do
  test -n "$item" || continue
  if ! git -C "$TARGET_ROOT" cat-file -e "$target_commit:$item"; then
    echo "accepted Symphony commit lacks moved source path: $item" >&2
    exit 1
  fi
  count=$((count + 1))
done < <(awk -F '\t' 'NR > 1 && $5 == "move" { print $1 }' "$OWNERSHIP_MAP" | LC_ALL=C sort)

test "$count" -eq 100 || {
  echo "frozen ownership map must identify exactly 100 moved paths, found $count" >&2
  exit 1
}

# The project-local intake extension was archived as documentation rather than
# copied into either repository's active .codex tree.
git -C "$TARGET_ROOT" cat-file -e \
  "$target_commit:docs/archive/extensions/harness-intake-griller/SKILL.md"
git -C "$TARGET_ROOT" cat-file -e \
  "$target_commit:docs/archive/extensions/harness-intake-griller/agents/openai.yaml"

for story in US-093 US-094 US-095 US-096; do
  receipt="$RECEIPT_DIR/$story.json"
  checksum="$receipt.sha256"
  test -f "$receipt" && test -f "$checksum" || {
    echo "missing receipt or checksum for $story" >&2; exit 1;
  }
  (cd "$(dirname "$receipt")" && shasum -a 256 -c "$(basename "$checksum")" >/dev/null)
  story_commit="$(jq -er '.target_commit | select(test("^[0-9a-f]{40}$"))' "$receipt")"
  if ! git -C "$TARGET_ROOT" merge-base --is-ancestor "$story_commit" "$target_commit"; then
    echo "$story receipt commit is not reachable from accepted US-096 commit" >&2
    exit 1
  fi
done

echo "all 100 moved paths and four receipt commits are owned by Symphony at $target_commit"
