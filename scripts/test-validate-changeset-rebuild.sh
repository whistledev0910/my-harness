#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATOR="$ROOT_DIR/scripts/validate-changeset-rebuild.sh"
CLI="$ROOT_DIR/target/debug/harness-cli"
FIXTURE_ROOT="$ROOT_DIR/tests/fixtures/changesets/generic-rebuild"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
FIXTURE_REPO="$TMP_DIR/repo"
mkdir -p "$FIXTURE_REPO/scripts"
cp -R "$ROOT_DIR/scripts/schema" "$FIXTURE_REPO/scripts/schema"

cargo build --quiet --manifest-path "$ROOT_DIR/Cargo.toml" -p harness-cli
HARNESS_VALIDATOR_LIBRARY_ONLY=1 source "$VALIDATOR"
unset HARNESS_VALIDATOR_LIBRARY_ONLY

default_output="$(env -u HARNESS_CLI "$VALIDATOR")"
grep -Fq "rebuild validator executable: $CLI" <<<"$default_output"
grep -Fq "rebuild validator fixtures: $FIXTURE_ROOT/positive" <<<"$default_output"
grep -Fq "generic changeset rebuild passed" <<<"$default_output"

override_output="$(HARNESS_CLI="$CLI" "$VALIDATOR" --fixtures "$FIXTURE_ROOT/positive" --expected "$FIXTURE_ROOT/expected.json")"
grep -Fq "rebuild validator executable: $CLI" <<<"$override_output"

if HARNESS_CLI="$TMP_DIR/missing-cli" "$VALIDATOR" >"$TMP_DIR/missing.out" 2>&1; then
  echo "validator unexpectedly accepted a missing explicit CLI" >&2
  exit 1
fi
grep -Fq "Harness CLI not found" "$TMP_DIR/missing.out"

selection_root="$TMP_DIR/selection-root"
mkdir -p "$selection_root/target/debug" "$selection_root/scripts/bin"
printf '%s\n' '#!/usr/bin/env bash' 'exit 0' >"$selection_root/target/debug/harness-cli"
printf '%s\n' '#!/usr/bin/env bash' 'exit 0' >"$selection_root/scripts/bin/harness-cli"
chmod +x "$selection_root/target/debug/harness-cli" "$selection_root/scripts/bin/harness-cli"
touch -t 209912312359 "$selection_root/scripts/bin/harness-cli"
selected="$(HARNESS_CLI= HARNESS_VALIDATOR_SKIP_BUILD=1 select_harness_cli "$selection_root")"
[[ "$selected" == "$selection_root/target/debug/harness-cli" ]]

assert_failed_apply_rolled_back() {
  local fixture="$1"
  local run_id="$2"
  local story_id="$3"
  local expected_error="$4"
  local name="$5"
  local db="$TMP_DIR/$name.db"
  HARNESS_REPO_ROOT="$FIXTURE_REPO" HARNESS_DB_PATH="$db" "$CLI" init >/dev/null
  if HARNESS_REPO_ROOT="$FIXTURE_REPO" HARNESS_DB_PATH="$db" "$CLI" db changeset apply "$fixture" >"$TMP_DIR/$name.out" 2>&1; then
    echo "negative fixture unexpectedly applied: $name" >&2
    exit 1
  fi
  grep -Fq "$expected_error" "$TMP_DIR/$name.out"
  [[ "$(sqlite3 "$db" "SELECT COUNT(*) FROM story WHERE id='$story_id';")" == "0" ]]
  [[ "$(sqlite3 "$db" "SELECT COUNT(*) FROM changeset_applied WHERE id='$run_id';")" == "0" ]]
}

assert_failed_apply_rolled_back \
  "$FIXTURE_ROOT/negative/unsupported-op.changeset.jsonl" \
  fixture_negative_unsupported FIX-ROLLBACK \
  "unsupported operation 'fixture.unsupported'" unsupported

assert_failed_apply_rolled_back \
  "$FIXTURE_ROOT/negative/invalid-timestamp.changeset.jsonl" \
  fixture_negative_timestamp FIX-BAD-TIMESTAMP \
  "verified_at must use YYYY-MM-DD HH:MM:SS" invalid-timestamp

assert_failed_apply_rolled_back \
  "$FIXTURE_ROOT/negative/missing-timestamp.changeset.jsonl" \
  fixture_negative_missing_timestamp FIX-MISSING-TIMESTAMP \
  "story.verify version 2 requires verified_at" missing-timestamp

identity_db="$TMP_DIR/identity.db"
identity_fixture="$TMP_DIR/identity.changeset.jsonl"
cp "$FIXTURE_ROOT/positive/001-story-graph.changeset.jsonl" "$identity_fixture"
HARNESS_REPO_ROOT="$FIXTURE_REPO" HARNESS_DB_PATH="$identity_db" "$CLI" init >/dev/null
HARNESS_REPO_ROOT="$FIXTURE_REPO" HARNESS_DB_PATH="$identity_db" "$CLI" db changeset apply "$identity_fixture" >/dev/null
sed 's/Generic root/Changed bytes/' "$identity_fixture" >"$identity_fixture.changed"
mv "$identity_fixture.changed" "$identity_fixture"
if HARNESS_REPO_ROOT="$FIXTURE_REPO" HARNESS_DB_PATH="$identity_db" "$CLI" db changeset status "$identity_fixture" --json >"$TMP_DIR/identity.out" 2>&1; then
  echo "changeset status unexpectedly accepted changed content for an applied run ID" >&2
  exit 1
fi
grep -Fq "changeset identity conflict" "$TMP_DIR/identity.out"
[[ "$(sqlite3 "$identity_db" "SELECT title FROM story WHERE id='FIX-ROOT';")" == "Generic root" ]]
[[ "$(sqlite3 "$identity_db" "SELECT COUNT(*) FROM changeset_applied WHERE id='fixture_generic_story_graph';")" == "1" ]]

echo "generic rebuild validator contract tests passed"
