# Exec Plan

## Goal

Remove reverse product coupling from repository-harness without changing the
generic Harness CLI contract.

## Scope

In scope:

- Tracked source/docs/tooling removal.
- Root workspace/lock and workflow separation.
- Installer, ignore, index, mixed-story, and boundary cleanup.

Out of scope:

- Symphony target changes.
- Runtime-state deletion.
- Final remote cutover.

## Risk Classification

Risk flags:

- Existing behavior.
- Public installer/documentation contract.
- Multi-domain.
- Cross-platform release.
- Removing large tracked trees.

Hard gates:

- Source-of-truth change.
- Validation replacement.
- Potential data loss if ignored runtime is confused with tracked source.

## Work Phases

1. Verify `US-096` and `US-097` evidence.
2. Land/enable capped changelog path rendering.
3. Remove target-owned tracked paths and workspace membership.
4. Generalize retained core capabilities and historical packets.
5. Repoint completed receipt proxies to self-contained E11 historical evidence
   verification and remove the temporary root gate script.
6. Clean installer, ignore, CI, release, and indexes while preserving/test-driving
   the generic consumer changeset tracking rule.
7. Run boundary/link/static checks.
8. Leave full behavioral proof to `US-099` before merge/cutover.

## Dependencies

- `US-096` standalone target release candidate.
- `US-097` durable history/local state partition.

## Stop Conditions

Pause if a removed path lacks a verified target/provenance copy, any CLI command
or schema would be removed, installer output becomes incomplete, or the cleanup
touches ignored worktrees/runs, or a fresh consumer can no longer commit a
semantic changeset.

## Rollback

Revert the cleanup commit/PR. The target remains independently usable, and the
pre-extraction source tag/bundle restores the exact old workspace if needed.
