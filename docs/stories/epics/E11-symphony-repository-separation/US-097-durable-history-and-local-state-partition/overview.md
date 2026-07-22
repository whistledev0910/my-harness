# Overview

## Current Behavior

At discovery, repository-harness tracked 31 operational changesets and used them
as a generic rebuild test even though they contain product history. Thirteen
are Symphony-owned, fifteen are core-owned, and three mix operations from both.
The E11 planning pass adds a transitional 32nd file. `US-092`, `US-093`, and
later receipt work may add more semantic files before partition, so 32 is a
baseline—not the final archive count.
The live local DB is also more complete than replay: it has 84 stories while
rebuild produces 59, plus live-only Symphony backlog and tool rows.

As a result, simply moving or deleting files either loses evidence or breaks
core validators and story proof. Keeping them active continues to reconstruct
Symphony work in the Harness repository.

## Target Behavior

Legacy raw state is backed up and checksummed, generic changeset behavior is
proved with synthetic test fixtures, and repository-harness begins an explicit
new active-state epoch with a fresh core-owned local DB and no tracked live
`.harness/changesets`. The target DB initialized by `US-093` is preserved;
selected live-only Symphony work is reviewed and added through the target CLI
rather than replacing that DB.

## Repository Ownership

Coordinated, with repository-harness backup/fixture/core-epoch work as the
primary implementation. Target writes are limited to the already reviewed
`US-094` dispositions and use only the target Harness CLI.

## Affected Users

- Maintainers relying on the local matrix, audit, backlog, and proposal loop.
- Future agents that must not receive work from the wrong product.
- Reviewers relying on semantic replay proof.

## Affected Product Docs

- Decision `0009`.
- `scripts/README.md`.
- Rebuild validator documentation.
- E11 migration manifest.

## Acceptance Criteria

- Before mutation, the source DB and every file in the frozen changeset
  manifests are preserved: the 32-file `US-089` baseline and a new partition
  cutoff containing every then-present semantic file, including post-baseline
  E11 protocol/proxy/receipt operations. Their hashes, full Git bundle, and
  worktree/run inventory are stored in verified backups outside the active
  checkout. Counts are derived from and reconciled between the two manifests,
  never hard-coded by the migration script.
- The three mixed changesets remain unedited in the raw archive. Any projected
  active operations use new run IDs so replay idempotence cannot skip changed
  content under an old header.
- Synthetic fixtures under a test-owned path cover add/update/retire/verify,
  dependency and hierarchy operations, tool changes, ID remapping, timestamps,
  idempotence, unsupported operations, and rollback.
- `scripts/validate-changeset-rebuild.sh` and its contract tests use those
  fixtures and contain no Symphony IDs or product row counts.
- Before replacement, table discovery enumerates every non-internal
  `sqlite_master` user table and exports every row/edge with stable UID/local
  ID, timestamps, status/outcome, owner, disposition, and foreign-key closure.
  It explicitly covers `intervention`, `story_backlog_link`,
  `proposal_evidence_link`, `audit_evidence_episode`,
  `backlog_outcome_observation`, `legacy_evidence_snapshot`,
  `changeset_applied`, and `schema_version`, not only story/backlog/tool rows.
- The source live-only Symphony slices are exported before replacement.
  `US-097` consumes the reviewed `US-094` dispositions and applies each target
  CLI mutation exactly once with stable provenance; omitted rows remain
  documented rather than silently dropped.
- Idempotent re-run produces no duplicate open proposal key, backlog
  occurrence, story, tool provider, or resolver authority in the target.
- A fresh core DB retains accepted core decisions and active core work,
  including E10/E11, without Symphony product backlog/traces/tools. The only
  temporary target-owned rows permitted are E11's completed or non-runnable
  `changed` receipt proxies and their original source edges. In particular, an
  unfinished `US-096` proxy survives if `US-097` activates first; it continues
  to block `US-098`/`US-100` until its target receipt completes it.
- The target DB from `US-093` is backed up and augmented only through Harness
  CLI operations. It is never replaced by or merged with the opaque source DB.
- Target CLI JSON responses and receipt hashes provide replay/audit evidence;
  temporary target semantic files are archived outside the active checkout so
  Symphony also ends with no tracked live `.harness/changesets`.
- Core and target ownership comparison reports no runnable record present in
  the wrong repository and no duplicated resolver authority. Per-table counts
  and stable-UID sets match the approved disposition manifest and all retained
  foreign keys close.
- The fresh core DB reaches the current schema by normal migrations;
  `schema_version`, `changeset_applied`, and derived tool-presence/index state
  are reset or recomputed for the new epoch rather than copied from legacy.
- Repository-harness stops tracking its current live
  `.harness/changesets/*.jsonl` files; active root runtime is ignored locally.
  The generic `.gitignore`/installer exception that lets a consuming repository
  commit its own semantic changesets is retained and tested in a fresh consumer.
- Generic `db changeset apply` and `db rebuild` behavior remains in the CLI and
  passes synthetic replay proof.
- Failure at any comparison step leaves the original DB and changeset directory
  active and restorable.
- Core activation uses a checksummed transition journal/completion marker while
  writers are fenced. Crash injection after each rename proves startup refuses
  a mixed fresh-DB/legacy-log epoch and can finish or compensate to one verified
  pair before writers resume. The marker stays incomplete and the writer fence
  remains held until audit/proposal/matrix/backlog/tools and replay checks pass
  against the switched pair.

## Non-Goals

- Delete Git history or the raw archive.
- Reconstruct every historical trace as active target work.
- Remove semantic changeset capability from Harness.
- Delete ignored worktrees or run directories.
