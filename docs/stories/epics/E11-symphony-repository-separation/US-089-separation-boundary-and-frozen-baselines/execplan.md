# Exec Plan

## Goal

Create a complete, recoverable, reviewable extraction baseline without changing
product behavior or ownership yet.

## Scope

In scope:

- Source/target ref checks.
- Tag, bundle, hashes, inventories, and test evidence.
- Exact ownership manifest.
- Worktree and runtime-state safety report.

Out of scope:

- Target import.
- Source cleanup.
- Database replacement.

## Risk Classification

Risk flags:

- Existing behavior.
- Data migration.
- Multi-domain.
- Weak proof if ignored worktrees or live-only rows are missed.

Hard gates:

- Data loss or migration.
- Removing validation requirements.

## Work Phases

1. Reconfirm both repository states and remote refs.
2. Resolve the `develop`/`main` extraction source.
3. Create and verify rollback tag/bundle for committed refs.
4. Generate path, changeset, and dynamic all-user-table database inventories.
5. Capture binary-safe staged/unstaged patches and untracked archives for every
   dirty worktree, then rehearse restoration in disposable checkouts.
6. Run the complete baseline at the frozen SHA.
7. Review zero-unknown ownership/FK closure and attach evidence.

## Dependencies

None. This story blocks every mutating E11 story.

## Stop Conditions

Pause if:

- Either working tree has unowned changes.
- The target remote gains a commit or tag.
- The selected SHA omits commits present at the discovery SHA.
- A registered worktree cannot be inspected.
- Any tracked path, changeset operation, or active durable row is unclassified.
- A baseline command fails.

## Rollback

This story is additive. Remove only newly created evidence after confirming the
source tag and bundle are not the sole recovery copies.
