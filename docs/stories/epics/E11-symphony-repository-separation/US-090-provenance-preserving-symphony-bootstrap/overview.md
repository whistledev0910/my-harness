# Overview

## Current Behavior

The target Symphony remote is empty. A filesystem copy would work mechanically
but would lose 34 commits of crate evolution plus the relationship between
scope, runner, UI, review, and bug-fix changes.

## Target Behavior

A disposable clone of repository-harness is filtered from the frozen
`develop` SHA using the reviewed path manifest. The result is pushed to the
empty Symphony remote with a commit map and provenance note. The original
repository is never filtered or force-pushed.

## Affected Users

- Symphony contributors using blame, log, and bisect.
- Harness maintainers who need proof that cleanup did not erase the only copy.

## Affected Product Docs

- E11 migration manifest.
- Target `docs/provenance/repository-harness-import.md`.

## Acceptance Criteria

- Filtering runs only in a disposable clone from the `US-089` bundle/tag. The
  clone has one extraction branch at the frozen SHA; every other local ref is
  deleted or excluded before filtering.
- `git-filter-repo` is installed from a pinned version and verified against a
  recorded publisher/source checksum before it touches the disposable clone.
- The exact `--paths-from-file` input is tracked with the target provenance
  note and matches the approved manifest.
- The imported lineage starts from accepted Symphony scope/implementation
  commits and excludes unrelated Harness CLI source and historical SQLite
  blobs.
- Representative target history traces to source commits `444d793` (runner),
  `f539f5d` (Web UI), and the later lifecycle fixes present at `6e8243f`.
- The filter-repo old-to-new commit map and original source SHA are tracked.
- Target is tagged at the raw import boundary before standalone bootstrap edits.
- `crates/harness-symphony/` is preserved; no flattening occurs.
- Target history contains no `crates/harness-cli/**` implementation.
- Target filtered history contains no active `.harness/changesets/**`,
  `.agents/**`, `.codex/**`, or `.impeccable/**` tree; those are preserved only
  by the source bundle/archive when historical evidence is needed.
- Source refs, files, and history are byte-for-byte unchanged by the import.
- The remote operation pushes only the reviewed filtered `HEAD:main` and the
  one raw-import tag; it never uses `--mirror`, `--all`, or pushes refs brought
  in by the recovery bundle.
- If the target remote is no longer empty, the story stops for a merge/history
  decision instead of force-pushing.

## Non-Goals

- Make the filtered tree buildable; `US-091` owns that.
- Reorganize docs.
- Import live databases, ignored run state, or all monorepo changesets.
- Delete source paths.
