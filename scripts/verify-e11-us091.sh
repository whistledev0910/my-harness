#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
target=${E11_US091_TARGET:-/Users/themrb/Documents/personal/symphony}
fresh=${E11_US091_FRESH_CLONE:-/Users/themrb/Documents/personal/e11-migration-artifacts/US-091-20260712-fresh-clone}
expected=61e92c2a73ba3381e0d50b11509ba0eeed079bc9
branch=feature/e11-standalone-workspace

for checkout in "$target" "$fresh"; do
  test "$(git -C "$checkout" rev-parse HEAD)" = "$expected"
  test "$(git -C "$checkout" branch --show-current)" = "$branch"
  test ! -e "$checkout/harness.db"
  git -C "$checkout" diff --quiet
  git -C "$checkout" diff --cached --quiet
done

test "$(git ls-remote git@github.com:hoangnb24/symphony.git "refs/heads/$branch" | awk '{print $1}')" = "$expected"
bash "$fresh/tests/standalone/test-verify-workspace.sh"
bash "$fresh/tests/standalone/verify-workspace.sh"
git -C "$repo_root" diff --check

echo "US-091 standalone Symphony workspace verification passed"
