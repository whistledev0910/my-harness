#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
tracked=$(git -C "$root" ls-files -- '.harness/changesets/*.changeset.jsonl')
if [[ -n "$tracked" ]]; then
  echo "repository root still tracks live operational changesets:" >&2
  printf '%s\n' "$tracked" >&2
  exit 1
fi

if [[ -d "$root/.harness/changesets" ]]; then
  count=$(find "$root/.harness/changesets" -mindepth 1 -maxdepth 1 -type f -name '*.changeset.jsonl' -print | wc -l | tr -d ' ')
  if [[ "$count" != 0 ]]; then
    echo "repository root still has active operational changesets on disk" >&2
    exit 1
  fi
fi

echo "repository root has no tracked or active operational changesets"
