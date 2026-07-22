#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOL="$ROOT_DIR/scripts/e11-us097-inventory.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/changesets"

sqlite3 "$TMP/source.db" <<'SQL'
PRAGMA foreign_keys=ON;
CREATE TABLE parent (id TEXT PRIMARY KEY, owner TEXT NOT NULL);
CREATE TABLE child (id INTEGER PRIMARY KEY, parent_id TEXT NOT NULL REFERENCES parent(id));
CREATE TABLE intervention (id INTEGER PRIMARY KEY);
CREATE TABLE story_backlog_link (story_id TEXT, backlog_id INTEGER, PRIMARY KEY(story_id, backlog_id));
CREATE TABLE proposal_evidence_link (proposal_key TEXT PRIMARY KEY);
CREATE TABLE audit_evidence_episode (id INTEGER PRIMARY KEY);
CREATE TABLE backlog_outcome_observation (id INTEGER PRIMARY KEY);
CREATE TABLE legacy_evidence_snapshot (id INTEGER PRIMARY KEY);
CREATE TABLE changeset_applied (id TEXT PRIMARY KEY);
CREATE TABLE schema_version (version INTEGER PRIMARY KEY);
INSERT INTO parent VALUES ('core-1','core'),('move-1','symphony');
INSERT INTO child VALUES (7,'core-1');
INSERT INTO schema_version VALUES (13);
SQL
sqlite3 "$TMP/target.db" <<'SQL'
CREATE TABLE parent (id TEXT PRIMARY KEY, owner TEXT NOT NULL);
INSERT INTO parent VALUES ('move-1','symphony'),('native-1','symphony');
SQL
cp "$TMP/source.db" "$TMP/core.db"
sqlite3 "$TMP/core.db" "DELETE FROM parent WHERE id='move-1';"
printf '%s\n' '{"op":"changeset.header","version":1,"run_id":"fixture","base_schema_version":13}' >"$TMP/changesets/base.changeset.jsonl"
hash="$(shasum -a 256 "$TMP/changesets/base.changeset.jsonl" | awk '{print $1}')"
printf '%s\t%s\t%s\t%s\t%s\n' "$TMP/changesets/base.changeset.jsonl" core archive fixture "$hash" >"$TMP/baseline.tsv"

python3 - "$TMP/source.db" "$TMP/dispositions.json" <<'PY'
import importlib.util, json, pathlib, sys
tool = pathlib.Path(sys.argv[0]).resolve().parent / "scripts/e11-us097-inventory.py"
spec = importlib.util.spec_from_file_location("inventory", tool)
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
inventory = module.inventory_database(pathlib.Path(sys.argv[1]))
rows=[]
for table, detail in inventory["tables"].items():
    for identity in detail["identities"]:
        action = "move-target" if identity == 'parent:id="move-1"' else "retain-core"
        rows.append({"table":table,"identity":identity,"action":action,"owner":"fixture","reason":"contract fixture"})
pathlib.Path(sys.argv[2]).write_text(json.dumps({"rows":rows}))
PY

python3 "$TOOL" --source-db "$TMP/source.db" --core-db "$TMP/core.db" --target-db "$TMP/target.db" \
  --changeset-dir "$TMP/changesets" --baseline-tsv "$TMP/baseline.tsv" \
  --dispositions "$TMP/dispositions.json" --output "$TMP/report.json" \
  --require-zero-unknown --require-fk-closure --compare-uid-sets >/dev/null
jq -e '.ok and .read_only and .source.table_count == 10 and .comparison.expected_target_rows == 1' "$TMP/report.json" >/dev/null

# Unknown rows fail closed.
jq '.rows = .rows[:-1]' "$TMP/dispositions.json" >"$TMP/incomplete.json"
if python3 "$TOOL" --source-db "$TMP/source.db" --target-db "$TMP/target.db" \
  --changeset-dir "$TMP/changesets" --baseline-tsv "$TMP/baseline.tsv" \
  --dispositions "$TMP/incomplete.json" --output "$TMP/incomplete-report.json" \
  --require-zero-unknown >/dev/null; then
  echo "inventory accepted an unclassified row" >&2; exit 1
fi

# A broken FK is reported even when SQLite enforcement was disabled by its creator.
cp "$TMP/source.db" "$TMP/broken.db"
sqlite3 "$TMP/broken.db" "PRAGMA foreign_keys=OFF; UPDATE child SET parent_id='missing';"
if python3 "$TOOL" --source-db "$TMP/broken.db" --target-db "$TMP/target.db" \
  --changeset-dir "$TMP/changesets" --baseline-tsv "$TMP/baseline.tsv" \
  --dispositions "$TMP/dispositions.json" --output "$TMP/broken-report.json" \
  --require-fk-closure >/dev/null; then
  echo "inventory accepted broken foreign-key closure" >&2; exit 1
fi

# Baseline mutation is detected by content hash rather than a hard-coded count.
printf '%s\n' '{}' >>"$TMP/changesets/base.changeset.jsonl"
if python3 "$TOOL" --source-db "$TMP/source.db" --target-db "$TMP/target.db" \
  --changeset-dir "$TMP/changesets" --baseline-tsv "$TMP/baseline.tsv" \
  --dispositions "$TMP/dispositions.json" --output "$TMP/hash-report.json" >/dev/null; then
  echo "inventory accepted a modified frozen-baseline file" >&2; exit 1
fi

echo "US-097 read-only inventory contract tests passed"
