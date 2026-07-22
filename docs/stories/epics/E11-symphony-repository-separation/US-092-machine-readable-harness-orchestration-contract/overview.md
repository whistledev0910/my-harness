# Overview

## Current Behavior

Symphony currently opens Harness tables directly, directly retires a root story
through SQL, hardcodes a Unix repository-local CLI path, and parses human
`db changeset apply` output. These behaviors work in one repository but are an
undocumented cross-product contract.

Harness has generic dependency and hierarchy state, yet hierarchy has no full
CLI mutation/query contract. Existing text commands also do not provide a
stable JSON protocol for an external orchestrator.

## Target Behavior

Harness publishes a versioned, additive orchestration protocol. Existing human
CLI output and commands remain compatible. External consumers can inspect CLI
and database compatibility without implicitly creating/migrating a database,
read one transactionally consistent work graph, create WAL-safe isolated
snapshots, mutate story and hierarchy state through compare-and-set/logged CLI
operations, and apply a validated changeset with a JSON result.

## Affected Users

- Harness CLI users, whose existing commands must not regress.
- External orchestrators, initially Symphony.
- Windows users who need a protocol independent of Unix path spelling.

## Affected Product Docs

- `docs/TOOL_REGISTRY.md`
- `scripts/README.md`
- New versioned Harness orchestration contract documentation.
- `docs/contracts/harness-orchestration-v1.md`
- `scripts/schema/007-story-dependencies.sql`
- `scripts/schema/008-story-hierarchy.sql`

## Acceptance Criteria

- A read-only JSON contract query reports protocol version, CLI version,
  supported schema minimum/maximum, required environment variables, named
  capabilities, and target database state: `missing`, `current`,
  `needs_migration`, or `unsupported`. Discovery never creates, migrates, or
  writes the target DB.
- JSON story output exposes stable fields needed by work selection without
  leaking terminal table formatting.
- A `query work-graph --json` capability returns stories, dependency edges, and
  hierarchy edges from one SQLite read transaction with one deterministic
  logical revision/hash. Symphony can select work with one bounded subprocess
  instead of three potentially inconsistent reads.
- Separate dependency and hierarchy queries remain deterministic JSON for
  generic callers.
- `db snapshot --output <path> --json` uses SQLite's backup API to create an
  atomic, self-contained snapshot that includes uncheckpointed WAL commits and
  reports the source logical revision/checksum. It never uses a bare
  `harness.db` file copy or changes logical source state.
- A read-only changeset-status JSON operation reports whether a named
  changeset is already applied; status/doctor flows never need to read
  `changeset_applied` directly or apply a file merely to inspect it.
- Hierarchy add/remove operations are cycle-safe, replayable, idempotent, and
  available through the generic CLI.
- `db changeset apply --json` reports id, applied/skipped status, and operation
  count without requiring prose parsing. Before its transaction starts, apply
  validates the header version and base schema range. Reusing an applied run ID
  with different content fails; status/apply report the parsed run ID and
  content SHA-256.
- Every Harness mutation issued by an orchestrator—story add/status/complete,
  dependency add/remove, hierarchy add/remove, and changeset apply—supports a
  versioned JSON success result, a versioned machine-readable error, and stable
  documented exit semantics. Failed writes are atomic and emit no partial
  semantic operation.
- Story status changes used by an orchestrator go through existing or additive
  CLI operations and create semantic operations when `HARNESS_RUN_ID` is set.
  Status mutation accepts an expected stored status and an optional
  `--require-runnable` precondition in the same transaction. A Ready-only
  retirement therefore conflicts rather than retiring work that changed after
  selection, and JSON returns before/after state.
- JSON `story add` and every advertised mutation are covered; no adapter falls
  back to text merely because the row does not yet exist.
- Protocol docs define one versioned success/error envelope, stable error
  codes/exit categories, UTF-8 and non-UTF-8 path behavior, maximum machine
  output size, consumer process timeouts/cancellation, and atomicity after
  timeout. Machine stdout contains exactly one JSON document.
- Every new JSON shape has a documented version and unknown additive fields are
  allowed for forward compatibility.
- Existing non-JSON CLI output and all current command spellings remain
  unchanged unless a separately documented deprecation is approved.
- All existing 73 Harness CLI tests pass, with new focused contract/replay tests.
- Bash and PowerShell installers provide an explicit, safe CLI-upgrade flag
  that replaces an existing binary only after downloading/verifying the exact
  requested Harness release checksum. Merge mode alone is not treated as an
  upgrade. Template source ref and CLI artifact tag must be the same immutable
  release.
- Installer and release packaging include the contract-compatible CLI and
  required schema migrations.
- Completion produces an immutable Harness CLI release tag newer than
  `harness-cli-v0.1.11`; all supported platform artifacts and SHA-256 files are
  published/retrievable and the exact positive protocol-v1 tag is recorded in
  the contract docs for `US-093` and `US-095`.
- The release matrix runs a native JSON contract/snapshot smoke against every
  published binary, including PowerShell/Windows `.exe`, before publication.
- Installer upgrade regression proves, step by step, that merge keeps the old
  binary, an explicit immutable-ref upgrade installs the verified binary, a bad
  checksum preserves the old binary, and a mutable ref is rejected.

## Non-Goals

- Add Symphony-specific commands or board labels to Harness.
- Move run, worktree, PR, Web, or Electron state into Harness.
- Publish a Rust library shared by source path.
- Remove the SQLite durable layer.
