# Phase 4 Control-Plane Freeze

Date: 2026-07-21

## Status

Complete

## Outcome

Freeze new upstream reliance on the SQLite lifecycle while preserving existing
state as readable compatibility history and keeping protocol-v1 orchestration
operational behind an explicit compatibility boundary.

Completion requires more than the first warning slice: inventory every real
write consumer, prove that current authority is repository-native, require
explicit intent for source-default human lifecycle writes, reject accidental
writes before a transaction, and retain tested reads, replay, recovery, and
orchestration.

## Context

- `docs/WORKFLOW.md` makes repository product, design, plan, decision, code,
  test, and runtime evidence authoritative for ordinary work.
- Decision `0019` removed database lifecycle writes from the default workflow.
- Decision `0020` moved the complete CLI and SQLite surface behind explicit
  compatibility installation.
- Decision `0021` requires application-legibility evidence rather than Harness
  compliance records.
- `docs/contracts/harness-orchestration-v1.md` remains a published compatibility
  contract used by external orchestration.
- The ignored upstream database remains readable and currently contains three
  nonterminal legacy stories, five open legacy backlog items, 133 intakes, 178
  traces, 16 interventions, and decision rows that predate or sit outside the
  current Git-native decision index.

## Scope

In scope for the full phase:

- Replace the superseded root Phase 4 roadmap with the current freeze boundary
  and preserve the old roadmap as compatibility history.
- Record a lasting decision that separates current Git authority, readable
  legacy state, legacy lifecycle writes, and protocol-required orchestration.
- Classify public CLI behavior into read/maintenance, legacy lifecycle writes,
  and protocol orchestration writes.
- Inventory active-looking SQLite rows and every repository/CI/protocol write
  consumer, with an explicit authority or compatibility disposition.
- Require `--compatibility-write` for a human-oriented legacy lifecycle write
  against the upstream default database and reject the accidental form before
  mutation.
- Keep machine JSON operations, installed consumer behavior, schemas, stored
  rows, command paths, and protocol capabilities unchanged.
- Add native-artifact proof for rejection, explicit maintenance, machine JSON,
  isolated databases, installed consumers, reads, and migrations.

Out of scope:

- Mutating, exporting, retiring, or deleting historical SQLite rows.
- Removing schema migrations or the tracked reproducible-state mechanism.
- Changing protocol-v1 JSON, exit codes, capabilities, or orchestration
  semantics.
- Deciding Symphony's long-term migration on its behalf.
- Completing Phase 3's still-open application runtime/interface evidence loop.

## Approach

1. Preserve the old `PHASE4.md` under `docs/compatibility/` and publish the new
   Phase 4 evidence matrix at the root.
2. Add decision `0022` with a staged `warn -> inventory -> require explicit
   compatibility intent -> freeze accidental writes` runway.
3. Treat rows that are absent from current Git indexes as compatibility
   history, not active authority; do not rewrite them to manufacture closure.
4. In the Rust interface, identify human-oriented lifecycle mutations without
   changing the command parser or repository implementation.
5. Inspect active-looking rows and all CLI callers. Export only genuinely
   current authority; classify historical rows without rewriting their status.
6. Reject an unflagged human lifecycle write only when it targets this source
   repository's default `harness.db`. Permit it with `--compatibility-write`.
7. Keep JSON machine operations, isolated databases, installed consumers,
   queries, initialization/migration, replay, snapshot, and database maintenance
   unchanged.
8. Prove the boundary in unit and native-artifact tests, then prove the public
   command, protocol, reconstruction, recovery, installer, and release
   contracts remain unchanged.
9. Retain the implementation because inventory confirms supported consumers.
   Deletion requires a future versioned decision and migration window.

## Risks And Recovery

- **Machine consumer breakage:** bypass the source-human freeze for machine JSON
  operations and retain every protocol shape. Recovery is to remove the
  interface guard; no durable state migration is involved.
- **False current-work interpretation:** document the exact nonterminal legacy
  rows and state that no database status rewrite is needed to supersede their
  authority.
- **False rejection:** scope enforcement to upstream default-database human
  lifecycle mutations. Explicit compatibility consumers, protocol JSON, and
  isolated fixtures remain unchanged.
- **Premature deletion:** make every phase change additive or documentary;
  preserve the database, snapshot, changesets, schemas, and command paths.
- **Phase-number collision:** archive the old mechanical-verification Phase 4
  verbatim and link it only from compatibility discovery.

