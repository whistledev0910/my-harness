# Exec Plan

## Goal

Create the smallest stable public Harness protocol that lets an external
orchestrator stop depending on Harness internals.

## Scope

In scope:

- Version/capability discovery.
- Read-only schema-state discovery and one consistent JSON work graph.
- WAL-safe isolated DB snapshot.
- Generic hierarchy mutation and replay.
- Compare-and-set JSON story mutations and validated changeset status/apply.
- Checksum-verified Bash/PowerShell CLI upgrade path.
- Backward compatibility tests and docs.

Out of scope:

- Symphony implementation changes.
- Network service or shared source library.
- Removal of existing text interfaces.

## Risk Classification

Risk flags:

- Public contract.
- Existing behavior.
- Data model.
- Cross-platform.
- Multi-domain.

Hard gates:

- Public API and durable replay compatibility.
- Removing or weakening validation requirements.

## Work Phases

1. Specify protocol v1 envelopes, error/exit/path/size/timeout rules, and
   compatibility behavior.
2. Add non-mutating contract discovery and transactionally consistent
   work-graph JSON.
3. Add SQLite-backup `db snapshot` with logical revision and atomic output.
4. Add generic hierarchy mutation/replay and compare-and-set story writes.
5. Validate changeset headers/content hashes and add JSON mutation/apply/status
   results.
6. Add checksum-verified Bash `--upgrade-cli --ref <tag>` and PowerShell
   `-UpgradeCli -Ref <tag>` replacement, prove ordinary merge remains a skip,
   and run the native smoke.
7. Run old and new CLI behavior side by side and update contract docs/fixtures.
8. Merge through the normal CLI release path, then verify the immutable tag,
   all platform artifacts, checksums, and contract docs.

## Dependencies

- `US-089` baseline accepted.

## Stop Conditions

Pause if the protocol requires consumer names in core, breaks text output,
requires destructive schema migration, silently migrates during discovery,
cannot snapshot uncheckpointed WAL state, or cannot replay logged mutations
into a fresh database. Immediately before
merge/tag/release publication, obtain and
record a fresh owner go/no-go naming the exact candidate SHA, protocol version,
release tag, and expected artifact checksums.

## Rollback

Revert additive commands and schema only before the protocol-v1 Harness CLI
release is published or a Symphony target consumes it. After publication, use
a new protocol version or capability deprecation rather than silent removal.
