#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DB="${HARNESS_SOURCE_DB:-$ROOT_DIR/harness.db}"
TARGET_DB="${HARNESS_TARGET_DB:-${SYMPHONY_ROOT:-$ROOT_DIR/../symphony}/harness.db}"
CORE_DB="${HARNESS_FRESH_CORE_DB:-}"
CHANGESET_DIR="${HARNESS_CHANGESET_DIR:-$ROOT_DIR/.harness/changesets}"
BASELINE_TSV="${HARNESS_BASELINE_TSV:-$ROOT_DIR/docs/stories/epics/E11-symphony-repository-separation/US-089-separation-boundary-and-frozen-baselines/evidence/changesets.tsv}"
DISPOSITIONS="${HARNESS_DISPOSITIONS:?set HARNESS_DISPOSITIONS to the reviewed row-disposition JSON}"
OUTPUT="${HARNESS_INVENTORY_OUTPUT:-$ROOT_DIR/.harness/runs/e11-us097-inventory.json}"

args=(python3 "$ROOT_DIR/scripts/e11-us097-inventory.py" \
  --source-db "$SOURCE_DB" \
  --target-db "$TARGET_DB" \
  --changeset-dir "$CHANGESET_DIR" \
  --baseline-tsv "$BASELINE_TSV" \
  --dispositions "$DISPOSITIONS" \
  --output "$OUTPUT")
if [[ -n "$CORE_DB" ]]; then
  args+=(--core-db "$CORE_DB")
fi
exec "${args[@]}" "$@"
