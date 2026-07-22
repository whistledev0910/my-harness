# Exec Plan

## Goal

Separate operational memory without losing recoverability or weakening generic
Harness replay behavior.

## Scope

In scope:

- Backups, raw archive, hashes, and ownership export.
- Synthetic core replay fixtures and validator rewrite.
- Fresh core DB preparation plus target DB backup/reconciliation.
- Removal of tracked active root changesets after proof.

Out of scope:

- Source crate/docs deletion.
- Git worktree pruning.
- Deleting historical bundles.

## Risk Classification

Risk flags:

- Data model and migration.
- Existing behavior.
- Audit/history integrity.
- Multi-domain.
- Weak proof from incomplete current replay.

Hard gates:

- Data loss/migration.
- Audit history.
- Validation replacement.

## Work Phases

1. Stop writers, create the partition-cutoff manifest, and verify DB/log/
   worktree backups against both the frozen and cutoff manifests.
2. Add synthetic generic replay fixtures first.
3. Rewrite and pass validators against fixtures.
4. Dynamically export every live user table/row/edge and prove disposition/FK
   closure.
5. Build a fresh migrated core DB, preserving E11 receipt proxies/edges, and
   stage reviewed target additions through the target CLI.
6. Compare per-table counts/UID sets, derived epoch state, invariants, and
   queries in both repositories.
7. Under a writer fence, use a checksummed epoch-transition journal to switch
   the core DB and active changeset directory as one recoverable pair while
   retaining the generic consumer tracking rule. Leave the journal incomplete
   and writers blocked after the fresh DB is active and the legacy log
   directory is archived; startup refuses that in-progress transition.
8. While still fenced, run audit, proposal, matrix, backlog, tools, generic
   replay, crash recovery, and a fresh consumer changeset-commit fixture. Only
   after every check passes write the completion marker and release writers;
   otherwise compensate to the original pair without exposing the new epoch.

## Dependencies

- `US-095` standalone parity, so the target can receive deliberate active work.

## Stop Conditions

Pause if a backup cannot verify, any mixed operation lacks an owner, live-only
work/table lacks a disposition, a retained foreign key does not close, an open
E11 receipt proxy/edge would be dropped, generic fixtures do not cover a
removed validator case, before/after core invariants differ unexpectedly, or
the platform cannot durably journal/rename and recover the DB/log pair.

## Rollback

Stop all writers. If the transition marker is incomplete, immediately finish
the named pair or compensate by restoring the original DB plus original
changeset directory; writers remain blocked throughout. Recheck journal and
artifact checksums, mark the recovered epoch complete, and rerun the old
matrix/audit before unlocking. Restore the separate target backup only if
staged target CLI additions must also be undone. Never mix a fresh projection
with a DB that already applied legacy run IDs.
