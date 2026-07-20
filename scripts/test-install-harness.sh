#!/usr/bin/env bash

set -eu

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INSTALLER="$ROOT_DIR/scripts/install-harness.sh"

grep -q 'HARNESS_DIR=.*\.harness' "$INSTALLER"

TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

TARGET="$TEST_DIR/project"
mkdir -p "$TARGET/docs" "$TARGET/scripts"
printf '%s\n' '# Existing project rules' > "$TARGET/AGENTS.md"
printf '%s\n' 'project docs' > "$TARGET/docs/ARCHITECTURE.md"
printf '%s\n' 'project script' > "$TARGET/scripts/build.sh"

HARNESS_SOURCE_DIR="$ROOT_DIR" "$INSTALLER" --directory "$TARGET" --yes
printf '%s\n' '# Rules after Harness' >> "$TARGET/AGENTS.md"
HARNESS_SOURCE_DIR="$ROOT_DIR" "$INSTALLER" --directory "$TARGET" --yes

grep -q '^# Existing project rules$' "$TARGET/AGENTS.md"
grep -q '^# Rules after Harness$' "$TARGET/AGENTS.md"
test "$(grep -c '<!-- HARNESS:BEGIN -->' "$TARGET/AGENTS.md")" -eq 1
test "$(grep -c '<!-- HARNESS:END -->' "$TARGET/AGENTS.md")" -eq 1
grep -q '^project docs$' "$TARGET/docs/ARCHITECTURE.md"
grep -q '^project script$' "$TARGET/scripts/build.sh"
test -f "$TARGET/.harness/README.md"
test -f "$TARGET/.harness/docs/HARNESS.md"
test ! -e "$TARGET/.harness/scripts/bin/harness-cli"

DRY_TARGET="$TEST_DIR/dry-run-project"
mkdir -p "$DRY_TARGET"
HARNESS_SOURCE_DIR="$ROOT_DIR" "$INSTALLER" --directory "$DRY_TARGET" --dry-run --yes
test ! -e "$DRY_TARGET/.harness"
test ! -e "$DRY_TARGET/AGENTS.md"

MALFORMED_TARGET="$TEST_DIR/malformed-project"
mkdir -p "$MALFORMED_TARGET"
printf '%s\n' '<!-- HARNESS:BEGIN -->' 'keep me' > "$MALFORMED_TARGET/AGENTS.md"
if HARNESS_SOURCE_DIR="$ROOT_DIR" "$INSTALLER" --directory "$MALFORMED_TARGET" --yes 2>/dev/null; then
  echo "installer accepted a malformed Harness block" >&2
  exit 1
fi
test ! -e "$MALFORMED_TARGET/.harness"
grep -q '^keep me$' "$MALFORMED_TARGET/AGENTS.md"

echo "installer test passed"
