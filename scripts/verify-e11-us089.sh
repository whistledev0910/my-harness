#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
evidence_dir="${E11_US089_EVIDENCE_DIR:-$repo_root/docs/stories/epics/E11-symphony-repository-separation/US-089-separation-boundary-and-frozen-baselines/evidence}"

python3 "$repo_root/scripts/e11-us089-baseline.py" verify --evidence-dir "$evidence_dir"

source_json="$evidence_dir/source.json"
artifact_dir="${E11_US089_ARTIFACT_DIR:?set E11_US089_ARTIFACT_DIR to the external owner-only US-089 vault}"
artifact_dir="$(cd "$artifact_dir" && pwd)"
case "$artifact_dir/" in
  "$repo_root/"*|"/Users/themrb/Documents/personal/symphony/"*)
    echo "E11_US089_ARTIFACT_DIR must be outside both product checkouts" >&2
    exit 1
    ;;
esac
bundle_name="$(awk '{print $2}' "$evidence_dir/bundle.sha256")"
bundle="$artifact_dir/$bundle_name"
database="$artifact_dir/harness.db"

test -d "$artifact_dir"
test -f "$bundle"
test -f "$database"

(cd "$artifact_dir" && shasum -a 256 -c "$evidence_dir/bundle.sha256")
(cd "$repo_root" && shasum -a 256 -c "$evidence_dir/changesets.sha256")
activation_changeset="$repo_root/.harness/changesets/run_1783790000000000000_us089_activation.changeset.jsonl"
completion_changeset="$repo_root/.harness/changesets/run_1783791000000000000_us089_completion.changeset.jsonl"
test -f "$activation_changeset"
test -f "$completion_changeset"
test "$(find "$repo_root/.harness/changesets" -maxdepth 1 -type f -name '*.changeset.jsonl' | wc -l | tr -d ' ')" = "34"
printf '%s  %s\n' "$(awk '{print $1}' "$evidence_dir/activation.sha256")" "$activation_changeset" | shasum -a 256 -c -
jq -se '
  length == 3 and
  .[0] == {"base_schema_version":12,"op":"changeset.header","run_id":"run_1783790000000000000_us089_activation","version":1} and
  .[1].op == "story.update" and .[1].id == "US-089" and .[1].payload.verify_command == "scripts/verify-e11-us089.sh" and
  .[2].op == "story.update" and .[2].id == "US-089" and .[2].payload.status == "in_progress"
' "$activation_changeset" >/dev/null
printf '%s  %s\n' "$(awk '{print $1}' "$evidence_dir/completion.sha256")" "$completion_changeset" | shasum -a 256 -c -
jq -se '
  length == 2 and
  .[0] == {"base_schema_version":12,"op":"changeset.header","run_id":"run_1783791000000000000_us089_completion","version":1} and
  .[1].op == "story.update" and .[1].id == "US-089" and .[1].payload.status == "implemented" and
  .[1].payload.unit_proof == 1 and .[1].payload.integration_proof == 1 and
  .[1].payload.e2e_proof == 1 and .[1].payload.platform_proof == 1
' "$completion_changeset" >/dev/null
printf '%s  %s\n' "$(awk '{print $1}' "$evidence_dir/database.sha256")" "$database" | shasum -a 256 -c -
git -C "$repo_root" bundle verify "$bundle" >/dev/null

frozen_sha="$(jq -er '.frozen_sha' "$source_json")"
tag="$(jq -er '.tag' "$source_json")"
test "$(git -C "$repo_root" rev-parse "${tag}^{commit}")" = "$frozen_sha"
test "$(git -C "$repo_root" rev-parse develop)" = "$frozen_sha"
test "$(git -C "$repo_root" rev-list --count main..develop)" = "18"

# Python capture already opens this snapshot with mode=ro. macOS sqlite3 3.43
# cannot open a WAL-mode snapshot with -readonly unless sidecar creation is
# allowed, so this second CLI integrity pass uses the owner-only vault path.
sqlite3 "$database" 'PRAGMA integrity_check; PRAGMA foreign_key_check;' |
  awk 'NR == 1 && $0 == "ok" { ok=1; next } { bad=1 } END { exit !(ok && !bad) }'

jq -e '.expected_counts == {"harness_cli_rust_tests":73,"harness_symphony_rust_tests":99,"playwright_tests":19}' \
  "$evidence_dir/baseline.json" >/dev/null
while IFS=$'\t' read -r relative expected; do
  log="$artifact_dir/$relative"
  test -f "$log"
  test "$(shasum -a 256 "$log" | awk '{print $1}')" = "$expected"
done < <(jq -r '.commands[] | [.log,.log_sha256] | @tsv' "$evidence_dir/baseline.json")
rg -q '73 passed' "$artifact_dir/frozen-baseline/logs/cargo-test.log"
rg -q '99 passed' "$artifact_dir/frozen-baseline/logs/cargo-test.log"
rg -q '19 passed' "$artifact_dir/frozen-baseline/logs/web-e2e.log"

if git ls-remote --heads --tags git@github.com:hoangnb24/symphony.git | grep -q .; then
  echo "target Symphony remote is no longer empty" >&2
  exit 1
fi

git -C "$repo_root" diff --check
echo "US-089 frozen baseline verification passed"
