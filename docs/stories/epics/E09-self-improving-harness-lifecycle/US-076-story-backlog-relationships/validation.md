# Validation

## Proof Strategy

Use temporary databases and separate changesets to prove relationship validation,
one-resolver authority, atomic failure, query explainability, and uid-based
rebuild parity.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Relationship parsing, resolves/references conflict, accepted-target eligibility, terminal-story refusal, and one-resolver rule. |
| Integration | Missing or unkeyed targets, duplicate link, open resolver replace/unlink, closed resolver immutability, reference unlink, verification invalidation, transaction rollback, and detailed query output. |
| E2E | One story resolves an accepted occurrence while two other stories reference it without closure authority. |
| Platform | Link operations in a later changeset resolve the correct backlog uid after fresh rebuild. |
| Performance | Indexed relationship queries remain bounded. |
| Logs/Audit | Changeset rendering explains link changes and historical resolver provenance. |

## Fixtures

- One accepted backlog occurrence with stable uid.
- Two candidate resolver stories and two reference stories.
- Different local backlog integer ids across source and rebuild databases.

## Commands

```bash
cargo fmt --check
sh -c 'cargo test -p harness-cli -- --list | rg "story_backlog_relationship" && cargo test -p harness-cli story_backlog_relationship -- --nocapture'
scripts/validate-changeset-rebuild.sh
cargo clippy --workspace -- -D warnings
git diff --check
```

## Acceptance Evidence

Add exact migration, command, and rebuild outputs after implementation.
