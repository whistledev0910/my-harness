#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
artifact=${1:-"$repo_root/target/debug/harness-cli"}
artifact=$(cd "$(dirname "$artifact")" && pwd)/$(basename "$artifact")
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
db="$tmp/harness.db"
mkdir -p "$tmp/scripts"
cp -R "$repo_root/scripts/schema" "$tmp/scripts/schema"

run() {
  HARNESS_REPO_ROOT="$tmp" HARNESS_DB_PATH="$db" "$artifact" "$@"
}

# Discovery of a missing target is read-only: the response says "missing" and
# the database path still does not exist afterward.
run query contract --json >"$tmp/contract.json"
jq -e '.protocol_version == 1 and .operation == "query.contract" and .result.database_state == "missing"' "$tmp/contract.json" >/dev/null
test ! -e "$db"

run init >/dev/null
run story add --id US-A --title Alpha --lane normal --verify true --json >"$tmp/add-a.json"
run story add --id US-B --title Beta --lane normal --verify true --json >"$tmp/add-b.json"
jq -e '.result.changed and .result.story.id == "US-A"' "$tmp/add-a.json" >/dev/null

run story dependency add --blocker US-A --blocked US-B --json >/dev/null
run story hierarchy add --parent US-A --child US-B --json >/dev/null
run query work-graph --json >"$tmp/graph-before.json"
jq -e '
  (.result.revision | length) == 64 and
  (.result.stories[] | select(.id == "US-A").runnable) == true and
  (.result.stories[] | select(.id == "US-B").runnable) == false and
  .result.dependencies == [{"blocker":"US-A","blocked":"US-B"}] and
  .result.hierarchy == [{"parent":"US-A","child":"US-B"}]
' "$tmp/graph-before.json" >/dev/null

run story update --id US-A --status implemented --expected-status planned --require-runnable --json >"$tmp/cas.json"
jq -e '.result.before_status == "planned" and .result.after_status == "implemented" and .result.runnable_before' "$tmp/cas.json" >/dev/null
run query stories --json | jq -e '(.result.stories[] | select(.id == "US-B").runnable) == true' >/dev/null

set +e
run story hierarchy add --parent US-B --child US-A --json >"$tmp/conflict.json"
conflict_exit=$?
set -e
test "$conflict_exit" -eq 3
jq -e '.error.code == "CONFLICT" and .operation == "story.hierarchy.add"' "$tmp/conflict.json" >/dev/null

changeset="$tmp/protocol-smoke.jsonl"
printf '%s\n' '{"base_schema_version":13,"op":"changeset.header","run_id":"protocol_smoke","version":1}' >"$changeset"
run db changeset status "$changeset" --json | jq -e '.result.applied == false and .result.operation_count == 0' >/dev/null
run db changeset apply "$changeset" --json | jq -e '.result.applied == true and .result.operations == 0 and (.result.content_sha256 | length) == 64' >/dev/null
run db changeset status "$changeset" --json | jq -e '.result.applied == true' >/dev/null

snapshot="$tmp/path with spaces/snapshot.db"
mkdir -p "$(dirname "$snapshot")"
run db snapshot --output "$snapshot" --json >"$tmp/snapshot.json"
jq -e --arg output "$snapshot" '.result.output == $output and (.result.snapshot_file_sha256 | length) == 64 and (.result.source_logical_sha256 | length) == 64' "$tmp/snapshot.json" >/dev/null
HARNESS_REPO_ROOT="$tmp" HARNESS_DB_PATH="$snapshot" "$artifact" query contract --json |
  jq -e '.result.database_state == "current"' >/dev/null

echo "protocol-v1 native artifact smoke passed"
