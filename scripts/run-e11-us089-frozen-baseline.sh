#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
evidence_dir="${E11_US089_EVIDENCE_DIR:-$repo_root/docs/stories/epics/E11-symphony-repository-separation/US-089-separation-boundary-and-frozen-baselines/evidence}"
source_json="$evidence_dir/source.json"
artifact_dir="${E11_US089_ARTIFACT_DIR:?set E11_US089_ARTIFACT_DIR to the external owner-only US-089 vault}"
frozen_sha="$(jq -er '.frozen_sha' "$source_json")"
bundle_name="$(awk '{print $2}' "$evidence_dir/bundle.sha256")"
bundle="$artifact_dir/$bundle_name"
final_baseline_root="$artifact_dir/frozen-baseline"
baseline_root="$artifact_dir/.frozen-baseline.staging.$$"
checkout="$baseline_root/checkout"
logs="$baseline_root/logs"

if [[ -e "$final_baseline_root" ]]; then
  echo "refusing to replace immutable baseline: $final_baseline_root" >&2
  exit 1
fi
trap 'rm -rf "$baseline_root"' EXIT
mkdir -p "$logs"
chmod 700 "$baseline_root" "$logs"
git clone --quiet "$bundle" "$checkout"
git -C "$checkout" checkout --quiet --detach "$frozen_sha"
test "$(git -C "$checkout" rev-parse HEAD)" = "$frozen_sha"
test -z "$(git -C "$checkout" status --short)"

# The online backup is a self-contained fixture. Copying this stopped snapshot
# is safe; copying the live WAL-mode source database is not.
cp "$artifact_dir/harness.db" "$checkout/harness.db"
chmod 600 "$checkout/harness.db"

report_tmp="$baseline_root/results.tsv"
printf 'name\texit_status\tduration_seconds\tlog_sha256\targv\n' >"$report_tmp"

run_check() {
  local name="$1"
  shift
  local started ended status
  started="$(date +%s)"
  set +e
  (cd "$checkout" && "$@") >"$logs/$name.log" 2>&1
  status=$?
  set -e
  ended="$(date +%s)"
  log_sha="$(shasum -a 256 "$logs/$name.log" | awk '{print $1}')"
  printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$status" "$((ended - started))" "$log_sha" "$*" >>"$report_tmp"
  if [[ $status -ne 0 ]]; then
    tail -80 "$logs/$name.log" >&2
    return "$status"
  fi
}

run_check tool-versions sh -c 'git --version; cargo --version; rustc --version; node --version; npm --version; python3 --version; sqlite3 --version'
run_check npm-ci npm --prefix crates/harness-symphony/web-ui ci
run_check playwright-browser npm --prefix crates/harness-symphony/web-ui exec -- playwright install chromium
run_check cargo-test cargo test --workspace
run_check web-build npm --prefix crates/harness-symphony/web-ui run build
run_check web-e2e npm --prefix crates/harness-symphony/web-ui run e2e
run_check desktop-smoke npm --prefix crates/harness-symphony/web-ui run desktop:smoke
run_check cargo-fmt cargo fmt --check
run_check cargo-clippy cargo clippy --workspace -- -D warnings
run_check changeset-rebuild scripts/validate-changeset-rebuild.sh
run_check changeset-validator-tests scripts/test-validate-changeset-rebuild.sh

rg -q '73 passed' "$logs/cargo-test.log"
rg -q '99 passed' "$logs/cargo-test.log"
rg -q '19 passed' "$logs/web-e2e.log"

python3 - "$report_tmp" "$evidence_dir/baseline.json" "$frozen_sha" <<'PY'
import csv, json, sys
source, destination, frozen_sha = sys.argv[1:]
with open(source, newline='', encoding='utf-8') as handle:
    rows = list(csv.DictReader(handle, delimiter='\t'))
for row in rows:
    row['exit_status'] = int(row['exit_status'])
    row['duration_seconds'] = int(row['duration_seconds'])
    row['log'] = f"frozen-baseline/logs/{row['name']}.log"
json.dump({'frozen_sha': frozen_sha, 'commands': rows,
           'expected_counts': {'harness_cli_rust_tests': 73, 'harness_symphony_rust_tests': 99,
                               'playwright_tests': 19}}, open(destination, 'w', encoding='utf-8'), indent=2)
open(destination, 'a', encoding='utf-8').write('\n')
PY

{
  echo '# US-089 Frozen Baseline'
  echo
  echo "- Frozen source: \`$frozen_sha\`"
  echo "- Disposable checkout: external artifact \`frozen-baseline/checkout\`"
  echo '- Database fixture: checksum-verified SQLite online backup; reset before the suite.'
  echo '- Raw logs: external owner-only `frozen-baseline/logs` directory.'
  echo
  echo '| Command | Exit | Duration (seconds) |'
  echo '| --- | ---: | ---: |'
  tail -n +2 "$report_tmp" | while IFS=$'\t' read -r name status duration log_sha argv; do
    printf '| `%s` | %s | %s |\n' "$name" "$status" "$duration"
  done
} >"$evidence_dir/baseline.md"

find "$baseline_root" -type f -exec chmod 600 {} +
find "$baseline_root" -type d -exec chmod 700 {} +
mv "$baseline_root" "$final_baseline_root"
trap - EXIT
echo "US-089 frozen baseline passed at $frozen_sha"
