# Exec Plan

## Goal

Create the first Symphony history safely from the frozen source without making
the source cleanup contingent on an irreversible remote rewrite.

## Scope

In scope:

- Disposable clone and pinned filter tool.
- Multi-path history filtering.
- Provenance/commit-map evidence.
- Initial target push and raw-import tag.

Out of scope:

- Source deletion.
- Runtime changes.
- Operational database migration.

## Risk Classification

Risk flags:

- Existing behavior.
- External system.
- Data/history migration.
- Multi-domain.

Hard gates:

- Remote history mutation.
- Data migration.

## Work Phases

1. Verify `US-089` artifacts and target emptiness.
2. Pin, checksum, install, and record the filter-repo version.
3. Create one disposable extraction branch at the frozen SHA, delete/exclude
   every other ref from the filtering namespace, and filter using the reviewed
   manifest.
4. Verify path exclusions and representative commit lineage.
5. Add provenance metadata and the raw import tag.
6. Push only `HEAD:main` and the raw-import tag after review of the filtered
   graph; reject mirror/all-ref pushes.

## Dependencies

- `US-089` complete.

## Stop Conditions

Pause if the target contains refs, a representative source commit disappears,
forbidden Harness CLI/database paths appear, or the filter requires changing
the source repository. Immediately before the first remote push, obtain a fresh
owner go/no-go naming the source SHA, filtered target HEAD, raw-import tag, path
manifest hash, and bundle checksum; record it as intervention/evidence.

## Rollback

Before any collaborator builds on the target, delete the imported target refs
and rerun from the source bundle only after a new owner go/no-go names the exact
refs and confirms no collaborator has based work on them. If that cannot be
proven, preserve the refs and choose a separately reviewed forward/recovery
path. Never roll back by rewriting repository-harness.
