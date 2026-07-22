# Phase 4 SQLite Write-Consumer Inventory

Date: 2026-07-21

## Outcome

No current upstream product or execution authority exists only in SQLite. The
source default database can therefore reject accidental human lifecycle writes
without exporting or rewriting historical rows.

Protocol-v1 orchestration, installed CLI-profile consumers, explicitly selected
databases, source reconstruction, and maintenance remain supported compatibility
users. Their retained operations are not evidence that ordinary upstream work
should keep writing lifecycle records.

## How The Boundary Was Audited

The audit used four direct sources:

1. Read-only queries of the ignored upstream `harness.db` for active-looking
   story, backlog, decision, intake, trace, and intervention rows.
2. Comparison with `docs/plans/README.md` and `docs/decisions/README.md`, which
   index current Git-native authority.
3. Repository-wide inspection of CLI invocations in `scripts/`, `tests/`, and
   `.github/workflows/`.
4. The published mutation and capability surface in
   `docs/contracts/harness-orchestration-v1.md`.

## Active-Looking Legacy Rows

| SQLite surface | Exact rows | Disposition |
| --- | --- | --- |
| Planned stories | `US-086`, `US-087`, `US-088` | Preserved E10 proposal history. E10 remains a legacy story packet and is absent from the active-plan index. No export. |
| Retired story | `US-110` | Explicitly retired Phase 0 evaluation work. No export. |
| Proposed backlog | `3`, `4`, `5`, `8`, `20` | Old trace-audit, benchmark, Phase 5, and decision-refresh proposals. None is an indexed active plan. No export. |
| Indexed compatibility decisions | `0005`, `0006`, `0007`, `0011-reproducible-core-state` | Git documents already exist and are indexed as compatibility authority. |
| Other durable decision rows | `0008`, `0009`, `0010`, the Phase 0 `0011`–`0014` rows, and `0018` | Git documents `0008`–`0010` are classified in the decision index. Phase 0 receipt rows and `0018` are historical database evidence, not missing current decisions. |
| Intakes, traces, interventions | 133 intakes, 178 traces, 16 interventions at audit start | Historical execution and review evidence. Current completion comes from Git, executable checks, CI, and runtime evidence. |

The ignored local database is also one tracked intake behind a fresh replay:
tracked state contains intake `224`, while the local materialization does not.
That drift demonstrates why the local database cannot be current roadmap
authority. Phase 4 reports it and leaves the local copy untouched.

## Write Consumers

| Consumer | Required behavior | Phase 4 disposition |
| --- | --- | --- |
| Ordinary upstream work | Git-native plans, decisions, code, tests, CI, and runtime evidence | SQLite lifecycle writes are frozen. |
| Human source maintenance of preserved lifecycle state | Rare, deliberate repair or compatibility verification | Requires global `--compatibility-write`; the command emits a warning and executes normally. |
| Protocol-v1 orchestrator | JSON story add/update/complete, dependency/hierarchy mutation, changeset apply/status, reads, and snapshots | Retained unchanged. Machine envelopes, capabilities, exit codes, and mutation semantics remain protocol v1. |
| Installed `core plus CLI` consumer | Its own explicitly selected local lifecycle and database | Retained unchanged. CLI-profile installation already expresses compatibility intent. |
| Explicit `HARNESS_DB_PATH` workflow | Fixtures, recovery, replay, copied databases, and isolated validation | Retained unchanged. Selecting a database path is explicit compatibility intent. |
| Source reconstruction and maintenance | Init, migrate, changeset apply, rebuild, snapshot, integrity and read queries | Retained unchanged because these preserve readable history and recovery. |
| Repository tests | Temporary source, consumer, worktree, epoch, and protocol fixtures | Retained. A test targeting the source-default write boundary supplies `--compatibility-write`; isolated fixtures need no flag. |
| CI workflows | Compilation, tests, materialization, protocol smoke, installer/release proof | No source-default human lifecycle dependency was found. |

## Enforced Cause And Effect

```text
harness-cli intake ...                 # upstream source default database
  -> exits before opening a write transaction
  -> explains that Git-native plans and decisions are current authority
  -> points to --compatibility-write for deliberate legacy maintenance

harness-cli --compatibility-write intake ...
  -> warns that compatibility was explicitly selected
  -> performs the existing mutation and automatic semantic capture

harness-cli story update ... --json    # protocol v1
  -> no freeze diagnostic
  -> existing JSON envelope, exit code, and transaction semantics

HARNESS_DB_PATH=/tmp/test.db harness-cli intake ...
  -> operates on the explicitly selected compatibility database
```

## Deletion Boundary

Phase 4 does not delete the Rust CLI, schemas, changesets, snapshots, protocol,
or readable database state. Direct inventory proves that protocol-v1 and
explicit CLI-profile consumers still need them. Removal would therefore weaken
a supported compatibility contract rather than reduce unused ceremony.

A future deletion proposal needs new evidence that those consumers migrated or
were retired, an immutable protocol/version decision, a read/export path for
old state, and a rehearsed recovery procedure. Until then, the completed Phase
4 boundary is read-old, maintain-explicitly, and write-new-to-Git.
