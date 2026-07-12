# Design

## Domain Model

Protocol v1 is capability based. Example capability identifiers:

- `stories.read.v1`
- `stories.write.v1`
- `work-graph.read.v1`
- `story-dependencies.read-write.v1`
- `story-hierarchy.read-write.v1`
- `changesets.apply.v1`
- `changesets.status-sha.v1`
- `isolated-db.v1`
- `isolated-db-snapshot.v1`
- `semantic-operation-log.v1`

Capabilities describe behavior, not a consumer name.

## Application Flow

```text
consumer resolves harness-cli
  -> query contract JSON
  -> compare protocol/capabilities/supported schema and target DB state
  -> read one consistent work-graph snapshot
  -> create isolated DB snapshot when a worktree needs one
  -> perform compare-and-set typed writes through CLI
  -> receive JSON mutation/apply result
```

## Interface Contract

Candidate additive command surface:

```text
harness-cli query contract --json
harness-cli query work-graph --json
harness-cli query stories --json
harness-cli query dependencies --json [--story <id>]
harness-cli query hierarchy --json [--story <id>]
harness-cli story add --id <id> --title <title> --lane <lane> --json
harness-cli story update --id <id> --status <status> --expected-status <status> [--require-runnable] --json
harness-cli story complete <id> --json
harness-cli story dependency add --blocker <id> --blocked <id> --json
harness-cli story dependency remove --blocker <id> --blocked <id> --json
harness-cli story hierarchy add --parent <id> --child <id> --json
harness-cli story hierarchy remove --parent <id> --child <id> --json
harness-cli db changeset status <path> --json
harness-cli db changeset apply <path> --json
harness-cli db snapshot --output <path> --json
```

Exact spelling may follow existing parser conventions, but the accepted JSON
schemas and capabilities cannot be replaced with consumer-specific SQL.

All JSON-mode commands use one envelope with `protocol_version`, `operation`,
`request_id`, and either `result` or `error`. Errors include a stable `code`,
safe `message`, `retryable` flag, and bounded structured `details`. Success
exits `0`; validation/compatibility, not-found/conflict, verification, and
internal failures have documented stable non-zero categories. JSON mode writes
exactly one bounded UTF-8 JSON document to stdout and no unrelated prose;
diagnostics go to stderr without secrets. Paths use platform-native arguments;
an unrepresentable JSON path returns `PATH_NOT_UTF8` before mutation. Protocol
docs pin the output ceiling and read/mutation timeout/cancellation rules so a
consumer cannot wait forever or allocate unbounded output. Non-JSON mode
retains current output.

Protocol v1 starts with concrete process limits: 16 MiB combined machine
output, 30 seconds for read-only operations, and 300 seconds for mutations.
The contract documents bounded configuration overrides and process-tree
cancellation on every platform. After a mutation timeout, consumers must query
logical/status state before retrying; they never assume either success or
rollback from the timeout alone.

`query work-graph` opens one SQLite read transaction, orders every collection,
and hashes the canonical graph payload into `revision`. `db snapshot` uses the
SQLite online backup API into a temporary output, integrity-checks it, records
a canonical full-database logical-state SHA-256 (plus the included graph
revision) and snapshot-file SHA-256, and atomically renames it. Tests compare
logical table state rather than volatile WAL/SHM file bytes.

## Data Model

Schema 007 and 008 remain Harness-owned and backward compatible. New hierarchy
operations use foreign keys and reject self-links and cycles. Semantic replay
uses versioned operations and preserves idempotence. If needed, an additive
migration records `content_sha256` with `changeset_applied`; a repeated run ID
is skipped only when its content hash matches. Apply parses and validates
`changeset.header.version` and `base_schema_version` before opening the write
transaction.

Contract discovery is dispatched before normal auto-init/migration. It may read
the target header/schema state, but reports `missing` or `needs_migration`
without changing files. The explicit init/migrate command remains the only
path that changes those states.

## Installer / Release Contract

Both installers accept an explicit upgrade operation (for example
`--upgrade-cli --ref <immutable-tag>` / `-UpgradeCli -Ref <immutable-tag>`) that verifies the platform artifact and
checksum before an atomic binary replacement. Existing `--merge` semantics
stay non-destructive. CI proves template files and the downloaded binary came
from the same tag, then runs `query contract`, `query work-graph`, and
`db snapshot` using the native artifact.

The normative shapes and process behavior are in
`docs/contracts/harness-orchestration-v1.md`; this design packet explains why
the contract exists and does not duplicate it as a second authority.

## UI / Platform Impact

No Harness UI. JSON is UTF-8 and path values do not assume `/` or a missing
`.exe` suffix.

## Observability

Mutations emit the same traceable semantic changeset operations as other
Harness writes. Contract checks are read-only and write no trace or changeset.

## Alternatives Considered

1. Document raw SQLite tables as the public API. Rejected because mutations,
   migrations, and human-output parsing would remain brittle across releases.
2. Add a Symphony-specific board command. Rejected because Harness must stay
   consumer-neutral.
3. Share a Rust crate by path or Git dependency. Rejected because it recreates
   source/release coupling.
