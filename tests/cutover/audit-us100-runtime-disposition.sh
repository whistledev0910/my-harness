#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASELINE="$ROOT_DIR/docs/stories/epics/E11-symphony-repository-separation/US-089-separation-boundary-and-frozen-baselines/evidence/worktree-backups.json"
MODE="${1:---plan}"

case "$MODE" in
  --plan|--expect-clean) ;;
  *) echo "usage: $0 [--plan|--expect-clean]" >&2; exit 2 ;;
esac

fail() { echo "US-100 runtime disposition audit failed: $*" >&2; exit 1; }
for command in git jq shasum; do
  command -v "$command" >/dev/null || fail "required command is missing: $command"
done
test -f "$BASELINE" || fail "US-089 worktree backup manifest is missing"

sha_text() { shasum -a 256 | awk '{print $1}'; }
empty_sha="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
records='[]'

while IFS= read -r worktree; do
  test "$worktree" != "$ROOT_DIR" || continue
  case "$worktree" in
    "$ROOT_DIR"/.symphony/worktrees/*) ;;
    *) fail "unexpected registered worktree outside the Symphony runtime root: $worktree" ;;
  esac

  id="$(basename "$worktree")"
  expected="$(jq -c --arg id "$id" '.[] | select(.id == $id)' "$BASELINE")"
  test -n "$expected" || fail "registered worktree has no frozen US-089 backup: $id"

  head="$(git -C "$worktree" rev-parse HEAD)"
  branch="$(git -C "$worktree" branch --show-current)"
  unstaged_sha="$(git -C "$worktree" diff --binary | sha_text)"
  staged_sha="$(git -C "$worktree" diff --binary --cached | sha_text)"
  untracked_count="$(git -C "$worktree" ls-files --others --exclude-standard -z | tr -cd '\0' | wc -c | tr -d ' ')"

  test "$head" = "$(jq -r '.head' <<<"$expected")" || fail "$id HEAD drifted after backup"
  test "$branch" = "$(jq -r '.branch' <<<"$expected")" || fail "$id branch drifted after backup"
  test "$unstaged_sha" = "$(jq -r '.unstaged_patch_sha256' <<<"$expected")" || fail "$id unstaged bytes drifted after backup"
  test "$staged_sha" = "$(jq -r '.staged_patch_sha256' <<<"$expected")" || fail "$id staged bytes drifted after backup"
  test "$untracked_count" = "$(jq -r '.untracked_file_count' <<<"$expected")" || fail "$id untracked file count drifted after backup"
  test "$(jq -r '.restore_rehearsal' <<<"$expected")" = pass || fail "$id backup was not restore-rehearsed"

  records="$(jq -c \
    --arg id "$id" --arg head "$head" --arg branch "$branch" \
    --arg unstaged "$unstaged_sha" --arg staged "$staged_sha" \
    --argjson untracked "$untracked_count" \
    '. + [{id:$id,head:$head,branch:$branch,staged_patch_sha256:$staged,unstaged_patch_sha256:$unstaged,untracked_file_count:$untracked,backup_match:true,restore_rehearsal:"pass",disposition:"remove_after_owner_approval"}]' \
    <<<"$records")"
done < <(git -C "$ROOT_DIR" worktree list --porcelain | awk '/^worktree / {sub(/^worktree /, ""); print}')

worktree_count="$(jq 'length' <<<"$records")"
impeccable_files=0
if test -d "$ROOT_DIR/.impeccable"; then
  impeccable_files="$(find "$ROOT_DIR/.impeccable" -type f | wc -l | tr -d ' ')"
fi
changeset_files=0
if test -d "$ROOT_DIR/.harness/changesets"; then
  changeset_files="$(find "$ROOT_DIR/.harness/changesets" -type f | wc -l | tr -d ' ')"
fi

if test "$MODE" = --expect-clean; then
  test "$worktree_count" = 0 || fail "$worktree_count"' archived Symphony worktrees remain registered'
  test "$impeccable_files" = 0 || fail "$impeccable_files"' .impeccable files remain active'
  test "$changeset_files" = 0 || fail "$changeset_files"' .harness/changesets files remain active'
fi

jq -n \
  --arg schema e11-us100-runtime-disposition-plan-v1 \
  --arg mode "${MODE#--}" --argjson worktrees "$records" \
  --argjson worktree_count "$worktree_count" \
  --argjson impeccable_files "$impeccable_files" \
  --argjson changeset_files "$changeset_files" \
  --arg empty_sha "$empty_sha" \
  '{schema:$schema,mode:$mode,status:(if $mode == "expect-clean" then "complete" else "pending_owner_approval" end),worktree_count:$worktree_count,worktrees:$worktrees,impeccable:{file_count:$impeccable_files,disposition:(if $impeccable_files == 0 then "absent" else "remove_after_owner_approval" end)},changesets:{file_count:$changeset_files,empty_sha256:$empty_sha,disposition:(if $changeset_files == 0 then "absent" else "review" end)},all_worktree_backups_match:all($worktrees[]; .backup_match and .restore_rehearsal == "pass")}'