Recovery is a normal Git revert of the interface guard and documentation. The
phase changes no schema or historical row, so rollback needs no data migration.

## Progress

- [x] Read the repository-centered workflow and completed reduction decisions.
- [x] Inventory current nonterminal SQLite state without mutation.
- [x] Publish decision 0022 and the current Phase 4 definition.
- [x] Preserve and index the superseded Phase 4 roadmap.
- [x] Implement and test the non-breaking source warning boundary.
- [x] Run focused documentation, Rust, command-contract, and repository proof.
- [x] Record the first-slice result and identify the next compatibility gate.
- [x] Inventory current-looking SQLite rows and classify their authority.
- [x] Inventory source, CI, fixture, installed-consumer, and protocol writes.
- [x] Prove that no current upstream authority needs export from SQLite.
- [x] Require explicit compatibility intent for source-default human writes.
- [x] Reject accidental lifecycle writes before mutation.
- [x] Preserve protocol JSON, explicit databases, consumers, reads, and
  maintenance in a native-artifact test.
- [x] Run the complete focused and repository-wide validation suite.
- [x] Record final evidence, move this plan to completed, and close Phase 4.

## Decisions

- 2026-07-21: Begin with a warning runway, not write rejection. Decisions 0019
  and 0020 removed the lifecycle from the default path, but protocol-v1 remains
  a published mutation contract.
- 2026-07-21: Do not close or migrate old stories/backlog items merely to make
  the database resemble current Git. Their statuses are historical facts; the
  authority boundary is the migration.
- 2026-07-21: Scope the first warning to the upstream default database. An
  installed consumer that explicitly selected the CLI profile already supplied
  compatibility intent.
- 2026-07-21: The direct inventory found no current authority present only in
  SQLite. Planned E10 stories, proposed backlog rows, and Phase 0 decision rows
  remain history; no status rewrite or export is warranted.
- 2026-07-21: Freeze accidental writes with global `--compatibility-write`
  rather than an environment variable. Intent is visible in command history and
  help, while protocol-v1 JSON remains byte-shape compatible.
- 2026-07-21: Retain schemas and implementation. Protocol-v1, explicit CLI
  consumers, reconstruction, and recovery are observed users, so deletion is
  not a safe Phase 4 outcome.

## Validation

- Focused proof: `cargo test -p harness-cli phase4_ -- --nocapture` passed 2
  tests; `tests/boundary/test-phase4-control-plane-freeze.sh` proved rejection
  before mutation, explicit compatibility maintenance, protocol JSON, explicit
  databases, installed consumers, reads, and migration; documentation contracts
  passed.
- Compatibility proof: `tests/core/assert-command-contract.sh` preserved all 50
  public command paths; the protocol native-artifact smoke and fresh-consumer
  changeset tracking passed.
- Repository workflow proof: `tests/evals/test-repository-workflow.sh` passed
  with zero Harness commands in representative ordinary work; task-authority,
  installer, worktree recovery, snapshot, CI, and release recovery checks
  passed.
- Rust proof: all 99 workspace tests passed and Clippy passed with warnings
  denied.
- Tracked-state proof: core snapshot verification passed, and materialized
  parity passed against a fresh replay of tracked state.
- Repository-wide proof: `scripts/validate-premerge.sh` passed end to end using
  a fresh tracked-state materialization as `HARNESS_SOURCE_DB`, including the
  Phase 4 boundary test, 99 Rust tests, Clippy with warnings denied, revision
  coherence, ownership, bootstrap, replay, snapshot, worktree recovery,
  protocol, installers, repository workflow, task authority, and release
  recovery.
- Local-state caveat: the ignored upstream `harness.db` has 133 intakes while
  tracked replay has 134, including intake 224. The local database was not
  mutated. Fresh tracked materialization passed durable-table parity, proving
  the tracked state rather than manufacturing local agreement.

## Result

Complete. New upstream work has one Git-native authority path. Accidental human
lifecycle writes to the source default database fail before mutation; explicit
compatibility maintenance remains possible and visible. Historical state stays
readable and reproducible, and protocol-v1, installed consumers, explicit
databases, reconstruction, and recovery retain their tested behavior.

No implementation was deleted. The consumer inventory proved deletion unsafe
while supported compatibility users remain, satisfying the Phase 4 deletion
boundary through an explicit retention decision.
