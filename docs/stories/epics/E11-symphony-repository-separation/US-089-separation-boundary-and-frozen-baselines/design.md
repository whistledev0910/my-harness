# Design

## Domain Model

The migration inventory uses four stable identifiers:

- `source_sha`: immutable repository-harness commit.
- `source_path`: path at that commit.
- `record_identity`: stable story/trace/backlog/tool identity when available.
- `disposition`: `move`, `retain`, `rewrite`, `archive`, or `discard_after_gate`.

Every inventory row also records a reason and the story that may perform the
action. Unknown ownership is an error, not a default to move or delete.

## Application Flow

```text
verify clean source and empty target
  -> freeze source SHA
  -> tag and bundle all committed refs
  -> hash bundle and changesets
  -> inventory tracked paths
  -> export durable row metadata
  -> inventory worktrees and ignored runtime
  -> run green baseline
  -> review zero-unknown report
```

## Interface Contract

Sanitized, reviewable evidence is stored under this story's `evidence/`
directory:

- `source.json`
- `paths.tsv`
- `planning-transition-paths.tsv`
- `durable-records.json`
- `durable-ownership-map.json`
- `changesets.tsv`
- `changeset-operations.json`, `changesets-summary.json`, and
  `applied-ledger.tsv`
- `changesets.sha256`
- `worktrees.txt`
- `worktree-backups.json`
- `ignored-runtime.tsv` and `ignored-runtime-backups.json`
- `wal-backup-proof.json`, `unreachable-commits.json`, and
  `replay-comparison.json`
- `baseline.json` and `baseline.md`
- `bundle.sha256`

Raw databases, patches, tar archives, the bundle, full row exports, disposable
clones, and command logs live only in the owner-only external vault selected by
`E11_US089_ARTIFACT_DIR`. Committed evidence uses logical IDs and SHA-256 and
contains no absolute workstation or vault path.

`paths.tsv` columns are:

```text
source_path  mode  object_type  object_id  disposition  owner_repository  implementation_story  reason
```

## Data Model

After writers are stopped/fenced, the live SQLite database is captured with
SQLite's online backup API into a new file, integrity-checked, and checksummed.
A bare `harness.db` copy is not accepted because committed WAL pages may be
missing; a SQL dump is useful additional evidence, not the only backup.

Table discovery queries `sqlite_master` for every non-internal user table. The
export records table schema, stable UID where present, local ID, timestamp,
status/outcome, owner, disposition, and referenced parent identities. A
foreign-key closure check proves that every retained or moved row's referenced
rows have a compatible disposition. `schema_version` and `changeset_applied`
are classified as epoch/derived state rather than silently copied as product
records.

`git bundle --all` cannot contain dirty, staged, untracked, or ignored files.
Each dirty registered worktree therefore receives a binary patch for staged and
unstaged tracked changes plus a content-addressed untracked archive. A throwaway
checkout applies those artifacts and compares hashes before the inventory is
accepted.

Raw DB/worktree/run evidence is an operational backup, not repository content.
It is secret-scanned, stored outside both working trees with `0600`-equivalent
access or encryption, and referenced from committed evidence only by safe
logical identity and SHA-256.

The extraction manifest comes from the immutable tree at
`6e8243f2a5cb6a32cf0a7a0ecebdb257a429bdd9`, not from the planning branch. The
38-path planning delta through `e3980e5` is recorded separately and is not a
history-filter input.

## UI / Platform Impact

None. This story only records current state.

## Observability

The baseline report records command, exit status, tool versions, duration, and
the frozen SHA. A passing command from another commit is not accepted.

## Alternatives Considered

1. Use `git status` and a prose checklist only. Rejected because hundreds of
   paths and durable rows need machine-checkable coverage.
2. Treat the committed changesets as the full backup. Rejected because a fresh
   rebuild produces 59 stories while the live DB has 84.
3. Delete ignored runtime as generated data. Rejected because at least one
   registered worktree contains a real uncommitted implementation diff.
