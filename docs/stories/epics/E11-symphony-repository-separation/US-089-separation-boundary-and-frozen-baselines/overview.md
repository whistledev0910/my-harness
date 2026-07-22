# Overview

## Current Behavior

The only working Symphony implementation is inside clean
`repository-harness/develop@6e8243f`, while the target Symphony repository has
no commits. Source code, docs, release metadata, operational changesets, live
database rows, tool providers, and ignored worktrees have different ownership
and cannot be separated by one directory copy.

The source also has two baselines: `develop` is 18 commits ahead of `main` and
contains 87 additional Symphony run-lifecycle lines. Choosing `main` by habit
would silently omit required completion behavior.

## Target Behavior

Before any move, filter, deletion, database replacement, or remote push, the
migration has an exact frozen source SHA, path manifest, durable-record
classification, source bundle, changeset hashes, worktree inventory, and green
test report. Every item has exactly one action: move, retain, rewrite, archive,
or discard after proof.

## Affected Users

- Harness maintainers who need a recoverable core cleanup.
- Symphony maintainers who need complete implementation provenance.
- Agents that currently read mixed product context from the source repository.

## Affected Product Docs

- `docs/decisions/0009-separate-symphony-product-repository.md`
- `docs/stories/epics/E11-symphony-repository-separation/migration-manifest.md`

## Acceptance Criteria

- The accepted extraction SHA is exactly
  `6e8243f2a5cb6a32cf0a7a0ecebdb257a429bdd9`. Planning/control SHA
  `e3980e5acdf520bf75101b9ef4a9fd4da310fc3e` is recorded separately; its 38
  changed paths are not extraction inputs.
- `develop` versus `main` is resolved explicitly; extraction never silently
  falls back to the older default branch.
- An annotated pre-extraction tag and `git bundle --all` are created from a
  clean source, and both the bundle and tag resolve to the frozen SHA. The
  bundle is explicitly treated as committed-ref recovery only, not as a backup
  of ignored or uncommitted worktree content.
- SHA-256 files cover the bundle, every one of the 31 original changesets, and
  the later transitional E11 planning changeset.
- A machine-readable path manifest assigns every tracked source path one
  disposition and reports zero unclassified paths.
- The 13 Symphony-owned, 15 core-owned, and 3 mixed changesets are enumerated
  by path and operation ownership.
- The live database export discovers every user table from `sqlite_master`
  (excluding SQLite internal tables), records every row/edge disposition, and
  verifies foreign-key closure. This includes stories, intakes, traces,
  backlog, decisions, tools, dependencies, hierarchy, `intervention`,
  `story_backlog_link`, `proposal_evidence_link`, `audit_evidence_episode`,
  `backlog_outcome_observation`, `legacy_evidence_snapshot`,
  `changeset_applied`, and `schema_version`; a newly discovered table fails the
  zero-unknown gate until classified.
- The primary checkout was clean at the immutable planning cutoff. All 15
  auxiliary registered worktrees are listed with branch, HEAD, and dirty status. The
  known 380-line uncommitted run diff is preserved or explained; no worktree is
  deleted. For every dirty worktree, binary-safe unstaged and staged patches,
  an untracked-file archive, file hashes, and the worktree HEAD are captured
  and restored in a disposable rehearsal.
- DB, run, worktree, and untracked archives are never committed. A secret/path
  review runs before storage; evidence is kept outside both checkouts with
  owner-only permissions (or encryption), and the committed plan records only
  non-sensitive checksums/identities.
- Every ignored SQLite candidate under the root, registered worktrees,
  recovery files, and `.harness/db-backups` is dynamically inventoried and
  backed up or assigned an explicit reviewed disposition. All eight unreachable
  commits have binary patches outside Git because a bundle contains only refs.
- The Rust, Web build, Playwright, desktop smoke, format, clippy, and rebuild
  baselines pass and are attached with exact commands.
- No source product file is moved or deleted in this story.

## Non-Goals

- Filter or push target history.
- Modify either product's runtime behavior.
- Clean ignored worktrees, runs, or databases.
- Decide a file's owner from its name alone.
